from openai import OpenAI
import base64
from PIL import Image
from io import BytesIO
from base import CutImageGeneratorBase
import requests
from dotenv import load_dotenv
import os

load_dotenv()


class CutImageGenerator(CutImageGeneratorBase):
    def __init__(self, entity=None):        # entity = list<image, description>
        super().__init__(entity)
        self.ai_model = self.__create_client()


    def __create_client(self) -> OpenAI:
        api_key = os.getenv("OPENAI_API_KEY")
        return OpenAI(api_key=api_key)

    # def __load_gpt_api_key(self) -> str:
    #     try:
    #         with open("api_key.txt", "r") as file:
    #             return file.read().strip()
    #     except FileNotFoundError:
    #         raise RuntimeError("api key doesn't exist")

    def execute(self):
        if not self.cut:
            raise ValueError("Cut doesn't exist")
        if not self.ai_model:
            raise RuntimeError("Image generating model dosen't exist")

        # Input prompt composing
        prompt_descs = [desc for _, desc in self.entity]
        cut_description = self.cut['description'] if isinstance(self.cut, dict) else str(self.cut)
        prompt = f"{cut_description} ///// {' '.join(prompt_descs)}"
        prompt = prompt + """
                Based on /////, the front part is the story and the back part is the attributes in the story. 
                And make the image describing the story by referring to the attributes needed to describe the story among the character object background attributes.
                """
        image_files = [open(path, "rb") for path, _ in self.entity]
    

        # ---------------dalle3 (can also dalle2)--------------

        # result = self.ai_model.images.generate(
        #     model="dall-e-3",
        #     prompt=prompt,
        #     size="1792x1024"
        # )
        # image_url = result.data[0].url
        # image_bytes = requests.get(image_url).content
        # self.cut_image = Image.open(BytesIO(image_bytes))

        # -----------------------------------------------------
        # 
        # ---------------------gpt-image-1---------------------

        result = self.ai_model.images.edit(
            model="gpt-image-1",
            image=image_files,
            prompt=prompt,
            # quality="low",         # high/medium/low
            size="1024x1024"       # There is no size compatible 16:9, need to adjust by prompt
        )

        for f in image_files:
            f.close()  # closing file descriptor 

        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)
        self.cut_image = Image.open(BytesIO(image_bytes))

        # -----------------------------------------------------
        return self.cut_image
        # --------for test, will be deleted

# -------------- For test ----------------------

# if __name__ == "__main__":

#     filtered_result = [
#     ('시내버스_front.png', '시내버스 : 크기: 대형(길이 약 10m, 40인승), 색깔: 파란색(서울 시내버스 기준, 임의), 형체: 직사각형, 창문이 큼, 카테고리: 교통수단, 태그: 대중교통, 정류장, 종점, 기사, 승객')
#     ]

#     generator = CutImageGenerator(entity=filtered_result)
#     generator.cut = {
#     'cut_id': 1,
#     'description': '버스 정류장에서 버스가 도착하는 장면.',
#     'characters': [],
#     'background': '조용한 아침 거리와 버스 정류장.',
#     'objects': ['버스', '버스 정류장']
#     }

#     img = generator.execute()
#     img.show()
#     img.save("edited_output.png")
