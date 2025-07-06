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

### Local Development Installation

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

### Ubuntu Server Installation

#### Prerequisites
- Ubuntu 20.04 LTS or higher
- Python 3.8 or higher
- Git
- Supervisor (for process management)

#### Step-by-Step Installation

1. **Update system packages:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install Python and required packages:**
   ```bash
   sudo apt install -y python3 python3-pip python3-venv git supervisor
   ```

3. **Create a dedicated user for the bot (recommended):**
   ```bash
   sudo adduser dobby
   sudo usermod -aG sudo dobby
   ```

4. **Switch to the dobby user:**
   ```bash
   sudo su - dobby
   ```

5. **Clone the repository:**
   ```bash
   cd /home/dobby
   git clone https://github.com/yourusername/dobby.news.git
   cd dobby.news
   ```

6. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

7. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

8. **Set up environment variables:**
   ```bash
   cp env.example .env
   nano .env
   ```
   
   Edit the `.env` file with your actual API keys:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

9. **Test the bot:**
   ```bash
   python3 telegram_bot.py
   ```
   
   Press `Ctrl+C` to stop the test.

10. **Configure Supervisor for automatic startup:**
    
    Copy the supervisor configuration:
    ```bash
    sudo cp supervisor.conf /etc/supervisor/conf.d/dobby-bot.conf
    ```
    
    Update the supervisor configuration to use the correct paths:
    ```bash
    sudo nano /etc/supervisor/conf.d/dobby-bot.conf
    ```
    
    Update the paths in the file:
    ```ini
    [program:dobby-bot]
    command=/home/dobby/dobby.news/venv/bin/python /home/dobby/dobby.news/telegram_bot.py
    directory=/home/dobby/dobby.news
    user=dobby
    autostart=true
    autorestart=true
    stderr_logfile=/var/log/dobby-bot.err.log
    stdout_logfile=/var/log/dobby-bot.out.log
    environment=PYTHONPATH="/home/dobby/dobby.news"
    redirect_stderr=true
    stdout_logfile_maxbytes=10MB
    stdout_logfile_backups=5
    stderr_logfile_maxbytes=10MB
    stderr_logfile_backups=5
    stopasgroup=true
    killasgroup=true
    ```

11. **Create log files and set permissions:**
    ```bash
    sudo touch /var/log/dobby-bot.err.log /var/log/dobby-bot.out.log
    sudo chown dobby:dobby /var/log/dobby-bot.*.log
    ```

12. **Reload supervisor and start the bot:**
    ```bash
    sudo supervisorctl reread
    sudo supervisorctl update
    sudo supervisorctl start dobby-bot
    ```

13. **Check bot status:**
    ```bash
    sudo supervisorctl status dobby-bot
    ```

14. **View logs (optional):**
    ```bash
    sudo tail -f /var/log/dobby-bot.out.log
    ```

#### Managing the Bot Service

- **Start the bot:** `sudo supervisorctl start dobby-bot`
- **Stop the bot:** `sudo supervisorctl stop dobby-bot`
- **Restart the bot:** `sudo supervisorctl restart dobby-bot`
- **Check status:** `sudo supervisorctl status dobby-bot`
- **View logs:** `sudo tail -f /var/log/dobby-bot.out.log`
- **View error logs:** `sudo tail -f /var/log/dobby-bot.err.log`

#### Firewall Configuration (if needed)

If you're running a firewall, ensure it allows outbound connections:
```bash
sudo ufw allow out 443/tcp  # HTTPS for API calls
sudo ufw allow out 80/tcp   # HTTP for API calls
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