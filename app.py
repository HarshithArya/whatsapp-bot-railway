#!/usr/bin/env python3
"""
Optimized WhatsApp Bot with OpenAI Assistant
Single-file implementation with improved performance and error handling
"""

import os
import json
import logging
import time
from typing import Dict, Optional
from datetime import datetime

import httpx
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
class Config:
    """Application configuration"""
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    PHONE_NUMBER_ID = os.getenv('PHONE_NUMBER_ID')
    VERIFY_TOKEN = os.getenv('VERIFY_TOKEN', '12345')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_ASSISTANT_ID = os.getenv('OPENAI_ASSISTANT_ID')
    ASSISTANT_NAME = os.getenv('ASSISTANT_NAME', 'WhatsApp Assistant')
    ASSISTANT_INSTRUCTIONS = os.getenv('ASSISTANT_INSTRUCTIONS', 'You are a helpful assistant.')

# Validate required environment variables
required_vars = ['ACCESS_TOKEN', 'PHONE_NUMBER_ID', 'OPENAI_API_KEY', 'OPENAI_ASSISTANT_ID']
missing_vars = [var for var in required_vars if not getattr(Config, var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {missing_vars}")

# In-memory storage for threads (replace with Redis in production)
threads: Dict[str, str] = {}

# HTTP client with connection pooling
http_client = httpx.Client(
    timeout=30.0,
    limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
)

app = Flask(__name__)

class WhatsAppService:
    """WhatsApp Business API service"""
    
    def __init__(self, access_token: str, phone_number_id: str):
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.base_url = "https://graph.facebook.com/v22.0"
    
    def send_message(self, phone_id: str, message: str) -> bool:
        """Send message via WhatsApp Business API"""
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            data = {
                "messaging_product": "whatsapp",
                "to": phone_id,
                "type": "text",
                "text": {"body": message}
            }
            
            response = http_client.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            logger.info(f"Message sent successfully to {phone_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message: {e}")
            return False

class OpenAIService:
    """OpenAI Assistant API service"""
    
    def __init__(self, api_key: str, assistant_id: str):
        self.api_key = api_key
        self.assistant_id = assistant_id
        self.base_url = "https://api.openai.com/v1"
    
    def get_or_create_thread(self, user_id: str) -> str:
        """Get existing thread or create new one"""
        if user_id in threads:
            return threads[user_id]
        
        try:
            url = f"{self.base_url}/threads"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            response = http_client.post(url, headers=headers)
            response.raise_for_status()
            
            thread_data = response.json()
            thread_id = thread_data["id"]
            threads[user_id] = thread_id
            
            logger.info(f"Created new thread {thread_id} for user {user_id}")
            return thread_id
            
        except Exception as e:
            logger.error(f"Failed to create thread: {e}")
            raise
    
    def add_message_to_thread(self, thread_id: str, message: str) -> bool:
        """Add user message to thread"""
        try:
            url = f"{self.base_url}/threads/{thread_id}/messages"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            data = {"role": "user", "content": message}
            
            response = http_client.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add message to thread: {e}")
            return False
    
    def run_assistant(self, thread_id: str) -> Optional[str]:
        """Run assistant and get response"""
        try:
            # Start run
            run_url = f"{self.base_url}/threads/{thread_id}/runs"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            run_data = {"assistant_id": self.assistant_id}
            
            response = http_client.post(run_url, headers=headers, json=run_data)
            response.raise_for_status()
            
            run_id = response.json()["id"]
            
            # Poll for completion
            max_attempts = 10
            for attempt in range(max_attempts):
                time.sleep(1)
                
                status_url = f"{self.base_url}/threads/{thread_id}/runs/{run_id}"
                status_response = http_client.get(status_url, headers=headers)
                status_response.raise_for_status()
                
                status = status_response.json()["status"]
                
                if status == "completed":
                    # Get messages
                    messages_url = f"{self.base_url}/threads/{thread_id}/messages"
                    messages_response = http_client.get(messages_url, headers=headers)
                    messages_response.raise_for_status()
                    
                    messages = messages_response.json()["data"]
                    if messages:
                        return messages[0]["content"][0]["text"]["value"]
                    break
                    
                elif status in ["failed", "cancelled", "expired"]:
                    logger.error(f"Assistant run failed with status: {status}")
                    break
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to run assistant: {e}")
            return None

# Initialize services
whatsapp_service = WhatsAppService(Config.ACCESS_TOKEN, Config.PHONE_NUMBER_ID)
openai_service = OpenAIService(Config.OPENAI_API_KEY, Config.OPENAI_ASSISTANT_ID)

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """Verify webhook for WhatsApp Business API"""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode == 'subscribe' and token == Config.VERIFY_TOKEN:
        logger.info("WEBHOOK_VERIFIED")
        return challenge
    else:
        return 'Forbidden', 403

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """Handle incoming WhatsApp messages"""
    try:
        data = request.get_json()
        logger.info(f"Received webhook: {data}")
        
        if not data or 'object' not in data or data['object'] != 'whatsapp_business_account':
            return 'OK', 200
        
        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                if change.get('field') == 'messages':
                    value = change.get('value', {})
                    
                    # Handle status updates
                    if 'statuses' in value:
                        logger.info("Received WhatsApp status update")
                        continue
                    
                    # Handle messages
                    for message in value.get('messages', []):
                        process_message(message, value.get('contacts', []))
        
        return 'OK', 200
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return 'OK', 200

def process_message(message: dict, contacts: list):
    """Process incoming WhatsApp message"""
    try:
        phone_id = message.get('from')
        message_text = message.get('text', {}).get('body', '')
        
        if not phone_id:
            logger.error("No phone_id in message")
            return
        
        # Get contact name
        contact_name = "Unknown"
        for contact in contacts:
            if contact.get('wa_id') == phone_id:
                contact_name = contact.get('profile', {}).get('name', 'Unknown')
                break
        
        logger.info(f"Received message from {contact_name} ({phone_id}): {message_text}")
        
        # Get or create thread
        thread_id = openai_service.get_or_create_thread(phone_id)
        
        # Add message to thread
        if not openai_service.add_message_to_thread(thread_id, message_text):
            logger.error("Failed to add message to thread")
            return
        
        # Get AI response
        ai_response = openai_service.run_assistant(thread_id)
        
        if ai_response:
            logger.info(f"AI Response to {contact_name}: {ai_response}")
            
            # Send response via WhatsApp
            success = whatsapp_service.send_message(phone_id, ai_response)
            
            if success:
                logger.info(f"Response sent successfully to {contact_name}")
            else:
                logger.error(f"Failed to send response to {contact_name}")
        else:
            logger.error("No AI response generated")
            
    except Exception as e:
        logger.error(f"Error processing message: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "threads_count": len(threads)
    })

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        "message": "WhatsApp Bot with OpenAI Assistant",
        "status": "running",
        "version": "2.0.0"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)