import openai

from config import OPENAI_API_KEY, OPENAI_MODEL

# Configure OpenAI client
openai.api_key = OPENAI_API_KEY



DEFAULT_PROMPT = """
Твоє завдання — швидко й точно оцінити новинний або соціальний пост.

Інструкції:
1. Відповідай тільки українською мовою.
2. Формат має бути короткий, структурований, зручний для читання на мобільному в Telegram.
3. Використовуй емодзі, щоб розділити блоки інформації.
4. Якщо є посилання або згадка про джерело, охарактеризуй його (офіційне / фейкове / пропаганда / жовта преса / експерт / блог / тощо).
5. Якщо джерело — репост, спробуй визначити оригінал.
6. Завжди відповідай, навіть якщо це мем, жарт або емоційний вкид.
7. Особливо звертай увагу на теми війни та паніки.
8. Дозволені теги: <b>, <strong>, <i>, <em>, <code>, <s>, <strike>, <del>, <u>, <pre language="c++">

📥 Аналізуй наступний пост:
CHANNEL: {channel_name}
POST: {post_text}

📤 Формат відповіді:

📰 Суть: [одне коротке речення з резюме]
---
📊 Оцінка (0–100%):
• Пропаганда: XX% – [1 речення, що пояснює оцінку]
• Брехня: XX% – [1 речення, що пояснює оцінку]
• Популізм: XX% – [1 речення, що пояснює оцінку]
• Емоційна маніпуляція: XX% – [1 речення, що пояснює оцінку]
• Токсичність: XX% – [1 речення, що пояснює оцінку]
• Воєнна паніка: XX% – [1 речення, що пояснює оцінку]
• Шітпостинг/тролінг: XX% – [1 речення, що пояснює оцінку]
---
🔍 Джерело: [назва джерела або каналу] — [тип: офіційне / жовта преса / плітки / бот / пропаганда / російське / анонімне / тощо]
---
📑 Перевірка фактів:
• [твердження 1 з посту]: правда / брехня / не перевірено [та, за необхідності, коротке пояснення або джерело перевірки]
• [твердження 2 з посту]: ...
---
✅ Висновок: [1–2 речення з загальною оцінкою і порадою читачу, що робити з цією інформацією]
---
📎 Попередження: [Якщо доречно — додай попередження, напр.: Цей канал часто поширює паніку, вкиди або неперевірену інформацію.]
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
                Відповідай тільки українською мовою. Використовуй Telegram (HTML) форматування.

                Дозволені теги: <b>, <strong>, <i>, <em>, <code>, <s>, <strike>, <del>, <u>, <pre language="c++">.

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
                Відповідай тільки українською мовою. Використовуй Telegram (HTML) форматування.

                Дозволені теги: <b>, <strong>, <i>, <em>, <code>, <s>, <strike>, <del>, <u>, <pre language="c++">.
                
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

    async def answer_general_question(self, question: str) -> str:
        """
        Answer a general user question as a helpful assistant in Ukrainian (HTML for Telegram).
        """
        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant. Answer the user's question in Ukrainian. Use only simple HTML tags for formatting if needed."},
                {"role": "user", "content": question}
            ]
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Вибачте, сталася помилка: {str(e)}"
