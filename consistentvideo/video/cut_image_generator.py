from openai import OpenAI
import base64
import json
from PIL import Image
from io import BytesIO
from base import CutImageGeneratorBase
import requests
from dotenv import load_dotenv
import os

load_dotenv()


class CutImageGenerator(CutImageGeneratorBase):
    def __init__(self, cut:dict, output_path:str, entity_image_path:str, entity:list=None): # cut = dict, entity = list<tuple(type, name, desc, image_path)>
        '''
        ex)
        cut = {'cut_id': 1, 'description': '버스 정류장에서 버스가 도착하는 장면.', 'characters': [], 'background': '조용한 아침 거리와 버스 정류장.', 'objects': ['버스', '버스 정류장']}
        entity = [
        ('character', '미상(할아버지)', '{"연령대": "70~80대", "인종": "동아시아(한국인)", "성별": "남성", "헤어 스타일": "짧은 흰머리", "헤어 컬러": "백발", "신장": "165cm(추정)", "체중": "60kg(추정)", "체형": "마른 체형", "패션 스타일": "평범한 노인 복장(점퍼, 모자 등)", "추가 특징": "귀가 어두움, 고집스러움, 장난기 많음, 반복적으로 벨을 누름, 시치미 뗌"}', '미상_할아버지__front.png'), 
        ('character', '미상(버스기사)', '{"연령대": "40~50대", "인종": "동아시아(한국인)", "성별": "남성", "헤어 스타일": "짧은 머리", "헤어 컬러": "검정 또는 흑갈색", "신장": "175cm(추정)", "체중": "75kg(추정)", "체형": "보통", "패션 스타일": "버스기사 유니폼", "추가 특징": "인내심 많으나 점점 짜증남, 유머러스함, 승객과 직접 대화"}', '미상_버스기사__front.png'), 
        ...
        ]
        '''
        super().__init__(entity)
        self.ai_model = self.__create_client()
        self.cut = cut
        self.entity_image_path = entity_image_path
        self.output_path = output_path


    def __create_client(self) -> OpenAI:
        api_key = os.getenv("OPENAI_API_KEY")
        return OpenAI(api_key=api_key)

    # def __load_gpt_api_key(self) -> str:
    #     try:
    #         with open("api_key.txt", "r") as file:
    #             return file.read().strip()
    #     except FileNotFoundError:
    #         raise RuntimeError("api key doesn't exist")

    def execute(self):
        if not self.cut:
            raise ValueError("Cut doesn't exist")
        if not self.ai_model:
            raise RuntimeError("Image generating model dosen't exist")
        if not self.entity:
            print("Entity list is empty") # not error

        # Get cut information
        cut_description = self.cut.get('description', '')
        cut_id = self.cut.get("cut_id", "unknown")

        # Get entities that will be used
        prompt_entity_parts = []
        image_files = []

        if self.entity:
            for e_type, name, attr_json, image_filename in self.entity:
                try:
                    attrs = json.loads(attr_json)
                except json.JSONDecodeError:
                    attrs = {}
                desc = f"{e_type}: {name}. " + ", ".join([f"{k}: {v}" for k, v in attrs.items()])
                prompt_entity_parts.append(desc)

                image_path = os.path.join(self.entity_image_path, image_filename)
                if not os.path.exists(image_path):
                    raise FileNotFoundError(f"Entity image file not found: {image_path}")
                image_files.append(open(image_path, "rb"))
        
        # Input prompt composing
        entity_prompt = " ".join(prompt_entity_parts)
        prompt = (
        f"{cut_description} ///// {entity_prompt}\n"
        "Based on /////, the front part is the story and the back part is the attributes in the story. "
        "Make the image describing the story by referring to the attributes needed to describe the story "
        "among the character, object, and background attributes."
        )
    

        # ---------------dalle3 (can also dalle2)--------------

        # result = self.ai_model.images.generate(
        #     model="dall-e-3",
        #     prompt=prompt,
        #     size="1792x1024"
        # )
        # image_url = result.data[0].url
        # image_bytes = requests.get(image_url).content
        # self.cut_image = Image.open(BytesIO(image_bytes))

        # -----------------------------------------------------
        # 
        # ---------------------gpt-image-1---------------------

        if image_files:
            result = self.ai_model.images.edit(
            model="gpt-image-1",
            image=image_files,
            prompt=prompt,
            # quality="low",         # high/medium/low
            size="1024x1024"       # There is no size compatible 16:9, need to adjust by prompt
            )
        else:
            result = self.ai_model.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            # quality="low",         # high/medium/low
            size="1024x1024"       # There is no size compatible 16:9, need to adjust by prompt
            )        
        # -----------------------------------------------------

        # closing file descriptor 
        for f in image_files:
            f.close()  

        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)
        self.cut_image = Image.open(BytesIO(image_bytes))

        filename = f"{cut_id}_depiction_image.png"
        save_path = os.path.join(self.output_path, filename)
        os.makedirs(self.output_path, exist_ok=True)
        self.cut_image.save(save_path)

        return save_path
        # --------for test, will be deleted -------------------

# -------------- For test ----------------------

# if __name__ == "__main__":

#     filtered_result = [
#     ('시내버스_front.png', '시내버스 : 크기: 대형(길이 약 10m, 40인승), 색깔: 파란색(서울 시내버스 기준, 임의), 형체: 직사각형, 창문이 큼, 카테고리: 교통수단, 태그: 대중교통, 정류장, 종점, 기사, 승객')
#     ]

#     generator = CutImageGenerator(entity=filtered_result)
#     generator.cut = {
#     'cut_id': 1,
#     'description': '버스 정류장에서 버스가 도착하는 장면.',
#     'characters': [],
#     'background': '조용한 아침 거리와 버스 정류장.',
#     'objects': ['버스', '버스 정류장']
#     }

#     img = generator.execute()
#     img.show()
#     img.save("edited_output.png")
