# WhatsApp Bot with OpenAI Assistant - Railway Deployment

A Python Flask application that integrates WhatsApp Business API with OpenAI Assistant for intelligent customer interactions.

## 🚀 Quick Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/new?template=https://github.com/yourusername/whatsapp-bot-railway)

## Features

- 🤖 **OpenAI Assistant Integration**: Powered by GPT-4 with custom instructions
- 📱 **WhatsApp Business API**: Real-time messaging with customers
- 🔄 **Conversation Threading**: Maintains context across messages
- 🏥 **Health Monitoring**: Built-in health check endpoints
- ☁️ **Cloud Ready**: Optimized for Railway deployment

## Environment Variables

Set these in your Railway project:

```env
# WhatsApp Business API Configuration
ACCESS_TOKEN=your_whatsapp_access_token_here
PHONE_NUMBER_ID=your_phone_number_id_here
VERIFY_TOKEN=12345

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_ASSISTANT_ID=your_assistant_id_here
ASSISTANT_NAME=Mosaic intl
ASSISTANT_INSTRUCTIONS=You are a restaurant owner handling customer queries strictly related to food ordering. Your sole focus is to take, modify, confirm, or answer questions about food orders. Reply in a friendly, concise, and professional tone, focused only on helping the customer order food.
```

## API Endpoints

- `GET /` - Home page with bot info
- `GET /health` - Health check endpoint
- `GET /webhook` - WhatsApp webhook verification
- `POST /webhook` - WhatsApp message processing

## Setup Instructions

1. **Deploy to Railway**: Click the deploy button above or connect your GitHub repo
2. **Configure Environment Variables**: Add all required variables in Railway dashboard
3. **Configure WhatsApp Webhook**: 
   - Go to Meta Developer Console
   - Set webhook URL to: `https://your-app-name.railway.app/webhook`
   - Set verify token to: `12345`
   - Select webhook fields: `messages` and `message_status`
4. **Test**: Send a message to your WhatsApp number

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp env.example .env
# Edit .env with your actual values

# Run locally
python app.py
```

## Testing Deployment

Use the included test script:

```bash
python test_deployment.py
```

Remember to update the `RAILWAY_URL` variable in the script with your actual Railway URL.

## License

MIT License - see LICENSE file for details. 