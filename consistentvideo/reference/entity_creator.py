from consistentvideo.reference.base import SynopsisAnalyzerBase, EntityCreatorBase

import os
import re
import base64
from openai import OpenAI


class EntityCreator:
    def __init__(self):
        self.image_dir = "reference_images"  # 기본값, set_base_dir로 재설정됨
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.typename = "generic"  # 서브클래스에서 덮어씀
        self.prompt = None

    def set_base_dir(self, path: str):
        # self.image_dir = os.path.join(path, self.subfolder)
        self.image_dir = os.path.join(path)
        os.makedirs(self.image_dir, exist_ok=True)

    def create(self, type: str, name: str, description: str) -> tuple:
        raise NotImplementedError("create() must be implemented by subclasses")

    def _generate_image(self, prompt: str, name: str, view: str = "front") -> str:
        try:
            response = self.client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                size="1024x1024",
                quality="low",
                n=1
            )

            image_b64 = response.data[0].b64_json
            image_bytes = base64.b64decode(image_b64)

            base_name = re.sub(r"[^\w\-]", "_", name)
            filename = f"{self.typename}+{base_name}_{view}.png"
            counter = 1
            path = os.path.join(self.image_dir, filename)
            while os.path.exists(path):
                filename = f"filename+{counter}.png"
                path = os.path.join(self.image_dir, filename)
                counter += 1

            with open(path, "wb") as f:
                f.write(image_bytes)

            return filename

        except Exception as e:
            print(f"[ERROR] 이미지 생성 실패 ({name}): {e}")
            return None


class CharacterImageCreator(EntityCreator):
    def __init__(self):
        super().__init__()
        self.typename = "characters"

    def create(self, type: str, name: str, description: str) -> tuple:
        prompt = self.prompt if self.prompt is not None else f"""A hyper-realistic front-facing portrait of a person, studio lighting, no background.
        Name: {name}, Description: {description}.
        Photographic realism. No illustration or cartoon style. Do not include any background."""
        image = self._generate_image(prompt, name, view="front")
        return (type, name, description, image)


class LocationImageCreator(EntityCreator):
    def __init__(self):
        super().__init__()
        self.typename = "locations"

    def create(self, type: str, name: str, description: str) -> tuple:
        prompt = self.prompt if self.prompt is not None else f"""A realistic photo of a location, wide-angle shot, natural lighting, no people.
        Location: {name}, Features: {description}.
        Cinematic realism, urban or natural environment as appropriate. Do not include any people."""
        image = self._generate_image(prompt, name, view="front")
        return (type, name, description, image)


class ObjectImageCreator(EntityCreator):
    def __init__(self):
        super().__init__()
        self.typename = "objects"

    def create(self, type: str, name: str, description: str) -> tuple:
        prompt = self.prompt if self.prompt is not None else f"""A high-resolution photograph of a real-world object, no background.
        Object: {name}, Features: {description}.
        Do not include any characters or scenes. No illustration, realistic lighting and texture."""
        image = self._generate_image(prompt, name, view="front")
        return (type, name, description, image)
