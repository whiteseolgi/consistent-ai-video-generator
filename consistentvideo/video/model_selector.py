from .base import ImageGeneratoAIBase, VideoGeneratorAIBase
import os
from openai import OpenAI
import base64
import requests
from PIL import Image
from io import BytesIO

class CutImageGeneratorModelSelector:
    def __init__(self):
        pass

    def call_CutImageGenerator_ai(self, ai_model : str, prompt_text : str = None, prompt_images : list = None):
        if ai_model == "gemini":
            return ImageGeneratorModelGemini(prompt_text = prompt_text, prompt_images = prompt_images)
        elif ai_model == "gpt":
            return ImageGeneratorModelGPT_image_1(prompt_text = prompt_text, prompt_images = prompt_images)
        else:
            return None
        
        
class ImageGeneratorModelGemini(ImageGeneratoAIBase):
    '''
    Need to fill this blank with Gemini version model
    '''
    def __init__(self, prompt_text : str = None, prompt_images : list = None):
        pass

    def execute(self):
        pass
    

class ImageGeneratorModelDalle3(ImageGeneratoAIBase):
    def __init__(self, prompt_text : str = None, prompt_images : list = None):
        api_key = os.getenv("OPENAI_API_KEY")
        super.ai_model = OpenAI(api_key=api_key)
        super.prompt_text = prompt_text
        super.prompt_images = prompt_images

    def execute(self):

        image_files = []
        for prompt_image_path in super.prompt_images:
            if not os.path.exists(prompt_image_path):
                raise FileNotFoundError(f"Entity image file not found: {prompt_image_path}")
            image_files.append(open(prompt_image_path, "rb"))
            # print(f"/////image_path: {prompt_image_path}")

        # ---------------dalle3 (can also dalle2)--------------

        result = super.ai_model.images.generate(
            model="dall-e-3",
            prompt=super.prompt_text,
            size="1792x1024"
        )
        image_url = result.data[0].url
        image_bytes = requests.get(image_url).content
        cut_image = Image.open(BytesIO(image_bytes))

        # -----------------------------------------------------

        return cut_image
    

class ImageGeneratorModelGPT_image_1(ImageGeneratoAIBase):
    def __init__(self, prompt_text : str = None, prompt_images : list = None):
        api_key = os.getenv("OPENAI_API_KEY")
        super.ai_model = OpenAI(api_key=api_key)
        super.prompt_text = prompt_text
        super.prompt_images = prompt_images

    def execute(self):

        image_files = []
        for prompt_image_path in super.prompt_images:
            if not os.path.exists(prompt_image_path):
                raise FileNotFoundError(f"Entity image file not found: {prompt_image_path}")
            image_files.append(open(prompt_image_path, "rb"))
            # print(f"/////image_path: {prompt_image_path}")

        # ---------------------gpt-image-1---------------------
        if image_files:
            result = self.ai_model.images.edit(
                model="gpt-image-1",
                image=image_files,
                prompt=super.prompt_text,
                quality="low",  # high/medium/low
                size="1536x1024"  # There is no size compatible 16:9, need to adjust by prompt
            )
        else:
            result = self.ai_model.images.generate(
                model="gpt-image-1",
                prompt=super.prompt_text,
                quality="low",  # high/medium/low
                size="1536x1024"  # There is no size compatible 16:9, need to adjust by prompt
            )
        
        for f in image_files:
            f.close()

        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)
        cut_image = Image.open(BytesIO(image_bytes))
        # -----------------------------------------------------

        return cut_image

# -------------------------------------------------------------------------------------------


class VideoGeneratorModelSelector:
    def __init__(self):
        pass

