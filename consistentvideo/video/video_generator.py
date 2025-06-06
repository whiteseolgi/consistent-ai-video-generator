from .base import VideoGeneratorBase
import base64
import time
import requests
from runwayml import RunwayML
from PIL import Image
from io import BytesIO
import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

# 컷 묘사 이미지와 컷 텍스트, 비디오 저장위치 등의 경로에 대해서 수정할 필요가 있음!!!!!
# from moviepy.editor import VideoFileClip, concatenate_videoclips으로 합치는 기능이 있지만 우선 
# subprocess모듈 불러와서 ffmpeg으로 합치는 기능으로 구현했음. ffmpeg이 속도상 더 우위이긴함.

class VideoGenerator(VideoGeneratorBase):

    def __init__(self, cut_image_list=None):
        super().__init__(cut_image_list)    # cut_image_list = ["path1", "path2", ... ]
        self.ai_model = self.__create_client()

        # ------------ 추상클래스에 없는 필드 테스트용으로 만들어서 사용한 부분임 삭제 요망!!!!!!!!!!!!!!!!!!!!
        # self.cut_image_list = cut_image_list
        # ------------ 추상클래스에 없는 필드 테스트용으로 만들어서 사용한 부분임 삭제 요망!!!!!!!!!!!!!!!!!!!!

    def __create_client(self) -> RunwayML:
        api_key = os.getenv("RUNWAY_API_KEY")
        return RunwayML(api_key=api_key)

    # def __load_gpt_api_key(self) -> str:
    #     try:
    #         with open("runway_api_key.txt", "r") as file:
    #             return file.read().strip()
    #     except FileNotFoundError:
    #         raise RuntimeError("api key doesn't exist")

    def execute(self, output_path="./"):
        if not self.cut_image_list:
            raise ValueError("cut_image_list is empty")
        if not self.ai_model:
            raise RuntimeError("There is no model")
        
        os.makedirs(output_path, exist_ok=True)  # 출력 경로 없으면 생성
        results = []

        for image_path in self.cut_image_list:
            base_name = os.path.basename(image_path)
            name_without_ext = os.path.splitext(base_name)[0]
            prompt_path = f"{name_without_ext}.txt"      # cut text path
            try:
                with open(prompt_path, "r", encoding="utf-8") as txt_file:
                    description = txt_file.read().strip()
            except FileNotFoundError:
                raise RuntimeError(f"Cut text '{prompt_path}'does not exist.")
            
            prompt_text = f"{description} Make a video that fits this situation."

            with open(image_path, "rb") as img_file:
                encoded_image = base64.b64encode(img_file.read()).decode("utf-8")
            
            task = self.ai_model.image_to_video.create(
                model='gen4_turbo',
                prompt_image=f"data:image/png;base64,{encoded_image}",
                prompt_text=prompt_text,
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
                    filename = f"{name_without_ext}_video.mp4"
                    full_path = os.path.join(output_path, filename)

                    response = requests.get(video_url)
                    if response.status_code == 200:
                        with open(full_path, "wb") as f:
                            f.write(response.content)
                        results.append(full_path)
                    else:
                        print(f"[{base_name}] Error status code: {response.status_code}")
                else:
                    print(f"[{base_name}] no output url")
            else:
                print(f"[{base_name}] fail to generate video: {task.status}")

        list_path = os.path.join(output_path, "clip_file_list.txt")
        with open(list_path, "w", encoding="utf-8") as f:
            for vf in results:
                f.write(f"file '{vf}'\n")
        
        final_output = os.path.join(output_path, "final_merged_video.mp4")
        subprocess.run([
            "ffmpeg", "-f", "concat", "-safe", "0",
            "-i", list_path, "-c", "copy", final_output
        ])
        self.video = final_output


# -------------- For test ----------------------

# if __name__ == "__main__":
#     image_paths = ["1-1.png", "1-2.png", "1-3.png", "2-1.png", "2-2.png"]
#     generator = VideoGenerator(cut_image_list=image_paths)
#     generator.execute()