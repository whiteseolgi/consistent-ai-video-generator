from io import BytesIO
from .base import CutImageGeneratorBase
from .model_selector import CutImageGeneratorModelSelector
from dotenv import load_dotenv
import os
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class CutImageGenerator(CutImageGeneratorBase):
    def __init__(self, scene_num: int, cut: dict, output_path: str, entity_image_path: str,
                 entity: list = None, ai_model: str = 'gpt-image-1', *, style: str = 'realistic', quality: str = 'low', size: str = '1536x1024'):
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
        self.prompt = None
        self.style = style
        self.quality = quality
        self.size = size
        self.cut_image_type_prompt = ""  # 스타일 프리셋으로 대체

    def execute(self):
        if not self.cut:
            raise ValueError("Cut 정보가 비어있습니다.")
        if not self.ai_model:
            raise ValueError("AI 모델이 선택되지 않았습니다.")
        if not self.entity:
            logger.info("엔티티 목록이 비어있습니다. 참조 이미지 없이 진행합니다.")

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
                    logger.debug(f"Entity prompt part: {desc}")
                    # 이미지 파일이 없거나(None) 경로가 존재하지 않으면 스킵
                    if image_filename:
                        image_path = os.path.join(self.entity_image_path, image_filename)
                        if os.path.exists(image_path):
                            image_paths.append(image_path)
                        else:
                            logger.warning(f"엔티티 이미지가 존재하지 않아 스킵합니다: {image_path}")
                    else:
                        logger.warning(f"엔티티에 이미지 파일명이 없어 스킵합니다: {name}")

        # Input prompt composing
        entity_prompt = " ".join(prompt_entity_parts)
        
        style_presets = {
            'realistic': 'Photographic realism, natural lighting, real-world textures.',
            'illustration': 'High-quality digital illustration, clean lines, soft shading, artstation trending.',
            'anime': 'Anime style, cel shading, vibrant colors, detailed character design.',
            'watercolor': 'Watercolor painting style, soft edges, bleeding pigments, paper texture.',
            'oil_painting': 'Oil painting style, visible brushstrokes, rich colors, canvas texture.',
            'comic': 'Western comic style, bold ink lines, halftone shading, dramatic lighting.',
            'storybook': "Children's storybook style, warm palette, whimsical, friendly shapes.",
            'sketch': 'Pencil sketch style, line art, cross-hatching, monochrome.',
            'pixel_art': 'Pixel art style, 16-bit era, limited palette, crisp pixels.',
            'lowpoly': 'Low-poly 3D style, faceted geometry, simple materials, minimal textures.',
        }
        style_desc = style_presets.get(self.style, style_presets['realistic'])

        self.prompt = (
            f"{cut_description} ///// {entity_prompt}\n"
            "Based on /////, the front part is the story and the back part is the attributes in the story. "
            "Make the image describing the story by referring to the attributes needed to describe the story "
            "among the character, object, and background attributes.\n"
            f"Style: {style_desc}"
        )

        logger.info(f"컷 이미지 생성 시작: S{self.scene_num:04d}-C{cut_id:04d}.png")
        logger.debug(f"참조 이미지 경로: {image_paths}")
        
        image_generator_model = CutImageGeneratorModelSelector().call_CutImageGenerator_ai(
            self.ai_model,
            prompt_text=self.prompt,
            prompt_images=image_paths
        )

        # 모델 파라미터 주입 (gpt-image-1 경로에서만 사용)
        if hasattr(image_generator_model, 'quality'):
            image_generator_model.quality = self.quality
        if hasattr(image_generator_model, 'size'):
            image_generator_model.size = self.size

        if image_generator_model == None:
            raise RuntimeError(f"지원되지 않는 모델입니다: {self.ai_model}")

        try:
            cut_image = image_generator_model.execute()
        except Exception as e:
            logger.error(f"컷 이미지 생성 중 오류: {e}")
            raise

        # Save
        filename = f"S{self.scene_num:04d}-C{cut_id:04d}.png"
        save_path = os.path.join(self.output_path, filename)
        os.makedirs(self.output_path, exist_ok=True)
        cut_image.save(save_path)
        logger.info(f"컷 이미지 저장 완료: {save_path}")

        return save_path

