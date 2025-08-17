# %% [markdown]
# ### 기본설정

# %%
import os
import sys
import logging
from ast import literal_eval

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

from consistentvideo import reference
from consistentvideo import story
from consistentvideo import video

# 로깅 설정 (노트북/스크립트 공통)
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)

# %% [markdown]
# 디렉토리 설정

# %%
# 디렉토리 설정
# BASE_DIR = os.path.abspath(os.path.join('.'))
# UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
# os.makedirs(UPLOAD_DIR, exist_ok=True)
# file_path = os.path.join(UPLOAD_DIR, "컬투쇼버스.txt")

# 기본
ENTITY_SET_NAME = "컬투쇼버스"
WORK_DIR = os.path.join("demo-file/", ENTITY_SET_NAME)

# 모델/화풍/품질 설정
TEXT_MODEL = "gpt-4.1"            # 예: "gpt-4.1", "gpt-5" 등
IMAGE_MODEL = "gpt-image-1"       # 예: "gpt-image-1", "dalle3"
IMAGE_STYLE = "realistic"          # realistic | illustration | anime | watercolor | oil_painting | comic | storybook | sketch | pixel_art | lowpoly
IMAGE_QUALITY = "low"              # low | medium | high
IMAGE_SIZE = "1536x1024"           # 예: "1024x1024", "1536x1024", "2048x2048"
VIDEO_MODEL = "veo-3.0-fast-generate-preview"               # "runway" | "veo3" | "veo-3.0-generate-preview" | "veo-3.0-fast-generate-preview"

# 레퍼런스 생성부
SYNOPSIS_TXT_PATH = "demo-file/컬투쇼버스.txt"  # SYNOPSIS_TEXT 파일입출력(선택)
SYNOPSIS_TEXT = "시놉시스 텍스트"
REFERENCE_PATH = os.path.join(WORK_DIR, "reference")
REFERENCE_IMG_PATH = os.path.join(REFERENCE_PATH, "images")
REFERENCE_ENTITY_LIST_PATH = os.path.join(REFERENCE_PATH, "entity_list.txt")

# 씬/컷 분리부
STORY_TXT_PATH = "demo-file/컬투쇼버스.txt"  # STORY_TEXT 파일입출력(선택)
STORY_TEXT = "스토리 텍스트"
STORY_PATH = os.path.join(WORK_DIR, "story")
STORY_CUT_LIST_PATH = os.path.join(STORY_PATH, "cut.txt")

# 비디오 생성부
VIDEO_PATH = os.path.join(WORK_DIR, "video")
CUT_IMG_PATH = os.path.join(VIDEO_PATH, "cut-images")
VIDEO_OUTPUT_PATH = os.path.join(VIDEO_PATH, "output")
VIDEO_CLIP_LIST_PATH = os.path.join(VIDEO_PATH, "clip_file_list.txt")
VIDEO_CONCAT_OUTPUT_PATH = os.path.join(VIDEO_PATH, f"{ENTITY_SET_NAME}_concat_video.mp4")

os.makedirs(WORK_DIR, exist_ok=True)

# %% [markdown]
# ## 레퍼런스 생성부 테스트

# %%
# 클래스 인스턴스
analyzer = reference.SynopsisAnalyzer()
character_creator = reference.CharacterImageCreator()
location_creator = reference.LocationImageCreator()
object_creator = reference.ObjectImageCreator()

# %%
# SYNOPSIS_TEXT 파일입출력(선택)
with open(SYNOPSIS_TXT_PATH, "r", encoding="utf-8") as f:
    SYNOPSIS_TEXT = f.read()

# 3. 시놉시스 분석 및 파싱
analyzer.save_dir = os.path.join(REFERENCE_PATH, "analyzer")
entity_dict_draft_list = analyzer.analyze(SYNOPSIS_TEXT)
logger.info(f"엔티티 초안 개수: {len(entity_dict_draft_list)}")


# %%
# 4. Creator들에게 base 디렉토리 설정
character_creator.set_base_dir(REFERENCE_IMG_PATH)
location_creator.set_base_dir(REFERENCE_IMG_PATH)
object_creator.set_base_dir(REFERENCE_IMG_PATH)

# 이미지 생성기 공통 옵션 적용
for creator in (character_creator, location_creator, object_creator):
    if hasattr(creator, "set_image_model"):
        creator.set_image_model(IMAGE_MODEL)
    if hasattr(creator, "set_style"):
        creator.set_style(IMAGE_STYLE)
    if hasattr(creator, "set_image_quality"):
        creator.set_image_quality(IMAGE_QUALITY)
    if hasattr(creator, "set_image_size"):
        creator.set_image_size(IMAGE_SIZE)

