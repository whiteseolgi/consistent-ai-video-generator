from consistentvideo.reference.base import SynopsisAnalyzerBase, EntityCreatorBase


import os
import re
import base64
from openai import OpenAI


class EntityCreator:
    def __init__(self):
        self.image_dir = "reference_images"  # 기본값, set_base_dir로 재설정됨
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.subfolder = "generic"  # 서브클래스에서 덮어씀

    def set_base_dir(self, base_name: str):
        self.image_dir = os.path.join("reference_images", base_name, self.subfolder)
        os.makedirs(self.image_dir, exist_ok=True)

    def create(self, type: str, name: str, description: str) -> tuple:
        raise NotImplementedError("create() must be implemented by subclasses")

    def _generate_image(self, prompt: str, name: str, view: str = "front") -> str:
        try:
            response = self.client.images.generate(
                model="gpt-image-1", prompt=prompt, size="1024x1024", n=1
            )

            image_b64 = response.data[0].b64_json
            image_bytes = base64.b64decode(image_b64)

            base_name = re.sub(r"[^\w\-]", "_", name)
            filename = f"{base_name}_{view}.png"
            counter = 1
            path = os.path.join(self.image_dir, filename)
            while os.path.exists(path):
                filename = f"{base_name}_{view}_{counter}.png"
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
        self.subfolder = "characters"

    def create(self, type: str, name: str, description: str) -> tuple:
        prompt = f"""A studio Ghibli-style character portrait, no background. The character is facing front.
        Name: {name}, Description: {description}.
        Do not include any background."""
        image = self._generate_image(prompt, name, view="front")
        return (type, name, description, image)


class LocationImageCreator(EntityCreator):
    def __init__(self):
        super().__init__()
        self.subfolder = "locations"

    def create(self, type: str, name: str, description: str) -> tuple:
        prompt = f"""A studio Ghibli-style environment illustration, no characters.
        Location: {name}, Features: {description}.
        Do not include any people."""
        image = self._generate_image(prompt, name, view="front")
        return (type, name, description, image)


class ObjectImageCreator(EntityCreator):
    def __init__(self):
        super().__init__()
        self.subfolder = "objects"

    def create(self, type: str, name: str, description: str) -> tuple:
        prompt = f"""A studio Ghibli-style fantasy object, isolated on a plain background.
        Object: {name}, Features: {description}.
        Do not include any characters or scenes."""
        image = self._generate_image(prompt, name, view="front")
        return (type, name, description, image)
