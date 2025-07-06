# Telegram Post Analyzer Bot

A Python Telegram bot that analyzes posts shared from channels using ChatGPT API. The bot provides comprehensive analysis including sentiment analysis, factual accuracy assessment, bias detection, and key takeaways.

## Features

- 🤖 **AI-Powered Analysis**: Uses ChatGPT to analyze posts with deep insights
- 📱 **Telegram Integration**: Works seamlessly with Telegram's forwarding feature
- 📊 **Comprehensive Analysis**: Provides sentiment, accuracy, bias, and quality assessment
- 🖼️ **Image Analysis**: Uses ChatGPT Vision API for full visual content analysis
- 📝 **Text Analysis**: Analyzes text content from any media type
- 🔄 **Real-time Processing**: Instant analysis with progress indicators

## Prerequisites

- Python 3.8 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- OpenAI API Key (from [OpenAI Platform](https://platform.openai.com/))

## Installation

1. **Clone or download the project files**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   
   Create a `.env` file in the project root with your API keys:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Setup Instructions

### 1. Create a Telegram Bot

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token provided

### 2. Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (keep it secure!)

### 3. Configure Environment

1. Copy `env.example` to `.env`
2. Replace the placeholder values with your actual API keys:
   ```env
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   OPENAI_API_KEY=sk-1234567890abcdefghijklmnopqrstuvwxyz
   ```

## Usage

### Running the Bot

```bash
python telegram_bot.py
```

The bot will start and display "Bot is running. Press Ctrl+C to stop."

### How to Use

1. **Start the bot**: Send `/start` to your bot
2. **Forward posts**: Forward any message from a channel to your bot
3. **Direct analysis**: Send text directly to the bot for analysis
4. **Get help**: Send `/help` for usage instructions

### Supported Content Types

- ✅ **Text messages** - Full analysis
- ✅ **Images** (with or without captions) - Full visual analysis using ChatGPT Vision API
- ✅ **Other media with text captions** - Text-only analysis
- ❌ **Other media without text** - Not supported

## Bot Commands

- `/start` - Welcome message and basic instructions
- `/help` - Detailed help and usage guide

## Analysis Features

The bot provides comprehensive analysis including:

1. **Main Topic & Key Points** - Identifies the primary subject and important information
2. **Sentiment Analysis** - Evaluates the emotional tone of the content
3. **Factual Accuracy** - Assesses the reliability of claims (when applicable)
4. **Bias Detection** - Identifies potential biases or perspectives
5. **Quality Assessment** - Evaluates overall credibility and presentation
6. **Key Takeaways** - Summarizes the most important insights

## Project Structure

```
├── telegram_bot.py      # Main bot application
├── chatgpt_analyzer.py  # ChatGPT API integration
├── config.py           # Configuration and environment setup
├── requirements.txt    # Python dependencies
├── env.example        # Example environment file
├── .env              # Your actual environment file (create this)
└── README.md         # This file
```

## Error Handling

The bot includes comprehensive error handling for:
- Missing API keys
- Network connectivity issues
- Invalid content types
- API rate limits
- General exceptions

## Security Notes

- Never commit your `.env` file to version control
- Keep your API keys secure and private
- The bot only processes messages sent directly to it
- Respect privacy and copyright when analyzing content

## Troubleshooting

### Common Issues

1. **"TELEGRAM_BOT_TOKEN not found"**
   - Check that your `.env` file exists and contains the correct token

2. **"OPENAI_API_KEY not found"**
   - Verify your OpenAI API key is correctly set in `.env`

3. **Bot not responding**
   - Ensure the bot is running (`python telegram_bot.py`)
   - Check that you've started a conversation with the bot (`/start`)

4. **Analysis fails**
   - Verify your OpenAI API key has sufficient credits
   - Check internet connectivity

### Getting Help

If you encounter issues:
1. Check the console output for error messages
2. Verify your API keys are correct
3. Ensure all dependencies are installed
4. Check your internet connection

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the bot! 