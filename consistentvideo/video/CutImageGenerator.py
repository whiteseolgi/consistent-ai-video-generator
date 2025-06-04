from openai import OpenAI
import base64
from PIL import Image
from io import BytesIO
from base import CutImageGeneratorBase
import requests


class CutImageGenerator(CutImageGeneratorBase):
    def __init__(self, entity=None):
        super().__init__(entity)
        self.ai_model = self.__create_client()

    def __create_client(self) -> OpenAI:
        api_key = self.__load_gpt_api_key()
        return OpenAI(api_key=api_key)

    def __load_gpt_api_key(self) -> str:
        try:
            with open("api_key.txt", "r") as file:
                return file.read().strip()
        except FileNotFoundError:
            raise RuntimeError("api key doesn't exist")
        
    def execute(self):
        if not self.cut:
            raise ValueError("Cut doesn't exist")
        if not self.ai_model:
            raise RuntimeError("Image generating model dosen't exist")
        
        # Input prompt composing
        prompt = self.cut if not self.entity else f"{self.cut} ///// {self.entity}"
        prompt = prompt + """
                Based on /////, the front part is the story and the back part is the attributes in the story. 
                And make the image describing the story in a 16:9 ratio by referring to the attributes needed to describe the story among the character object background attributes.
                """


        # ---------------dalle3 (can also dalle2)--------------

        result = self.ai_model.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1792x1024"
        )
        image_url = result.data[0].url
        image_bytes = requests.get(image_url).content
        self.cut_image = Image.open(BytesIO(image_bytes))

        # -----------------------------------------------------
        # 
        # ---------------------gpt-image-1---------------------

        # result = self.ai_model.images.generate(
        #     model="gpt-image-1",
        #     prompt=prompt,
        #     # quality="low",         # high/medium/low
        #     size="1024x1024"       # There is no size compatible 16:9, need to adjust by prompt
        # )
        # image_base64 = result.data[0].b64_json
        # image_bytes = base64.b64decode(image_base64)
        # self.cut_image = Image.open(BytesIO(image_bytes))

        # -----------------------------------------------------



# -------------- For test ----------------------

# if __name__ == "__main__":
#     generator = CutImageGenerator()
#     generator.cut = "point-of-view from an elderly man's perspective as he steps into an almost empty city bus, rows of fabric-covered blue seats stretching forward, subtle overhead lighting, daylight pouring in through the side windows, clean floor and metal handrails, overall quiet atmosphere, photorealistic interior shot"
#     generator.entity = """
#         bus_driver : A realistic passport-style photo of a middle-aged Korean man in his late 40s or early 50s. Short black hair, slightly receding hairline, tired eyes, and faint stubble on the chin. Wearing a navy blue work uniform shirt with a subtle badge or patch, like a bus company logo. Neutral-to-frustrated expression. Plain off-white or very light gray background. Realistic lighting, clear focus.
#         elderly_person : A realistic passport-style photo of an elderly Korean man in his late 70s. Balding head with short gray hair on the sides, deep facial wrinkles, thick gray eyebrows, and a slightly smirking expression. Wearing a beige cardigan or windbreaker over a collared shirt. Slight squint in the eyes, suggesting stubbornness or mischief. Plain light blue background. Front-facing, realistic lighting.
#         main_character : A realistic passport-style photo of a young Korean man in his early 20s. Short, tidy black hair, clean-shaven face, even skin tone. Wearing a simple light gray or white crewneck T-shirt. Neutral expression with a hint of a gentle smile, looking calm and observant. Plain light gray background. Front-facing, well-lit, soft shadows."""
    
#     img = generator.execute()
#     img.show()
#     img.save("2-2.png")
