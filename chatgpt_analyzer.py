import openai

from config import OPENAI_API_KEY, OPENAI_MODEL

# Configure OpenAI client
openai.api_key = OPENAI_API_KEY


class ChatGPTAnalyzer:
    def __init__(self):
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)

    async def analyze_post(self, post_text: str, channel_name: str = "Unknown") -> str:
        """
        Analyze a post using ChatGPT API
        
        Args:
            post_text (str): The text content of the post to analyze
            channel_name (str): Name of the channel where the post was shared
            
        Returns:
            str: Analysis result from ChatGPT
        """
        try:
            # Create a prompt for analysis
            prompt = f"""
            Analyze the following news post for Telegram.

            Your task:
            - Briefly retell the essence (1 sentence)
            - Assess propaganda, lies, shitposting with percentages
            - Identify and characterize the source
            - Check key claims
            - Brief conclusion

            IMPORTANT: Format for Telegram - keep it concise, use emojis, make it readable on mobile.
            The channel where posted ({channel_name}) might NOT be the original source.
            Always respond in Ukrainian!
            Response format (very concise):

            📰 Суть: [1 речення]

            ⚠️ Оцінка:
            • Пропаганда: XX% - [коротко]
            • Брехня: XX% - [коротко]  
            • Шітпостінг: XX% - [коротко]
            • Тупість: XX% - [коротко]

            🔍 Джерело: [назва] - [характеристика]

            ✅ Перевірка: [основні твердження - правда/брехня/не перевірено]

            📊 Висновок: [1-2 речення]

            Channel: {channel_name}
            Content: {post_text}
            """

            # Call ChatGPT API
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system",
                     "content": "You are a helpful assistant that analyzes social media posts and provides insightful commentary."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"Error analyzing post: {str(e)}"

    async def analyze_image_post(self, image_urls: list, caption: str, channel_name: str = "Unknown") -> str:
        """
        Analyze an image post using ChatGPT Vision API (supports multiple images)
        
        Args:
            image_urls (list): List of image URLs to analyze
            caption (str): The caption or description of the images
            channel_name (str): Name of the channel where the post was shared
            
        Returns:
            str: Analysis result from ChatGPT
        """
        try:
            # Create a prompt for image analysis
            prompt = f"""
            Analyze the following news post with images for Telegram.

            Your task:
            - Briefly retell the essence (1 sentence)
            - Assess propaganda, lies, shitposting with percentages
            - Identify and characterize the source
            - Check key claims
            - Brief conclusion

            IMPORTANT: Format for Telegram - keep it concise, use emojis, make it readable on mobile.
            Always respond in Ukrainian!
            Response format (very concise):

            📰 Суть: [1 речення]

            ⚠️ Оцінка:
            • Пропаганда: XX% - [коротко]
            • Брехня: XX% - [коротко]  
            • Шітпостінг: XX% - [коротко]
            • Тупість: XX% - [коротко]

            🔍 Джерело: [назва] - [характеристика]

            ✅ Перевірка: [основні твердження - правда/брехня/не перевірено]

            📊 Висновок: [1-2 речення]

            Channel: {channel_name}
            Caption: {caption or "No text provided"}
            """

            # Build the message content for ChatGPT Vision API
            message_content = [{"type": "text", "text": prompt}]
            for url in image_urls:
                message_content.append({"type": "image_url", "image_url": {"url": url}})

            # Call ChatGPT Vision API
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system",
                     "content": "You are a helpful assistant that analyzes social media posts and provides insightful commentary."},
                    {"role": "user", "content": message_content}
                ],
                max_tokens=500,
                temperature=0.7
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"Error analyzing image post: {str(e)}"