# 5. 이미지 생성 및 결과 수집
entity_list = []
# results를 txt 파일로 저장
with open(REFERENCE_ENTITY_LIST_PATH, "w", encoding="utf-8") as f:
    for entity in entity_dict_draft_list:
        type_ = entity.get("type")
        name = entity.get("name")
        description = entity.get("description")

        try:
            if name == "기타":
                result = (type_, name, description, None)
            elif type_ == "character":
                result = character_creator.create(type_, name, description)
            elif type_ == "location":
                result = location_creator.create(type_, name, description)
            elif type_ == "object":
                result = object_creator.create(type_, name, description)
            else:
                result = (type_, name, description, None)
        except Exception as e:
            logger.error(f"이미지 생성 실패 [{type_}:{name}]: {e}")
            result = (type_, name, description, None)

        logger.info(f"[RESULT] {result}")
        entity_list.append(result)
        f.write(str(result) + "\n")


# %% [markdown]
# 엔티티 이미지 생성 8분 17초 소요

# %%
logger.info(f"엔티티 최종 개수: {len(entity_list)}")

# %% [markdown]
# ## 씬/컷 분리부 테스트

# %%
def load_entity_list(file_path):
    entities = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            # 빈 줄 건너뛰기
            if not line.strip():
                continue
            # 문자열을 튜플로 안전하게 변환
            try:
                entity_tuple = literal_eval(line.strip())
                entities.append(entity_tuple)
            except Exception as e:
                logger.warning(f"라인 파싱 중 오류 발생: {e}")
                continue
    return entities


# 엔티티 리스트 로드
entity_list = load_entity_list(REFERENCE_ENTITY_LIST_PATH)
logger.info(f"로드된 엔티티 개수: {len(entity_list)}")

# %%
# 예시 스토리
with open(STORY_TXT_PATH, "r", encoding="utf-8") as f:
    STORY_TEXT = f.read()

scene_gen = story.SceneGenerator()
scenes = scene_gen.generate_scenes(STORY_TEXT, model=TEXT_MODEL)

os.makedirs(STORY_PATH, exist_ok=True)
with open(os.path.join(STORY_PATH, "scene.txt"), "w", encoding="utf-8") as f:
    for scene in scenes:
        logger.info(f"씬 생성: {scene}")
        f.write(str(scene) + "\n")


# %%
cut_generator = story.CutGenerator()
cut_list = list()

with open(STORY_CUT_LIST_PATH, "w", encoding="utf-8") as f:
    for scene in scenes:
        cut = cut_generator.cut_scene(scene, entity_list, story_text=STORY_TEXT, model=TEXT_MODEL)
        cut_list.append(cut)
        logger.info(f"컷 분리 결과: {cut}")
        f.write(str(cut) + "\n")


# %% [markdown]
# 컷생성 1분 2초 소요

# %%
# print(scenes)
logger.info(f"전체 컷 리스트 개수(씬별): {len(cut_list)}")

# %% [markdown]
# ## 비디오 생성부 테스트

# %%
os.makedirs(CUT_IMG_PATH, exist_ok=True)

# %%
# 파일에서 entity_list, cut_list 로드

def load_entity_list(file_path):
    entities = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            # 빈 줄 건너뛰기
            if not line.strip():
                continue
            # 문자열을 튜플로 안전하게 변환
            try:
                entity_tuple = literal_eval(line.strip())
                entities.append(entity_tuple)
            except Exception as e:
                logger.warning(f"라인 파싱 중 오류 발생: {e}")
                continue
    return entities


def load_cut_list(file_path):
    cuts_by_scene = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            # 빈 줄 건너뛰기
            if not line.strip():
                continue
            try:
                # ast.literal_eval을 사용하여 더 안전하게 파싱
                scene_cuts = literal_eval(line.strip())
                cuts_by_scene.append(scene_cuts)
            except Exception as e:
                logger.warning(f"파싱 중 오류 발생: {e}")
                continue
    return cuts_by_scene

# %%
# 엔티티 리스트 로드
entity_list = load_entity_list(REFERENCE_ENTITY_LIST_PATH)
logger.info(f"로드된 엔티티 개수: {len(entity_list)}")

# 컷 리스트 로드
cut_list = load_cut_list(STORY_CUT_LIST_PATH)
logger.info(f"로드된 컷 씬 개수: {len(cut_list)}")

# %%
scene_num = 1
for scene in cut_list:
    cut_num = 1
    for cut in scene:
        cut_image_generator = video.CutImageGenerator(
            scene_num=scene_num,
            cut=cut,
            output_path=CUT_IMG_PATH,
            entity_image_path=REFERENCE_IMG_PATH,
            entity=entity_list,
            ai_model=IMAGE_MODEL,
            style=IMAGE_STYLE,
            quality=IMAGE_QUALITY,
            size=IMAGE_SIZE,
        )
        filename = cut_image_generator.execute()
        logger.info(f"save {filename}")
    scene_num += 1

# %%
image_paths = []
for filename in os.listdir(CUT_IMG_PATH):
    if filename.lower().endswith('.png') or filename.lower().endswith('.jpg'):  # 대소문자 구분 없이 .png 확장자 확인
        image_paths.append(os.path.join(CUT_IMG_PATH, filename))
