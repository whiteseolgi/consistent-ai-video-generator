import json
import re
from typing import List, Dict
from .call_gpt import call_gpt
import logging

logger = logging.getLogger(__name__)


class CutGenerator:
    def __init__(self):
        pass

    def cut_scene(self, scene: Dict, entity_list: list, story_text: str, *, model: str = "gpt-4.1") -> List[Dict]:
        prompt = f"""
다음 씬 정보를 컷 단위로 나누어 주세요. 각 컷은 반드시 아래 형식으로 출력해주세요. 하나의 씬당 컷은 최대 3~5개 이하로 해주세요. description에는 컷 내용으로 이미지를 생성할 수 있는 프롬프트를 자세하게 영어로 묘사해주세요.
하나의 구성요소는 (type, name, attribute, img_path)가 튜플 형식으로 구성되어 있습니다. character, location, object에는 알맞는 구성요소의 "name" 문자열만 그대로 리스트형태로 들어가야 합니다.
character, location, object에 알맞는 구성요소를 찾을 때 전체 스토리와 씬 정보를 참고하여 매칭해주세요. 구성 요소는 여러개가 매칭될 수도 있고 없을 수도 있습니다.

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

전체 스토리:
```{story_text}```

구성요소:
{entity_list}

씬 정보:
{json.dumps(scene, ensure_ascii=False, indent=2)}
        """
        logger.info("컷 분할 프롬프트 전송")
        response = call_gpt(prompt, model=model)
        try:
            # 코드 블록 안 JSON 추출 또는 본문에서 첫 JSON 배열 추출
            match = re.search(r"```json\s*(\[.*?\])\s*```", response, re.DOTALL | re.IGNORECASE)
            json_str = match.group(1) if match else None
            if not json_str:
                match = re.search(r"(\[\s*\{[\s\S]*?\}\s*\])", response)
                json_str = match.group(1) if match else None
            if not json_str:
                # 백업: 문자열 양 끝 기준으로 배열 경계 추정
                start = response.find("[")
                end = response.rfind("]")
                if start != -1 and end != -1 and end > start:
                    json_str = response[start:end + 1]
            if not json_str:
                raise ValueError("응답에서 JSON 배열을 찾을 수 없습니다.")
            cuts = json.loads(json_str)
            logger.info(f"컷 분할 결과 수신: {len(cuts)}개")
            return cuts
        except json.JSONDecodeError as e:
            logger.error(f"컷 분할 응답 JSON 파싱 실패: {e}")
            raise ValueError(f"컷 분할 응답을 JSON으로 파싱할 수 없습니다: {e}")
