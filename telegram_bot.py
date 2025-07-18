import asyncio
import logging
import re

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from chatgpt_analyzer import ChatGPTAnalyzer
from config import TELEGRAM_BOT_TOKEN, OPENAI_MODEL

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    force=True  # Force reconfiguration
)
logger = logging.getLogger(__name__)

# Also configure the root logger to ensure all logs are visible
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
if not root_logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    root_logger.addHandler(handler)


def escape_markdown_v2(text: str) -> str:
    """
    Escapes Telegram Markdown V2 special characters in text.
    """
    return text
    # escape_chars = r"_*[]()~`>#+-=|{}.!\\"
    # return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)


class TelegramBot:
    def __init__(self):
        self.analyzer = ChatGPTAnalyzer()
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self.media_groups = {}  # Store media groups being processed
        self.bot_id = None  # Will be set at startup
        self.setup_handlers()

    def setup_handlers(self):
        """Setup message handlers for the bot"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        # Message handlers for forwarded messages and channel posts (private chats only)
        self.application.add_handler(MessageHandler(
            filters.FORWARDED & filters.ChatType.PRIVATE,
            self.handle_forwarded_message
        ))
        # Handler for regular messages (for testing, private chats only)
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
            self.handle_text_message
        ))
        # Handler for group and channel mentions
        self.application.add_handler(MessageHandler(
            (filters.ChatType.GROUPS | filters.ChatType.SUPERGROUP) & filters.TEXT & filters.Entity("mention"),
            self.handle_group_mention
        ))
        # Handler for channel mentions (separate from groups)
        self.application.add_handler(MessageHandler(
            filters.ChatType.CHANNEL & filters.TEXT & filters.Entity("mention"),
            self.handle_channel_mention
        ))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🤖 Welcome to the Post Analyzer Bot!

I can analyze posts shared from any channel using AI.

**How to use:**
1. Forward any message from a channel to me
2. I'll analyze the content and provide insights
3. You can also send me text directly for analysis
4. In groups/channels: Mention me (@botname) to analyze replied-to messages
5. Add custom instructions after mentioning me (e.g., "@botname focus on propaganda")

**Supported content:**
• Text messages
• Images (with or without captions)
• Other media with text captions

**Commands:**
/start - Show this welcome message
/help - Show help information

Let's get started! Forward a post from any channel to me.
        """
        await update.message.reply_text(welcome_message)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
📚 **Post Analyzer Bot Help**

**What I do:**
I analyze posts shared from channels using ChatGPT to provide:
• Main topic and key points
• Sentiment analysis
• Factual accuracy assessment
• Bias detection
• Quality and credibility evaluation
• Key takeaways

**How to use:**
1. **Forward a message** from any channel to me
2. **Send text directly** for analysis
3. **In groups/channels:** Mention me (@botname) to analyze replied-to messages
4. **Custom prompts:** Add instructions after mentioning me (e.g., "@botname focus on propaganda detection")
5. Wait for my AI-powered analysis

**Supported content types:**
• ✅ Text messages
• ✅ Images (with or without captions) - full visual analysis
• ✅ Other media with text captions (text only analysis)
• ❌ Other media without text (not supported)

**Custom prompts examples:**
• "@botname analyze this for fake news"
• "@botname check if this is propaganda"
• "@botname focus on bias detection"
• "@botname verify the claims in this post"

