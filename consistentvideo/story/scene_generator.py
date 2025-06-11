import json
import re
from typing import List, Dict
from .call_gpt import call_gpt


class SceneGenerator:
    def __init__(self):
        pass

    def generate_scenes(self, synopsis: str) -> List[Dict]:
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
        response = call_gpt(prompt)

        # JSON 추출
        match = re.search(r'(\[\s*{.*}\s*\])', response, re.DOTALL)
        if match:
            json_str = match.group(1)
            try:
                scenes = json.loads(json_str)
                return scenes
            except json.JSONDecodeError:
                raise ValueError("GPT 응답에서 추출한 JSON 파싱 실패")
        else:
            raise ValueError("GPT 응답에 JSON 부분이 없습니다.")
