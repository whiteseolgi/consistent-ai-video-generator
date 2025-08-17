import os
from dotenv import load_dotenv
from openai import OpenAI
import logging

load_dotenv()

_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
logger = logging.getLogger(__name__)


def call_gpt(prompt: str, model: str = "gpt-4.1", temperature: float = 0.7, max_tokens: int = 1500) -> str:
    try:
        logger.debug(f"OpenAI 요청: model={model}, temperature={temperature}, max_tokens={max_tokens}")
        response = _client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        text = response.choices[0].message.content.strip()
        logger.debug("OpenAI 응답 수신 완료")
        return text
    except Exception as e:
        logger.error(f"OpenAI 호출 중 오류 발생 (model={model}): {e}")
        raise RuntimeError(f"OpenAI 호출 중 오류 발생 (model={model}): {e}")
