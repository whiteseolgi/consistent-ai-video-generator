import json
import re
from typing import List, Dict
from .call_gpt import call_gpt
import logging

logger = logging.getLogger(__name__)


class SceneGenerator:
    def __init__(self):
        pass

    def generate_scenes(self, synopsis: str, *, model: str = "gpt-4.1") -> List[Dict]:
        prompt = f"""
다음 시놉시스를 바탕으로 씬 단위로 나누어 주세요.
각 씬은 다음 형식의 JSON으로 구성해 주세요:
[
  {{
    "scene_id": 1,
    "title": "씬 제목",
    "description": "씬의 구체적인 설명"
  }},
  ...
]

시놉시스:
{synopsis}
        """
        logger.info("씬 생성 프롬프트 전송")
        response = call_gpt(prompt, model=model)

        # JSON 추출 강화: 코드블록 우선, 그 다음 일반 배열
        match = re.search(r"```json\s*(\[.*?\])\s*```", response, re.DOTALL | re.IGNORECASE)
        json_str = match.group(1) if match else None
        if not json_str:
            match = re.search(r"(\[\s*\{[\s\S]*?\}\s*\])", response)
            json_str = match.group(1) if match else None
        if not json_str:
            start = response.find("[")
            end = response.rfind("]")
            if start != -1 and end != -1 and end > start:
                json_str = response[start:end + 1]
        if not json_str:
            logger.error("GPT 응답에 JSON 배열이 없습니다.")
            raise ValueError("GPT 응답에 JSON 배열이 없습니다.")
        try:
            scenes = json.loads(json_str)
            logger.info(f"씬 생성 결과 수신: {len(scenes)}개")
            return scenes
        except json.JSONDecodeError:
            logger.error("GPT 응답에서 추출한 JSON 파싱 실패")
            raise ValueError("GPT 응답에서 추출한 JSON 파싱 실패")
