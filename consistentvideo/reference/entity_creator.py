from consistentvideo.reference.base import SynopsisAnalyzerBase, EntityCreatorBase

import os
import re
import base64
from typing import Optional, Tuple, Union, List
from openai import OpenAI
from google import genai
from google.genai import types as genai_types
from io import BytesIO
from mimetypes import guess_type
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class EntityCreator:
    def __init__(self):
        self.image_dir = "reference_images"  # 기본값, set_base_dir로 재설정됨
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.gemini_client = None
        self.typename = "generic"  # 서브클래스에서 덮어씀
        self.prompt = None
        self.image_model = "gpt-image-1"
        self.style = "realistic"
        self.image_quality = "low"
        self.image_size = "1024x1024"
        self.aspect_ratio = "1:1"

        # 화풍 프리셋
        self.STYLE_PRESETS: dict[str, str] = {
            "realistic": "Photographic realism, natural lighting, real-world textures. No illustration or cartoon.",
            "illustration": "High-quality digital illustration, clean lines, soft shading, artstation trending.",
            "anime": "Anime style, cel shading, vibrant colors, detailed character design.",
            "watercolor": "Watercolor painting style, soft edges, bleeding pigments, paper texture.",
            "oil_painting": "Oil painting style, visible brushstrokes, rich colors, canvas texture.",
            "comic": "Western comic style, bold ink lines, halftone shading, dramatic lighting.",
            "storybook": "Children's storybook style, warm palette, whimsical, friendly shapes.",
            "sketch": "Pencil sketch style, line art, cross-hatching, monochrome.",
            "pixel_art": "Pixel art style, 16-bit era, limited palette, crisp pixels.",
            "lowpoly": "Low-poly 3D style, faceted geometry, simple materials, minimal textures.",
        }

    def set_base_dir(self, path: str):
        # self.image_dir = os.path.join(path, self.subfolder)
        self.image_dir = os.path.join(path)
        os.makedirs(self.image_dir, exist_ok=True)

    def set_image_model(self, model_name: str):
        self.image_model = model_name
        # Gemini 모델인 경우 클라이언트 초기화
        if model_name == "gemini-2.5-flash-imag(Nano Banana)":
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                self.gemini_client = genai.Client(api_key=api_key)
            else:
                logger.warning("GEMINI_API_KEY가 설정되지 않았습니다.")

    def set_style(self, style_name: str):
        self.style = style_name if style_name in self.STYLE_PRESETS else "realistic"

    def _apply_style(self, prompt: str) -> str:
        style_desc = self.STYLE_PRESETS.get(self.style, self.STYLE_PRESETS["realistic"])
        return f"{prompt}\nStyle: {style_desc}"

    def set_image_quality(self, quality: str):
        # 예: "low", "medium", "high"
        self.image_quality = quality

    def set_image_size(self, size: str):
        # 예: "1024x1024", "1536x1024", "2048x2048"
        self.image_size = size

    def set_aspect_ratio(self, ratio: str):
        # Gemini용 aspect ratio 설정
        self.aspect_ratio = ratio

    def create(self, type: str, name: str, description: str, reference_image_path: Optional[Union[str, List[str]]] = None) -> tuple:
        raise NotImplementedError("create() must be implemented by subclasses")

    def _generate_image(
        self,
        prompt: str,
        name: str,
        view: str = "front",
        reference_image_path: Optional[Union[str, List[str]]] = None,
    ) -> Optional[str]:
        try:
            if self.image_model == "gemini-2.5-flash-imag(Nano Banana)":
                return self._generate_image_gemini(prompt, name, view, reference_image_path)
            else:
                return self._generate_image_openai(prompt, name, view, reference_image_path)

        except Exception as e:
            logger.error(f"이미지 생성 실패 ({name}): {e}")
            return None

    def _generate_image_openai(
        self,
        prompt: str,
        name: str,
        view: str = "front",
        reference_image_path: Optional[Union[str, List[str]]] = None,
    ) -> Optional[str]:
        # 참조 이미지가 있으면 편집 API 우선 사용, 실패 시 일반 생성으로 폴백
        file_handles: List = []
        paths: List[str] = []
        if isinstance(reference_image_path, str) and reference_image_path:
            paths = [reference_image_path]
        elif isinstance(reference_image_path, list):
            paths = [p for p in reference_image_path if isinstance(p, str) and p]

        try:
            if paths:
                for p in paths:
                    if not os.path.exists(p):
                        logger.warning(f"참조 이미지가 존재하지 않아 스킵합니다: {p}")
                        continue
                    file_handles.append(open(p, "rb"))

            if file_handles:
                response = self.openai_client.images.edit(
                    model=self.image_model,
                    image=file_handles,
                    prompt=prompt,
                    quality=self.image_quality,
                    size=self.image_size,
                    n=1,
                )
            else:
                response = self.openai_client.images.generate(
                    model=self.image_model,
                    prompt=prompt,
                    size=self.image_size,
                    quality=self.image_quality,
                    n=1
                )
        finally:
            for fh in file_handles:
                try:
                    fh.close()
                except Exception:
                    pass

        image_b64 = response.data[0].b64_json
        image_bytes = base64.b64decode(image_b64)

        base_name = re.sub(r"[^\w\-]", "_", name)
        filename = f"{self.typename}+{base_name}_{view}.png"
        counter = 1
        path = os.path.join(self.image_dir, filename)
        while os.path.exists(path):
            filename = f"{self.typename}+{base_name}_{view}_{counter}.png"
            path = os.path.join(self.image_dir, filename)
            counter += 1

        with open(path, "wb") as f:
            f.write(image_bytes)

        return filename

    def _generate_image_gemini(
        self,
        prompt: str,
        name: str,
        view: str = "front",
        reference_image_path: Optional[Union[str, List[str]]] = None,
    ) -> Optional[str]:
        if not self.gemini_client:
            logger.error("Gemini 클라이언트가 초기화되지 않았습니다.")
            return None

        # 참조 이미지가 있는 경우와 없는 경우를 분리 처리
        if reference_image_path:
            # 참조 이미지가 있는 경우: PIL Image 객체 + 텍스트 프롬프트
            contents = []
            
            if isinstance(reference_image_path, str):
                paths = [reference_image_path]
            else:
                paths = [p for p in reference_image_path if isinstance(p, str) and p]
            
            for img_path in paths:
                if not os.path.exists(img_path):
                    logger.warning(f"참조 이미지가 존재하지 않아 스킵합니다: {img_path}")
                    continue
                
                # PIL Image 객체로 직접 로드
                pil_image = Image.open(img_path)
                contents.append(pil_image)
            
            # 텍스트 프롬프트 추가
            contents.append(prompt)
            
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=contents,
                config=genai_types.GenerateContentConfig(
                    image_config=genai_types.ImageConfig(
                        aspect_ratio=self.aspect_ratio,
                    )
                )
            )
        else:
            # 참조 이미지가 없는 경우: 텍스트만
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=[prompt],
                config=genai_types.GenerateContentConfig(
                    image_config=genai_types.ImageConfig(
                        aspect_ratio=self.aspect_ratio,
                    )
                )
            )

        image_parts = [
            part.inline_data.data
            for part in response.candidates[0].content.parts
            if part.inline_data
        ]

        if not image_parts:
            logger.error("Gemini에서 이미지를 생성하지 못했습니다.")
            return None

        image_bytes = image_parts[0]
        image = Image.open(BytesIO(image_bytes))

        base_name = re.sub(r"[^\w\-]", "_", name)
        filename = f"{self.typename}+{base_name}_{view}.png"
        counter = 1
        path = os.path.join(self.image_dir, filename)
        while os.path.exists(path):
            filename = f"{self.typename}+{base_name}_{view}_{counter}.png"
            path = os.path.join(self.image_dir, filename)
            counter += 1

        image.save(path, "PNG")
        return filename


