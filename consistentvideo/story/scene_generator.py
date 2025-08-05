import json
import re
from typing import List, Dict
from .call_gpt import call_gpt_ai


class SceneGenerator:
    def __init__(self):
        self.prompt_text = """
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

    def generate_scenes(self, synopsis: str, prompt_image: List[str] = None, ai_model: str = "gpt-4o") -> List[Dict]:
        """
        prompt_image: 이미지 프롬프트 리스트 (기본값 None)
        ai_model: 사용할 AI 모델 이름 (기본값 "gpt-4o")
        """

        if prompt_image is None:
            prompt_image = []

        prompt_text = self.prompt_text.format(synopsis=synopsis)

        response = call_gpt_ai(prompt_text=prompt_text, prompt_image=prompt_image, ai_model=ai_model)

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
