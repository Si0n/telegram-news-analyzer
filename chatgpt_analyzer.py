import openai

from config import OPENAI_API_KEY, OPENAI_MODEL

# Configure OpenAI client
openai.api_key = OPENAI_API_KEY

IMPORTANT_PROMPT = """
Answer only in Ukrainian.
IMPORTANT: Use only Telegram Markdown V2 formatting in your response. Do not use HTML.
Use emojis to visually separate information blocks.

"""

DEFAULT_PROMPT = """
Your task is to quickly and accurately assess a news or social media post.

{important_prompt}

Instructions:
- Respond only in Ukrainian.
- The format should be short, structured, and mobile-friendly for Telegram.
- Use emojis to visually separate information blocks.
- If there is a link or a source mentioned, describe it (official / fake / propaganda / tabloid / expert / blog / etc.).
- If the source is a repost, try to identify the original.
- Always respond, even if the post is a meme, joke, or emotional bait.
- Pay special attention to topics related to war and panic.

📥 Analyze the following post:
CHANNEL: {channel_name}
POST: {post_text}

📤 Response Format:

📰 Summary: [one short sentence summarizing the post]
📊 Assessment (0–100%):
• Propaganda: XX% – [1 sentence explaining the score]
• Falsehood: XX% – [1 sentence explaining the score]
• Populism: XX% – [1 sentence explaining the score]
• Emotional Manipulation: XX% – [1 sentence explaining the score]
• Toxicity: XX% – [1 sentence explaining the score]
• War Panic: XX% – [1 sentence explaining the score]
• Shitposting/Trolling: XX% – [1 sentence explaining the score]
🔍 Source: [name of source or channel] — [type: official / tabloid / gossip / bot / propaganda / Russian / anonymous / etc.]
📑 Fact-Check:
• [claim 1 from the post]: true / false / unverified [with a brief explanation or fact-check source if needed]
• [claim 2 from the post]: ...
✅ Conclusion: [1–2 sentences with the overall judgment and advice for the reader on what to do with the information]
📎 Warning: [if appropriate — add a warning, e.g., "This channel often spreads panic, disinformation, or unverified content."]
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
                {IMPORTANT_PROMPT}

                Channel: {channel_name}
                Message: {post_text}
                Question: {custom_prompt}
                
                """
                messages.append({"role": "system", "content": "You are a helpful assistant, you will receive a Message, Channel and a Question about the Message, Answer please on the Question(-s)."})
            else:
                # Use default prompt
                prompt = DEFAULT_PROMPT.format(important_prompt=IMPORTANT_PROMPT, post_text=post_text, channel_name=channel_name)
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
                {IMPORTANT_PROMPT}
                
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
                prompt = DEFAULT_PROMPT.format(important_prompt=IMPORTANT_PROMPT, channel_name=channel_name, post_text=post_text) + f"""
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
                {
                    "role": "system",
                    "content": f"You are the smartest person in the world, you answer the questions (short and accurate). \n {IMPORTANT_PROMPT}"
                },
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