**Note:** Make sure you have permission to share the content you're analyzing.
        """
        await update.message.reply_text(help_message)

    async def handle_forwarded_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle forwarded messages from channels"""
        try:
            message = update.message

            # Check if message exists
            if not message:
                return

            # Ignore if forwarded from the bot itself
            if message.forward_from and self.bot_id and message.forward_from.id == self.bot_id:
                return

            # Check if this is part of a media group
            if message.media_group_id:
                # This is part of a media group - store it and wait for more
                if message.media_group_id not in self.media_groups:
                    self.media_groups[message.media_group_id] = {
                        'messages': [],
                        'processed': False,
                        'timer': None
                    }

                self.media_groups[message.media_group_id]['messages'].append(message)

                # Set a timer to process the group after a short delay
                if self.media_groups[message.media_group_id]['timer']:
                    self.media_groups[message.media_group_id]['timer'].cancel()

                self.media_groups[message.media_group_id]['timer'] = asyncio.create_task(
                    self.process_media_group_after_delay(message.media_group_id, context)
                )
                return

            # Regular message (not part of a media group) - process immediately
            await self.process_single_message(message, context)

        except Exception as e:
            logger.error(f"Error handling forwarded message: {e}")
            await update.message.reply_text("❌ Вибачте, сталася помилка при аналізі поста. Спробуйте ще раз.")

    async def process_media_group_after_delay(self, media_group_id: str, context: ContextTypes.DEFAULT_TYPE):
        """Process a media group after a delay to collect all messages"""
        try:
            # Wait 2 seconds for all messages in the group to arrive
            await asyncio.sleep(2)

            if media_group_id in self.media_groups and not self.media_groups[media_group_id]['processed']:
                messages = self.media_groups[media_group_id]['messages']
                if messages:
                    # Process the first message as the representative
                    await self.process_media_group(messages, context)

                # Clean up
                del self.media_groups[media_group_id]

        except Exception as e:
            logger.error(f"Error processing media group: {e}")

    async def process_media_group(self, messages: list, context: ContextTypes.DEFAULT_TYPE):
        """Process a group of media messages"""
        try:
            first_message = messages[0]

            # Get channel information from the first message
            if first_message.forward_from_chat:
                channel_name = first_message.forward_from_chat.title
                channel_username = first_message.forward_from_chat.username
                channel_info = f"@{channel_username}" if channel_username else channel_name
            else:
                channel_info = "Unknown Channel"

            # Send processing message
            processing_msg = await first_message.reply_text("🔍 Аналізую пост... Очікуйте.")

            all_image_urls = []
            all_texts = []
            caption = ""

            for msg in messages:
                if msg.photo:
                    for photo in msg.photo:
                        url = await self.get_image_url(photo.file_id, context)
                        if url:
                            all_image_urls.append(url)
                # Збираємо всі caption/text
                if msg.caption:
                    all_texts.append(msg.caption)
                    if not caption:
                        caption = msg.caption
                elif msg.text:
                    all_texts.append(msg.text)

            post_text = "\n".join(all_texts).strip()

            if all_image_urls:
                analysis = await self.analyzer.analyze_image_post(
                    image_urls=all_image_urls,
                    post_text=post_text,
                    caption=caption,
                    channel_name=channel_info
                )
            else:
                analysis = "❌ Не вдалося отримати зображення для аналізу."

            formatted_answer = self.format_analysis(analysis)
            logger.info("Answer: " + analysis)
            logger.info("Formatted Answer: " + formatted_answer)

            # Delete processing message and send analysis
            await processing_msg.delete()
            try:
                await first_message.reply_text(formatted_answer, parse_mode=ParseMode.MARKDOWN_V2)
            except Exception as e:
                logger.warning(f"HTML parsing failed, sending as plain text: {e}")
                await first_message.reply_text(formatted_answer, parse_mode=None)

            # Mark as processed
            if first_message.media_group_id in self.media_groups:
                self.media_groups[first_message.media_group_id]['processed'] = True

        except Exception as e:
            logger.error(f"Error processing media group: {e}")
            await first_message.reply_text("❌ Вибачте, сталася помилка при аналізі медіа групи. Спробуйте ще раз.")

    def extract_custom_prompt(self, message_text: str, bot_username: str) -> str:
        """Extract custom prompt from a message that mentions the bot"""
        try:
            # Find the bot mention in the message
            mention_pattern = f"@{bot_username.lower()}"
            mention_pattern_upper = f"@{bot_username}"

            # Find the position of the mention
            mention_pos = -1
            if mention_pattern in message_text.lower():
                mention_pos = message_text.lower().find(mention_pattern)
            elif mention_pattern_upper in message_text:
                mention_pos = message_text.find(mention_pattern_upper)

            if mention_pos == -1:
                return ""

            # Extract text after the mention
            after_mention = message_text[mention_pos + len(mention_pattern_upper):].strip()

            # If there's text after the mention, return it as the custom prompt
            if after_mention:
                logger.info(f"Extracted custom prompt: '{after_mention}'")
                return after_mention

            return ""

        except Exception as e:
            logger.error(f"Error extracting custom prompt: {e}")
            return ""

    async def process_single_message(self, message, context: ContextTypes.DEFAULT_TYPE, original_message=None,
                                     custom_prompt: str = ""):
        """Process a single message (not part of a media group)"""
        try:
            # Use original_message for sending replies if provided (for mock messages)
            reply_message = original_message if original_message else message

            # Get channel information
            if message.forward_from_chat:
                channel_name = message.forward_from_chat.title
                channel_username = message.forward_from_chat.username
                channel_info = f"@{channel_username}" if channel_username else channel_name
            else:
                channel_info = "Unknown Channel"

            # Send processing message
            processing_msg = await reply_message.reply_text("🔍 Аналізую пост... Очікуйте.")

            # Analyze based on content type
            if message.text and not message.photo and not message.video and not message.document and not message.audio and not message.voice and not message.video_note:
                # Pure text message
                analysis = await self.analyzer.analyze_post(message.text, channel_info, custom_prompt)
            elif message.photo:
                # Single image post - use ChatGPT Vision API
                image_urls = []
                for photo in message.photo:
                    url = await self.get_image_url(photo.file_id, context)
                    if url:
                        image_urls.append(url)
                if image_urls:
                    analysis = await self.analyzer.analyze_image_post(image_urls=image_urls,
                                                                      post_text=message.text if message.text else "",
                                                                      caption=message.caption if message.caption else "",
                                                                      channel_name=channel_info,
                                                                      custom_prompt=custom_prompt)
                else:
                    analysis = "❌ Не вдалося отримати зображення для аналізу."
            elif message.caption and (
                    message.video or message.document or message.audio or message.voice or message.video_note):
                # Other media types with caption - analyze only the text
                analysis = await self.analyzer.analyze_post(message.caption, channel_info, custom_prompt)
            else:
                # Unsupported media without text
                analysis = "❌ Цей тип медіа не підтримується для аналізу. Надішліть текст або зображення."

            formatted_answer = self.format_analysis(analysis)

            logger.info("Answer: " + analysis)
            logger.info("Formatted Answer: " + formatted_answer)

            # Delete processing message and send analysis
            await processing_msg.delete()
            try:
                await reply_message.reply_text(formatted_answer, parse_mode=ParseMode.MARKDOWN_V2)
            except Exception as e:
                # If HTML parsing fails, send without formatting
                logger.warning(f"HTML parsing failed, sending as plain text: {e}")
                await reply_message.reply_text(formatted_answer, parse_mode=None)

        except Exception as e:
            logger.error(f"Error processing single message: {e}")
            if original_message:
                await original_message.reply_text("❌ Вибачте, сталася помилка при аналізі поста. Спробуйте ще раз.")
            else:
                await message.reply_text("❌ Вибачте, сталася помилка при аналізі поста. Спробуйте ще раз.")

    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages for direct analysis"""
        try:
            message = update.message

            # Check if message exists
            if not message:
                return

            # Send processing message
            processing_msg = await message.reply_text("🔍 Аналізую пост... Очікуйте.")

            # Analyze the text
            analysis = await self.analyzer.analyze_post(message.text, "Direct Message")

            formatted_answer = self.format_analysis(analysis)

            logger.info("Answer: " + analysis)
            logger.info("Formatted Answer: " + formatted_answer)

            # Delete processing message and send analysis
            await processing_msg.delete()
            try:
                await message.reply_text(formatted_answer, parse_mode=ParseMode.MARKDOWN_V2)
            except Exception as e:
                # If HTML parsing fails, send without formatting
                logger.warning(f"Markdown V2 parsing failed, sending as plain text: {e}")
                await message.reply_text(analysis, parse_mode=None)

        except Exception as e:
            logger.error(f"Error handling text message: {e}")
            await message.reply_text("❌ Вибачте, сталася помилка при аналізі тексту. Спробуйте ще раз.")

    async def get_image_url(self, file_id: str, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Get the URL of an image file from Telegram"""
        try:
            file = await context.bot.get_file(file_id)
            return file.file_path
        except Exception as e:
            logger.error(f"Error getting image URL: {e}")
            return ""

    async def get_message_by_id(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int):
        """Fetch a message by its ID from Telegram API"""
        try:
            # Use the bot's API to get the message
            # We'll use a workaround by getting recent messages and finding the one we need
            messages = await context.bot.get_chat_history(chat_id, limit=100)

            # Find the message with the specified ID
            for msg in messages:
                if msg.message_id == message_id:
                    logger.info(f"Found message {message_id} in chat history")
                    return msg

            logger.warning(f"Message {message_id} not found in recent chat history")
            return None

        except Exception as e:
            logger.error(f"Error fetching message by ID: {e}")
            return None

    def format_analysis(self, analysis: str) -> str:
        """Format the analysis for better presentation (HTML version)"""
        return escape_markdown_v2(analysis).strip()

    async def handle_group_mention(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle messages in groups where the bot is mentioned"""
        try:
            message = update.message

            # Check if message exists
            if not message:
                return
            bot_username = (await context.bot.get_me()).username
            # Check if the bot is actually mentioned
            if not any(entity.type == "mention" and message.text[
                                                    entity.offset:entity.offset + entity.length].lower() == f"@{bot_username.lower()}"
                       for entity in message.entities or []):
                return
            # Ignore if replying to the bot's own message
            if message.reply_to_message and self.bot_id and getattr(message.reply_to_message.from_user, 'id',
                                                                    None) == self.bot_id:
                return

            # Extract custom prompt from the mention message
            custom_prompt = self.extract_custom_prompt(message.text, bot_username)
            if custom_prompt:
                logger.info(f"Custom prompt extracted: '{custom_prompt}'")
            else:
                logger.info("No custom prompt found, using default analysis")

            # Prefer to analyze the replied-to message
            if message.reply_to_message:
                logger.info("Reply detected, analyzing replied-to message")
                target_message = message.reply_to_message
            elif message.api_kwargs.get('quote'):
                # Quote detected (group reply)
                quote = message.api_kwargs.get('quote')
                logger.info(f"Quote detected in group: {quote}")

                # Extract the quoted text
                if quote.get('text'):
                    quoted_text = quote['text']
                    logger.info(f"Found quoted text: {quoted_text}")

                    # Create a mock message object with the quoted text
                    class MockMessage:
                        def __init__(self, text, chat_info):
                            self.text = text
                            self.chat = type('Chat', (),
                                             {'title': chat_info['title'], 'username': chat_info.get('username')})()
                            self.forward_from_chat = None
                            self.photo = None
                            self.caption = None
                            self.video = None
                            self.document = None
                            self.audio = None
                            self.voice = None
                            self.video_note = None

                    # Get chat info from the current message
                    chat_info = {'title': message.chat.title, 'username': getattr(message.chat, 'username', None)}
                    target_message = MockMessage(quoted_text, chat_info)
                    logger.info("Created mock message with quoted text")
                else:
                    logger.info("No quoted text found, analyzing current message")
                    target_message = message
            else:
                # No reply or quote: answer as a general assistant
                logger.info("No reply or quote detected, answering as a general assistant")
                answer = await self.analyzer.answer_general_question(message.text)
                formatted_answer = self.format_analysis(answer)

                logger.info("Answer: " + answer)
                logger.info("Formatted Answer: " + formatted_answer)
                await message.reply_text(formatted_answer, parse_mode=ParseMode.MARKDOWN_V2)
                return
            await self.process_single_message(target_message, context, original_message=message,
                                              custom_prompt=custom_prompt)
        except Exception as e:
            logger.error(f"Error handling group mention: {e}")
            await update.message.reply_text("❌ Вибачте, сталася помилка при аналізі згаданого поста. Спробуйте ще раз.")

    async def handle_channel_mention(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle messages in channels where the bot is mentioned"""
        try:
            message = update.message

            # Check if message exists
            if not message:
                logger.info("Channel mention: No message found")
                return

            bot_username = (await context.bot.get_me()).username
            logger.info(f"Channel mention detected. Bot username: @{bot_username}")
            logger.info(f"Message text: {message.text}")
            logger.info(f"Message entities: {message.entities}")

            # Check if the bot is actually mentioned
            if not any(entity.type == "mention" and message.text[
                                                    entity.offset:entity.offset + entity.length].lower() == f"@{bot_username.lower()}"
                       for entity in message.entities or []):
                logger.info("Bot not actually mentioned in channel message")
                return

            # Ignore if replying to the bot's own message
            if message.reply_to_message and self.bot_id and getattr(message.reply_to_message.from_user, 'id',
                                                                    None) == self.bot_id:
                return

            # Extract custom prompt from the mention message
            custom_prompt = self.extract_custom_prompt(message.text, bot_username)
            if custom_prompt:
                logger.info(f"Custom prompt extracted: '{custom_prompt}'")
            else:
                logger.info("No custom prompt found, using default analysis")

            logger.info("Bot mentioned in channel, starting analysis...")
            # In channels, prefer to analyze the replied-to message if it exists
            if message.reply_to_message:
                logger.info("Reply detected, analyzing replied-to message")
                target_message = message.reply_to_message
            elif message.api_kwargs.get('quote'):
                # Quote detected (channel reply)
                quote = message.api_kwargs.get('quote')
                logger.info(f"Quote detected: {quote}")

                # Extract the quoted text
                if quote.get('text'):
                    quoted_text = quote['text']
                    logger.info(f"Found quoted text: {quoted_text}")

                    # Create a mock message object with the quoted text
                    class MockMessage:
                        def __init__(self, text, chat_info):
                            self.text = text
                            self.chat = type('Chat', (),
                                             {'title': chat_info['title'], 'username': chat_info.get('username')})()
                            self.forward_from_chat = None
                            self.photo = None
                            self.caption = None
                            self.video = None
                            self.document = None
                            self.audio = None
                            self.voice = None
                            self.video_note = None

                    # Get chat info from the current message
                    chat_info = {'title': message.chat.title, 'username': getattr(message.chat, 'username', None)}
                    target_message = MockMessage(quoted_text, chat_info)
                    logger.info("Created mock message with quoted text")
                else:
                    logger.info("No quoted text found, analyzing current message")
                    target_message = message
            else:
                # No reply or quote: answer as a general assistant
                logger.info("No reply or quote detected, answering as a general assistant")
                answer = await self.analyzer.answer_general_question(message.text)
                await message.reply_text(answer, parse_mode=ParseMode.MARKDOWN_V2)
                return
            await self.process_single_message(target_message, context, original_message=message,
                                              custom_prompt=custom_prompt)
        except Exception as e:
            logger.error(f"Error handling channel mention: {e}")
            await update.message.reply_text("❌ Вибачте, сталася помилка при аналізі згаданого поста. Спробуйте ще раз.")

    async def run(self):
        """Run the bot"""
        logger.info("=== STARTING TELEGRAM BOT ===")
        logger.info("Bot is initializing...")
        await self.application.initialize()
        # Get bot id
        me = await self.application.bot.get_me()
        self.bot_id = me.id
        await self.application.start()
        await self.application.updater.start_polling()

        logger.info("=== BOT IS RUNNING ===")
        logger.info("Press Ctrl+C to stop.")
        logger.info("Waiting for messages...")

        try:
            # Keep the bot running
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Stopping bot...")
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()


def main():
    """Main function to run the bot"""
    bot = TelegramBot()
    asyncio.run(bot.run())


if __name__ == "__main__":
    main()
