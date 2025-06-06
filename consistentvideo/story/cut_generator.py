import json
from typing import List, Dict
from .call_gpt import call_gpt

class CutGenerator:
    def __init__(self):
        pass

    def cut_scene(self, scene: Dict) -> List[Dict]:
        prompt = f"""
다음 씬 정보를 컷 단위로 나누어 주세요. 각 컷은 아래 형식으로 출력해주세요:
[
  {{
    "cut_id": 1,
    "description": "...",      
    "characters": [...],        
    "background": "...",        
    "objects": [...]            
  }},
  ...
]

씬 정보:
{json.dumps(scene, ensure_ascii=False, indent=2)}
        """
        response = call_gpt(prompt)
        try:
            # 래핑 제거
            cleaned = response.strip().strip("```json").strip("```")
            return json.loads(cleaned)
        except json.JSONDecodeError:
            raise ValueError("컷 분할 응답을 JSON으로 파싱할 수 없습니다.")