class CharacterImageCreator(EntityCreator):
    def __init__(self):
        super().__init__()
        self.typename = "characters"

    def create(self, type: str, name: str, description: str, reference_image_path: Optional[Union[str, List[str]]] = None) -> tuple:
        base_prompt = self.prompt if self.prompt is not None else f"""A front-facing portrait of a person, studio lighting, no background.
        Name: {name}, Description: {description}.
        Do not include any background."""
        prompt = self._apply_style(base_prompt)
        image = self._generate_image(prompt, name, view="front", reference_image_path=reference_image_path)
        return (type, name, description, image)


class LocationImageCreator(EntityCreator):
    def __init__(self):
        super().__init__()
        self.typename = "locations"

    def create(self, type: str, name: str, description: str, reference_image_path: Optional[Union[str, List[str]]] = None) -> tuple:
        base_prompt = self.prompt if self.prompt is not None else f"""A view of a location, wide-angle shot, no people.
        Location: {name}, Features: {description}.
        Urban or natural environment as appropriate. Do not include any people."""
        prompt = self._apply_style(base_prompt)
        image = self._generate_image(prompt, name, view="front", reference_image_path=reference_image_path)
        return (type, name, description, image)


class ObjectImageCreator(EntityCreator):
    def __init__(self):
        super().__init__()
        self.typename = "objects"

    def create(self, type: str, name: str, description: str, reference_image_path: Optional[Union[str, List[str]]] = None) -> tuple:
        base_prompt = self.prompt if self.prompt is not None else f"""A detailed depiction of a real-world object, no background.
        Object: {name}, Features: {description}.
        Do not include any characters or scenes."""
        prompt = self._apply_style(base_prompt)
        image = self._generate_image(prompt, name, view="front", reference_image_path=reference_image_path)
        return (type, name, description, image)
