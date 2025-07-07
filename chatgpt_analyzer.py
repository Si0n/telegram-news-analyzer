import openai

from config import OPENAI_API_KEY, OPENAI_MODEL

# Configure OpenAI client
openai.api_key = OPENAI_API_KEY



DEFAULT_PROMPT = """
Твоє завдання — швидко й точно оцінити новинний або соціальний пост.

Форматування: HTML для Telegram.
Використовуй тільки прості HTML-теги для Telegram: <b>, <i>, <u>, <s>, <a>, <code>, <pre>. Не додавай зайвих пробілів у тегах. Не використовуй вкладені теги. Не вставляй теги всередину емодзі чи посередині слова. Не додавай зайвих тегів. Всі теги мають бути коректно закриті.

🔧 <b>Інструкції:</b>
1. Відповідай <b>тільки українською мовою</b>.
2. Формат має бути <b>короткий, структурований, зручний для читання на мобільному в Telegram</b>.
3. Використовуй емодзі, щоб розділити блоки.
4. Якщо є посилання або згадка про джерело — <i>охарактеризуй</i> його (офіційне / фейкове / пропаганда / жовта преса / експерт / блог тощо).
5. Якщо джерело — репост, спробуй визначити <i>оригінал</i>.
6. Завжди відповідай, навіть якщо це мем, жарт або емоційний вкид.
7. Особливо звертай увагу на теми війни та паніки.

📥 <b>Аналізуй наступний пост:</b>
<b>CHANNEL:</b> {channel_name}
<b>POST:</b> {post_text}

📤 <b>Формат відповіді:</b>

📰 <b>Суть:</b> [одне коротке речення з резюме]

📊 <b>Оцінка (0–100%):</b>
• Пропаганда: XX% – [1 речення]
• Брехня: XX% – [1 речення]
• Популізм: XX% – [1 речення]
• Емоційна маніпуляція: XX% – [1 речення]
• Токсичність: XX% – [1 речення]
• Воєнна паніка: XX% – [1 речення]
• Шітпостинг/тролінг: XX% – [1 речення]

🔍 <b>Джерело:</b> [назва джерела або каналу] — [тип: офіційне / жовта преса / плітки / бот / пропаганда / російське / анонімне / тощо]

📑 <b>Перевірка фактів:</b>
• [твердження 1]: правда / брехня / не перевірено
• [твердження 2]: ...

✅ <b>Висновок:</b> [1–2 речення з загальною оцінкою і порадою читачу]

📎 Якщо доречно — додай попередження, напр.:
⚠️ <i>Цей канал часто поширює паніку, вкиди або неперевірену інформацію.</i>
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
            # Trim custom_prompt and check length
            custom_prompt = custom_prompt.strip()
            # Create a prompt for analysis
            if len(custom_prompt) > 3:
                # Use custom prompt if provided
                prompt = f"""
                Always use format HTML for Telegram.
                Important: You must answer in Ukrainian language only.

                Channel: {channel_name}
                Message: {post_text}
                Question: {custom_prompt}
                
                """
                messages.append({"role": "system", "content": "You are a helpful assistant, you will receive a Message, Channel and a Question about the Message, Answer please on the Question(-s)."})
            else:
                # Use default prompt
                prompt = DEFAULT_PROMPT.format(post_text=post_text, channel_name=channel_name)
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

    async def analyze_image_post(self, image_urls: list, post_text: str, caption: str, channel_name: str = "Unknown", custom_prompt: str = "") -> str:
        """
        Analyze an image post using ChatGPT Vision API (supports multiple images)
        
        Args:
            image_urls (list): List of image URLs to analyze
            post_text (str): The text content of the post to analyze
            caption (str): The caption or description of the images
            channel_name (str): Name of the channel where the post was shared
            custom_prompt (str): Custom prompt to use for analysis (optional)
            
        Returns:
            str: Analysis result from ChatGPT
        """
        try:
            messages = []
            # Trim custom_prompt and check length
            custom_prompt = custom_prompt.strip()
            # Create a prompt for image analysis
            if len(custom_prompt) > 3:
                prompt = f"""
                Always use format HTML for Telegram.
                Important: You must answer in Ukrainian language only.
                
                Channel: {channel_name}
                Post: {post_text}
                Caption: {caption or "No text provided"}
                Question: {custom_prompt}
                """
                messages.append({"role": "system", "content": custom_prompt})
                messages.append({"role": "system",
                                 "content": "You are a helpful assistant, you will receive a Message, Channel and a Question about the Message, Answer please on the Question(-s)."})
            else:
                # Use default prompt
                prompt = DEFAULT_PROMPT.format(channel_name=channel_name, post_text=post_text) + f"""
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
