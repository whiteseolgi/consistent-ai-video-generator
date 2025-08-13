from .base import MultiModalLoaderBase
import os
from openai import OpenAI
import base64
import requests
from PIL import Image
from io import BytesIO
from copy import deepcopy
import json

class MultiModalLoaderModelSelector:
    def __init__(self):
        pass

    def call_MultiModalLoader_ai(self, ai_model : str, prompt_text : str = None, prompt_images : list = None):
        if ai_model == "gpt-4.1":
            return MultiModalLoaderModelGPT_4_1(prompt_text=prompt_text, prompt_images=prompt_images)
        else:
            return None
        

class MultiModalLoaderModelGPT_4_1(MultiModalLoaderBase):
    def __init__(self, prompt_text : str = None, prompt_images : list = None):  # prompt_text is multi-modal data
        api_key = os.getenv("OPENAI_API_KEY")
        super.ai_model = OpenAI(api_key=api_key)
        super.prompt_text = prompt_text
        super.prompt_images = prompt_images

    def __load_entity_list(file_path):
        entities = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                # 빈 줄 건너뛰기
                if not line.strip():
                    continue
                # 문자열을 튜플로 안전하게 변환
                try:
                    entity_tuple = eval(line.strip())
                    entities.append(entity_tuple)
                except Exception as e:
                    print(f"라인 파싱 중 오류 발생: {e}")
                    continue
        return entities

    def execute(self):
        
        entity_list = self.__load_entity_list("entity_list.txt")

        input_text = f"""
            다음은 원본 entity_list입니다.
            각 항목은 (type, name, json_attr, image_path) 형식입니다.

            원본 entity_list:
            {json.dumps(entity_list, ensure_ascii=False, indent=2)}

            다음은 multi_modal_data입니다.
            여기에는 이미지 분석 결과, 사물 인식, 날씨, 배경 등의 정보가 포함됩니다.

            multi_modal_data:
            {json.dumps(super.prompt_text, ensure_ascii=False, indent=2)}

            요청사항:
            1. multi_modal_data의 정보를 반영하여 entity_list를 수정하세요.
            2. 기존 entity의 속성을 multi_modal_data 정보로 업데이트하거나 새 속성을 추가하세요.
            3. 결과는 반드시 Python 리스트 형태로, 각 요소는 (type, name, json_attr, image_path) 형식이어야 하며 json_attr는 JSON 문자열로 작성하세요.
            4. 기존 entity_list의 구조와 순서를 기본적으로 유지하되, 필요한 경우 새로운 entity를 추가해도 됩니다.
            5. image_path가 없으면 None으로 둡니다.
        """

        response = super.ai_model.responses.create(
            model="gpt-4.1",
            input=input_text,
            temperature=0.2,
            max_output_tokens=2000
        )

        try:
            updated_entity_list = json.loads(response.output_text)
        except json.JSONDecodeError:
            raise ValueError("모델이 올바른 JSON 리스트 형식으로 반환하지 않았습니다.")

        return updated_entity_list