image_paths.sort()
image_paths

# %%
video_generator = video.VideoGenerator(cut_list, VIDEO_OUTPUT_PATH, cut_image_list=image_paths, ai_model=VIDEO_MODEL)
video_generator.execute()

# %%
video_clip_path_list = []
for filename in os.listdir(VIDEO_OUTPUT_PATH):
    if filename.lower().endswith('.mp4'):
        video_clip_path_list.append(os.path.join(VIDEO_OUTPUT_PATH, filename))
video_clip_path_list.sort()

logger.info(f"클립 파일 수: {len(video_clip_path_list)}")

# %%
import ffmpeg

# results 리스트에 있는 비디오들을 합치기 (원본 스트림 그대로: concat demuxer + copy)
final_output = VIDEO_CONCAT_OUTPUT_PATH

# ffmpeg concat용 파일 리스트 생성
with open(VIDEO_CLIP_LIST_PATH, "w", encoding="utf-8") as f:
    for video_path in video_clip_path_list:
        abs_path = os.path.abspath(video_path)
        f.write(f"file '{abs_path}'\n")

# concat demuxer 사용해 원본 비디오/오디오 스트림 그대로 복사
(
    ffmpeg
    .input(VIDEO_CLIP_LIST_PATH, format="concat", safe=0)
    .output(final_output, c="copy")
    .run(overwrite_output=True)
)

# %% [markdown]
# ## 멀티모달 엔티티 편집/추가 예시

# %%
# 파일에서 entity_list, cut_list 로드

def load_entity_list(file_path):
    entities = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            # 빈 줄 건너뛰기
            if not line.strip():
                continue
            # 문자열을 튜플로 안전하게 변환
            try:
                entity_tuple = eval(line.strip())
                entities.append(entity_tuple)
            except Exception as e:
                print(f"라인 파싱 중 오류 발생: {e}")
                continue
    return entities


def load_cut_list(file_path):
    cuts_by_scene = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            # 빈 줄 건너뛰기
            if not line.strip():
                continue
            try:
                # ast.literal_eval을 사용하여 더 안전하게 파싱
                scene_cuts = literal_eval(line.strip())
                cuts_by_scene.append(scene_cuts)
            except Exception as e:
                print(f"파싱 중 오류 발생: {e}")
                continue
    return cuts_by_scene

# %%
from consistentvideo.multimodal import EntityMultimodalEditor, edit_or_add_entity

# 에디터 생성 (레퍼런스 이미지가 저장되는 경로를 그대로 사용)
editor = EntityMultimodalEditor(entity_image_base_dir=REFERENCE_IMG_PATH)

# 멀티모달 분석에 사용할 샘플 이미지 선택 (존재할 경우 첫 번째 이미지 사용)
if os.path.exists(REFERENCE_IMG_PATH):
    for fn in os.listdir(REFERENCE_IMG_PATH):
        if fn.lower().endswith((".png", ".jpg", ".jpeg")):
            sample_image = os.path.abspath(os.path.join(REFERENCE_IMG_PATH, fn))
            break
# sample_image = None # 이미지 위치 지정

# 엔티티 리스트 로드
entity_list = load_entity_list(REFERENCE_ENTITY_LIST_PATH)
print(entity_list)

# %%

# 1) 엔티티 수정 예시: 0번 인덱스 엔티티를 이미지 분석(gpt-4.1)과 추가 프롬프트를 반영하여 설명 갱신 후,
#    레퍼런스 이미지를 gpt-image-1로 재생성
if entity_list:
    entity_list = edit_or_add_entity(
        entity_list,
        operation="edit",
        editor=editor,
        index=1,  # 수정할 엔티티 인덱스
        name=None,  # 이름 변경이 필요하면 문자열 지정
        description="",
        image_path=sample_image,  # 이미지가 없으면 None도 가능
        # extra_prompt="추가 프롬프트: 자연광, 사실적인 질감",
    )
    EntityMultimodalEditor.save_entity_list(REFERENCE_ENTITY_LIST_PATH, entity_list)
    print("[Multimodal] 1번 엔티티 수정 완료:", entity_list[1])


# %%

# 2) 엔티티 추가 예시: 새로운 오브젝트를 이미지 분석(gpt-4.1)과 추가 프롬프트를 반영하여 추가하고,
#    레퍼런스 이미지를 gpt-image-1로 생성
entity_list = edit_or_add_entity(
    entity_list,
    operation="add",
    editor=editor,
    type_="character",  # character | location | object
    name="테스트아코",
    # description="예시로 추가된 오브젝트",
    image_path=sample_image,
    # extra_prompt="작고 둥근 형태",
)
EntityMultimodalEditor.save_entity_list(REFERENCE_ENTITY_LIST_PATH, entity_list)
print("[Multimodal] 새 엔티티 추가 완료:", entity_list[-1])



