import os
import openai
from typing import List
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def call_gpt_ai(prompt_text: str, prompt_image: List[str], ai_model: str) -> str:
    image_prompt_text = ""
    if prompt_image:
        image_prompt_text = "\n\n[Image prompts]:\n" + "\n".join(prompt_image)

    full_prompt = prompt_text + image_prompt_text

    try:
        response = openai.chat.completions.create(
            model=ai_model,
            messages=[
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.7,
            max_tokens=1500,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise RuntimeError(f"OpenAI 호출 중 오류 발생: {e}")