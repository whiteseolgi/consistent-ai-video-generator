import json
from typing import List, Dict
from .call_gpt import call_gpt_ai

class CutGenerator:
    def __init__(self):
        self.prompt_text = """
다음 씬 정보를 컷 단위로 나누어 주세요. 각 컷은 반드시 아래 형식으로 출력해주세요. description에는 컷 내용으로 이미지를 생성할 수 있는 프롬프트를 자세하게 영어로 묘사해주세요.
하나의 구성요소는 (type, name, attribute, img_path)가 튜플 형식으로 구성되어 있습니다. character, location, object에는 알맞는 구성요소의 "name" 문자열만 그대로 리스트형태로 들어가야 합니다. 

형식(JSON):
[
  {{
    "cut_id": 1,
    "description": "...",      
    "character": [...],        
    "location": [...],       
    "object": [...]            
  }},
  ...
]

구성요소:
{entity_list}

씬 정보:
{scene}
        """

    def cut_scene(self, scene: Dict, entity_list: List[str]) -> List[Dict]:
        prompt_text = self.prompt_text.format(
            entity_list=entity_list,
            scene = json.dumps(scene, ensure_ascii=False, indent=2)
        )
        response = call_gpt_ai(prompt_text=prompt_text, prompt_image=[], ai_model="gpt-4o")
        try:
            print(f"response:{response}")
            # 래핑 제거
            cleaned = response.strip().strip("```json").strip("```")
            return json.loads(cleaned)
        except json.JSONDecodeError:
            raise ValueError("컷 분할 응답을 JSON으로 파싱할 수 없습니다.")