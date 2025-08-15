from .base import VideoGeneratorBase
from .model_selector import VideoGeneratorModelSelector
import os
import subprocess
from dotenv import load_dotenv
import re

load_dotenv()


# 컷 묘사 이미지와 컷 텍스트, 비디오 저장위치 등의 경로에 대해서 수정할 필요가 있음!!!!!
# from moviepy.editor import VideoFileClip, concatenate_videoclips으로 합치는 기능이 있지만 우선 
# subprocess모듈 불러와서 ffmpeg으로 합치는 기능으로 구현했음. ffmpeg이 속도상 더 우위이긴함.

class VideoGenerator(VideoGeneratorBase):

    def __init__(self, cut_list, output_path="./", cut_image_list=None, ai_model: str = "runway"):
        super().__init__(cut_image_list)  # cut_image_list = ["path1", "path2", ... ]
        self.model_selector = VideoGeneratorModelSelector()
        self.ai_model_name = ai_model
        self.cut_list = cut_list
        self.output_path = output_path

        # ------------ 추상클래스에 없는 필드 테스트용으로 만들어서 사용한 부분임 삭제 요망!!!!!!!!!!!!!!!!!!!!
        self.cut_image_list = cut_image_list
        # ------------ 추상클래스에 없는 필드 테스트용으로 만들어서 사용한 부분임 삭제 요망!!!!!!!!!!!!!!!!!!!!

    # def __load_gpt_api_key(self) -> str:
    #     try:
    #         with open("runway_api_key.txt", "r") as file:
    #             return file.read().strip()
    #     except FileNotFoundError:
    #         raise RuntimeError("api key doesn't exist")

    def execute(self):
        if not self.cut_image_list:
            raise ValueError("cut_image_list is empty")
        if not self.cut_list:
            raise ValueError("cut_list is missing or does not match the number of images")
        if not self.ai_model_name:
            raise RuntimeError("There is no selected model name")

        os.makedirs(self.output_path, exist_ok=True)  # 출력 경로 없으면 생성
        results = []

        for image_path in self.cut_image_list:
            # 파일명에서 S번호와 C번호 추출
            match = re.match(r'S(\d+)-C(\d+)', os.path.basename(image_path))
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

            # 모델 선택 및 실행
            generator_model = self.model_selector.call_VideoGenerator_ai(
                self.ai_model_name,
                prompt_text=prompt_text,
                prompt_image=image_path,
            )
            if generator_model is None:
                raise RuntimeError(f"Unsupported video model: {self.ai_model_name}")

            # 필요한 컨텍스트 주입
            generator_model.cut_list = self.cut_list

            video_bytes = generator_model.execute()
            if video_bytes:
                filename = f"S{scene_num:04d}-C{cut_id:04d}_video.mp4"
                full_path = os.path.join(self.output_path, filename)
                with open(full_path, "wb") as f:
                    f.write(video_bytes)
                results.append(full_path)
            else:
                print(f"[cut_id={cut_id}] fail to generate video")

        # list_path = os.path.join(self.output_path, "clip_file_list.txt")
        # with open(list_path, "w", encoding="utf-8") as f:
        #     for vf in results:
        #         f.write(f"file '{vf}'\n")

        # final_output = os.path.join(self.output_path, "final_merged_video.mp4")
        # subprocess.run([
        #     "ffmpeg", "-f", "concat", "-safe", "0",
        #     "-i", list_path, "-c", "copy", final_output
        # ])
        # self.video = final_output

        # ------------video path output------------
        return True
        # ---------------삭제 가능------------------

# -------------- For test ----------------------

# if __name__ == "__main__":
#     image_paths = ["1-1.png", "1-2.png", "1-3.png", "2-1.png", "2-2.png"]
#     generator = VideoGenerator(cut_image_list=image_paths)
#     generator.execute()
