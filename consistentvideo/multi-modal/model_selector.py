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
            The following is the original entity_list.  
            Each item is in the format (type, name, json_attr, image_path).  

            Original entity_list:  
            {json.dumps(entity_list, ensure_ascii=False, indent=2)}  

            The following is multi_modal_data.  
            It contains information such as image analysis results, object recognition, weather, and background details.  

            multi_modal_data:  
            {json.dumps(super.prompt_text, ensure_ascii=False, indent=2)}  

            Instructions:  
            1. Update the entity_list by incorporating the information from multi_modal_data.  
            2. Update existing entity attributes or add new attributes based on the information in multi_modal_data.  
            3. The result must be in Python list format, where each element is in the form (type, name, json_attr, image_path), and json_attr must be a JSON string.  
            4. Keep the original structure and order of the entity_list as much as possible, but you may add new entities if necessary.  
            5. If image_path is missing, set it to None.  
        """

        response = super.ai_model.responses.create(
            model="gpt-4.1",
            input=input_text,
            temperature=0.2,
        )

        try:
            updated_entity_list = json.loads(response.output_text)
        except json.JSONDecodeError:
            raise ValueError("모델이 올바른 JSON 리스트 형식으로 반환하지 않았습니다.")

        return updated_entity_list

