from base import VideoGeneratorBase
import base64
import time
import requests
from runwayml import RunwayML

# class VideoGenerator(VideoGeneratorBase):

#     def __init__(self, cut_image=None):
#         super().__init__(cut_image)
#         self.ai_model = self.__create_client()

#     def __create_client(self) -> OpenAI:
#         api_key = self.__load_gpt_api_key()
#         return OpenAI(api_key=api_key)

#     def __load_gpt_api_key(self) -> str:
#         try:
#             with open("api_key.txt", "r") as file:
#                 return file.read().strip()
#         except FileNotFoundError:
#             raise RuntimeError("api key doesn't exist")


client = RunwayML()

image = './example.png'

# encode image to base64
with open(image, "rb") as f:
    base64_image = base64.b64encode(f.read()).decode("utf-8")

# Create a new image-to-video task using the "gen4_turbo" model
task = client.image_to_video.create(
  model='gen4_turbo',
  # Point this at your own image file
  prompt_image=f"data:image/png;base64,{base64_image}",
  prompt_text='Generate a video',
  ratio='1280:720',
  duration=5,
)
task_id = task.id

# Poll the task until it's complete
time.sleep(10)  # Wait for ten seconds before polling
task = client.tasks.retrieve(task_id)
while task.status not in ['SUCCEEDED', 'FAILED']:
  time.sleep(10)  # Wait for ten seconds before polling
  task = client.tasks.retrieve(task_id)

print('Task complete:', task)

# Check if the task succeeded
if task.status == 'SUCCEEDED':
    video_url = task.output['video']  # Runway가 생성한 비디오 URL
    print("Video URL:", video_url)

    # Download the video and save it locally
    response = requests.get(video_url)
    if response.status_code == 200:
        with open("generated_video.mp4", "wb") as f:
            f.write(response.content)
        print("Video saved as 'generated_video.mp4'")
    else:
        print("Failed to download video. Status code:", response.status_code)
else:
    print("Video generation failed. Task status:", task.status)