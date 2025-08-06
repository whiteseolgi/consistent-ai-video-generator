from .base import ImageGeneratoAIBase, VideoGeneratorAIBase
import os
from openai import OpenAI
import base64
import requests
from PIL import Image
from io import BytesIO
from runwayml import RunwayML
import time
import re

class CutImageGeneratorModelSelector:
    def __init__(self):
        pass

    def call_CutImageGenerator_ai(self, ai_model : str, prompt_text : str = None, prompt_images : list = None):
        if ai_model == "gemini":
            return ImageGeneratorModelGemini(prompt_text = prompt_text, prompt_images = prompt_images)
        elif ai_model == "gpt-image-1":
            return ImageGeneratorModelGPT_image_1(prompt_text = prompt_text, prompt_images = prompt_images)
        elif ai_model == "dalle3":
            return ImageGeneratorModelDalle3(prompt_text = prompt_text, prompt_images = prompt_images)
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

    def call_VideoGenerator_ai(self, ai_model : str, prompt_text : str = None, prompt_image : str = None):
        if ai_model == "runway":
            return VideoGeneratorModelRunway(prompt_text = prompt_text, prompt_images = prompt_image)
        elif ai_model == "veo3":
            return VideoGeneratorModelVeo3(prompt_text = prompt_text, prompt_images = prompt_image)
        else:
            return None


class VideoGeneratorModelRunway(VideoGeneratorAIBase):
    def __init__(self, prompt_text : str = None, prompt_image : str = None):
        api_key = os.getenv("RUNWAY_API_KEY")
        super.ai_model = RunwayML(api_key=api_key)
        super.prompt_text = prompt_text
        super.prompt_image = prompt_image

    def execute(self):

        # 파일명에서 S번호와 C번호 추출
        match = re.match(r'S(\d+)-C(\d+)', os.path.basename(super.prompt_image))
        if match:
            scene_num = int(match.group(1))  # S번호
            cut_num = int(match.group(2))    # C번호

        print(f"scene_num={scene_num}, cut_num={cut_num}")
        cut = self.cut_list[scene_num-1][cut_num-1]
        cut_id = cut.get('cut_id')
        description = cut.get('description', '')
        base_name = os.path.basename(image_path)
        name_without_ext = os.path.splitext(base_name)[0]

        prompt_text = f"{description} Make a video that fits this situation."

        with open(super.prompt_image, "rb") as img_file:
            encoded_image = base64.b64encode(img_file.read()).decode("utf-8")

        task = self.ai_model.image_to_video.create(
            model='gen4_turbo',
            prompt_image=f"data:image/png;base64,{encoded_image}",
            prompt_text=super.prompt_text,
            ratio='1280:720',
            duration=5,
        )

        task_id = task.id

        time.sleep(10)
        task = self.ai_model.tasks.retrieve(task_id)
        while task.status not in ['SUCCEEDED', 'FAILED']:
            time.sleep(10)
            task = self.ai_model.tasks.retrieve(task_id)

        # Download
        if task.status == 'SUCCEEDED':
            output_urls = task.output
            if output_urls and isinstance(output_urls, list):
                video_url = output_urls[0]
                # filename = f"S{scene_num:04d}-C{cut_id:04d}_video.mp4"
                # full_path = os.path.join(self.output_path, filename)

                response = requests.get(video_url)
                if response.status_code == 200:
                    # with open(full_path, "wb") as f:
                    #     f.write(response.content)
                    # results.append(full_path)
                    return response.content # Binary type video data
                else:
                    print(f"[cut_id={cut_id}] Error status code: {response.status_code}")
            else:
                print(f"[cut_id={cut_id}] no output url")
        else:
            print(f"[cut_id={cut_id}] fail to generate video: {task.status}")

        return None


class VideoGeneratorModelVeo3(VideoGeneratorAIBase):
    '''
    Need to fill this blank with Gemini version model
    '''
    def __init__(self, prompt_text : str = None, prompt_images : list = None):
        pass

    def execute(self):
        pass