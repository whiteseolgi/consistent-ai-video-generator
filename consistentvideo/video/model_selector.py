from .base import ImageGeneratorBase, VideoGeneratorBase
import os
from openai import OpenAI
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
            return ImageGeneratorModelGPT(prompt_text = prompt_text, prompt_images = prompt_images)
        else:
            return None
        
class ImageGeneratorModelGemini(ImageGeneratorBase):
    '''
    Need to fill this blank with Gemini version model
    '''
    def __init__(self, prompt_text : str = None, prompt_images : list = None):
        pass

    def execute(self):
        pass
    


class ImageGeneratorModelGPT(ImageGeneratorBase):
    def __init__(self, prompt_text : str = None, prompt_images : list = None):
        api_key = os.getenv("OPENAI_API_KEY")
        super.ai_model = OpenAI(api_key=api_key)
        super.prompt_text = prompt_text
        super.prompt_images = prompt_images

    def execute(self):
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
        # 
        # ---------------------gpt-image-1---------------------
        print(f"S{self.scene_num:04d}-C{cut_id:04d}.png")
        print(f"image_files: {image_files}")
        if image_files:
            result = self.ai_model.images.edit(
                model="gpt-image-1",
                image=image_files,
                prompt=prompt,
                quality="low",  # high/medium/low
                size="1536x1024"  # There is no size compatible 16:9, need to adjust by prompt
            )
        else:
            result = self.ai_model.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                quality="low",  # high/medium/low
                size="1536x1024"  # There is no size compatible 16:9, need to adjust by prompt
            )
        # -----------------------------------------------------


# -------------------------------------------------------------------------------------------

class VideoGeneratorModelSelector:
    def __init__(self):
        pass

