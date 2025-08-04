from io import BytesIO
from .base import CutImageGeneratorBase
from .model_selector import *
from dotenv import load_dotenv
import os

load_dotenv()

class CutImageGenerator(CutImageGeneratorBase):
    def __init__(self, scene_num: int, cut: dict, output_path: str, entity_image_path: str,
                 entity: list = None, ai_model: str = 'gpt'):  # cut = dict, entity = list<tuple(type, name, desc, image_path)>
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
        self.scene_num = scene_num
        self.cut = cut
        self.entity_image_path = entity_image_path
        self.output_path = output_path
        self.ai_model = ai_model

    def execute(self):
        if not self.cut:
            raise ValueError("Cut doesn't exist")
        if not self.ai_model:
            raise RuntimeError("Image generating model dosen't exist")
        if not self.entity:
            print("Entity list is empty")  # not error

        # Get cut information
        cut_description = self.cut.get('description', '')
        cut_id = self.cut.get("cut_id", 9999)

        # Get entities that will be used
        prompt_entity_parts = []
        image_paths = []

        if self.entity:
            for e_type, name, attrs, image_filename in self.entity:
                if (
                    (e_type == "character" and name in self.cut.get("character", [])) or
                    (e_type == "object" and name in self.cut.get("object", [])) or
                    (e_type == "location" and name == self.cut.get("location", ""))
                ):
                    desc = f"['{e_type}': '{name}', 'attribute': {attrs}]"
                    prompt_entity_parts.append(desc)
                    print(f"/////desc: {desc}")
                    image_path = os.path.join(self.entity_image_path, image_filename)
                    image_paths.append(image_path)

        # Input prompt composing
        entity_prompt = " ".join(prompt_entity_parts)
        prompt = (
            f"{cut_description} ///// {entity_prompt}\n"
            "Based on /////, the front part is the story and the back part is the attributes in the story. "
            "Make the image describing the story by referring to the attributes needed to describe the story "
            "among the character, object, and background attributes."
        )

        print(f"S{self.scene_num:04d}-C{cut_id:04d}.png")
        print(f"image_paths: {image_paths}")
        
        image_generator_model = CutImageGeneratorModelSelector().call_CutImageGenerator_ai(
            self.ai_model, 
            prompt_text = prompt, 
            prompt_images = image_paths
        )
        cut_image = image_generator_model.execute()

        filename = f"S{self.scene_num:04d}-C{cut_id:04d}.png"
        save_path = os.path.join(self.output_path, filename)
        os.makedirs(self.output_path, exist_ok=True)
        cut_image.save(save_path)

        return save_path

