import openai

from config import OPENAI_API_KEY, OPENAI_MODEL

# Configure OpenAI client
openai.api_key = OPENAI_API_KEY



DEFAULT_PROMPT = """
Твоє завдання — швидко й точно оцінити новинний або соціальний пост.

🔧 Інструкції:
1. Відповідай **тільки українською мовою**.
2. Формат має бути **короткий, структурований, зручний для читання на мобільному в Telegram**.
3. Використовуй емодзі, щоб розділити блоки.
4. Якщо є посилання або згадка про джерело — **охарактеризуй** його (офіційне / фейкове / пропаганда / жовта преса / експерт / блог тощо).
5. Якщо джерело — репост, спробуй визначити **оригінал**.
6. Завжди відповідай, навіть якщо це мем, жарт або емоційний вкид.
7. Особливо звертай увагу на теми війни та паніки.

📥 Аналізуй наступний пост:
<POST>: {post_text} </POST>
<CHANNEL>: {channel_name} </CHANNEL>

📤 Формат відповіді:

📰 **Суть:** [одне коротке речення з резюме]

📊 **Оцінка (0–100%):**
• Пропаганда: XX% – [1 речення]
• Брехня: XX% – [1 речення]
• Емоційна маніпуляція: XX% – [1 речення]
• Токсичність: XX% – [1 речення]
• Воєнна паніка: XX% – [1 речення]
• Шітпостинг/тролінг: XX% – [1 речення]

🔍 **Джерело:** [назва джерела або каналу] — [тип: офіційне / жовта преса / плітки / бот / пропаганда / російське / анонімне / тощо]

📑 **Перевірка фактів:**  
• [твердження 1]: правда / брехня / не перевірено  
• [твердження 2]: ...

✅ **Висновок:** [1–2 речення з загальною оцінкою і порадою читачу]

📎 Якщо доречно — додай попередження, напр.:
⚠️ *Цей канал часто поширює паніку, вкиди або неперевірену інформацію.*
"""


class ChatGPTAnalyzer:
    def __init__(self):
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)

    async def analyze_post(self, post_text: str, channel_name: str = "Unknown", custom_prompt: str = "") -> str:
        """
        Analyze a post using ChatGPT API
        
        Args:
            post_text (str): The text content of the post to analyze
            channel_name (str): Name of the channel where the post was shared
            custom_prompt (str): Custom prompt to use for analysis (optional)
            
        Returns:
            str: Analysis result from ChatGPT
        """
        try:
            messages = []
            # Create a prompt for analysis
            if custom_prompt:
                # Use custom prompt if provided
                prompt = f"""

                Channel: {channel_name}
                Message: {post_text}
                """
                messages.append({"role": "system", "content": custom_prompt})
            else:
                # Use default prompt
                prompt = DEFAULT_PROMPT
                messages.append({"role": "system", "content": 'You are a master of information warfare, an expert in detecting propaganda, manipulation, and fake news.'})
            
            messages.append({"role": "user", "content": prompt})

            # Call ChatGPT API
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"Error analyzing post: {str(e)}"

    async def analyze_image_post(self, image_urls: list, caption: str, channel_name: str = "Unknown", custom_prompt: str = "") -> str:
        """
        Analyze an image post using ChatGPT Vision API (supports multiple images)
        
        Args:
            image_urls (list): List of image URLs to analyze
            caption (str): The caption or description of the images
            channel_name (str): Name of the channel where the post was shared
            custom_prompt (str): Custom prompt to use for analysis (optional)
            
        Returns:
            str: Analysis result from ChatGPT
        """
        try:
            messages = []
            # Create a prompt for image analysis
            if custom_prompt:
                prompt = f"""
                Channel: {channel_name}
                Caption: {caption or "No text provided"}
                """
                messages.append({"role": "system", "content": custom_prompt})
            else:
                # Use default prompt
                prompt = DEFAULT_PROMPT + f"""
                Caption: {caption or "No text provided"}
                """
                messages.append({"role": "system", "content": 'You are a master of information warfare, an expert in detecting propaganda, manipulation, and fake news.'})

            message_content = [{"type": "text", "text": prompt}]
            for url in image_urls:
                message_content.append({"type": "image_url", "image_url": {"url": url}})
            
            messages.append({"role": "user", "content": message_content})

            # Call ChatGPT Vision API
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"Error analyzing image post: {str(e)}"
