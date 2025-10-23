import os
import sys
import json
import logging
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# 부모 디렉토리를 파이썬 경로에 추가하여 `consistentvideo` 패키지 임포트 가능하게 설정
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PARENT_DIR not in sys.path:
    sys.path.append(PARENT_DIR)

from consistentvideo import reference, story, video  # noqa: E402
from consistentvideo.multimodal import EntityMultimodalEditor, edit_or_add_entity  # noqa: E402


logger = logging.getLogger(__name__)

# .env 로드 (필요 시)
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass


# -----------------------------
# 공용 유틸
# -----------------------------
def ensure_dir(path: str) -> None:
    if path:
        os.makedirs(path, exist_ok=True)


def load_text_from_path_or_content(path: Optional[str], content: Optional[str]) -> str:
    if path:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return content or ""


def derive_paths(work_dir: Optional[str], entity_set_name: Optional[str]) -> dict:
    """WORK_DIR/ENTITY_SET_NAME 하위에 표준 경로들을 유도한다."""
    if not work_dir:
        return {
            "REFERENCE_PATH": None,
            "REFERENCE_ANALYZER_DIR": None,
            "REFERENCE_IMAGES_DIR": None,
            "REFERENCE_ENTITY_LIST_PATH": None,
            "STORY_PATH": None,
            "SCENE_TXT_PATH": None,
            "CUT_TXT_PATH": None,
            "VIDEO_PATH": None,
            "CUT_IMG_DIR": None,
            "VIDEO_OUTPUT_DIR": None,
            "CLIP_LIST_PATH": None,
            "FINAL_OUTPUT_PATH": None,
        }

    base_dir = work_dir
    if entity_set_name:
        base_dir = os.path.join(work_dir, entity_set_name)

    reference_path = os.path.join(base_dir, "reference")
    story_path = os.path.join(base_dir, "story")
    video_path = os.path.join(base_dir, "video")

    final_output_name = f"{entity_set_name}_concat_video.mp4" if entity_set_name else "final_concat_video.mp4"

    return {
        "REFERENCE_PATH": reference_path,
        "REFERENCE_ANALYZER_DIR": os.path.join(reference_path, "analyzer"),
        "REFERENCE_IMAGES_DIR": os.path.join(reference_path, "images"),
        "REFERENCE_ENTITY_LIST_PATH": os.path.join(reference_path, "entity_list.txt"),
        "STORY_PATH": story_path,
        "SCENE_TXT_PATH": os.path.join(story_path, "scene.txt"),
        "CUT_TXT_PATH": os.path.join(story_path, "cut.txt"),
        "VIDEO_PATH": video_path,
        "CUT_IMG_DIR": os.path.join(video_path, "cut-images"),
        "VIDEO_OUTPUT_DIR": os.path.join(video_path, "output"),
        "CLIP_LIST_PATH": os.path.join(video_path, "clip_file_list.txt"),
        "FINAL_OUTPUT_PATH": os.path.join(video_path, final_output_name),
    }


def load_entity_list(file_path: str) -> list:
    import ast
    entities = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                entity_tuple = ast.literal_eval(line.strip())
                entities.append(entity_tuple)
            except Exception:
                continue
    return entities


def load_cut_list(file_path: str) -> list:
    import ast
    cuts_by_scene = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                scene_cuts = ast.literal_eval(line.strip())
                cuts_by_scene.append(scene_cuts)
            except Exception:
                continue
    return cuts_by_scene


def parse_json_str(json_str: Optional[str]):
    if not json_str:
        return None
    try:
        return json.loads(json_str)
    except Exception:
        return None


def read_upload_text_sync(upload: Optional[UploadFile]) -> Optional[str]:
    if upload is None:
        return None
    try:
        data = upload.file.read()
        if not data:
            return ""
        try:
            return data.decode("utf-8")
        except Exception:
            return data.decode("utf-8", errors="ignore")
    except Exception:
        return None


def parse_entity_list_from_text(text: Optional[str]) -> list:
    if not text:
        return []
    import ast
    entities = []
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            entities.append(ast.literal_eval(line.strip()))
        except Exception:
            continue
    return entities


def parse_cut_list_from_text(text: Optional[str]) -> list:
    if not text:
        return []
    import ast
    cuts_by_scene = []
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            cuts_by_scene.append(ast.literal_eval(line.strip()))
        except Exception:
            continue
    return cuts_by_scene


def parse_scenes_from_text(text: Optional[str]) -> list:
    if not text:
        return []
    import ast
    scenes = []
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            scenes.append(ast.literal_eval(line.strip()))
        except Exception:
            continue
    return scenes


def save_text(path: str, text: str) -> None:
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        f.write(text or "")


# -----------------------------
# 스키마
# -----------------------------
class SynopsisAnalyzeRequest(BaseModel):
    entity_set_name: Optional[str] = Field(default=None)
    work_dir: Optional[str] = Field(default=None)
    synopsis_text: Optional[str] = Field(default=None, description="분석할 시놉시스 텍스트")
    synopsis_text_path: Optional[str] = Field(default=None, description="시놉시스를 읽을 파일 경로(옵션)")
    analyzer_save_dir: Optional[str] = Field(default=None, description="시놉시스 분석 결과 저장 디렉토리, 예: <WORK_DIR>/reference/analyzer")
    text_model: str = Field(default="gpt-4.1", description="텍스트 모델 이름")


class SynopsisAnalyzeResponse(BaseModel):
    entity_dict_draft_list: list
    saved_txt_path: str
    saved_json_path: str


class CreateEntitiesRequest(BaseModel):
    entity_set_name: Optional[str] = Field(default=None)
    work_dir: Optional[str] = Field(default=None)
    entity_dict_draft_list: Optional[list] = None
    entity_draft_json_path: Optional[str] = None
    reference_image_dir: Optional[str] = Field(default=None, description="엔티티 이미지가 저장될 경로, 예: <WORK_DIR>/reference/images")
    entity_list_output_path: Optional[str] = Field(default=None, description="엔티티 리스트를 저장할 파일 경로, 예: <WORK_DIR>/reference/entity_list.txt")
    image_model: str = Field(default="gpt-image-1")
    image_style: str = Field(default="realistic")
    image_quality: str = Field(default="low")
    image_size: str = Field(default="1536x1024")


class CreateEntitiesResponse(BaseModel):
    entity_list: list
    entity_list_output_path: str


class GenerateScenesRequest(BaseModel):
    entity_set_name: Optional[str] = Field(default=None)
    work_dir: Optional[str] = Field(default=None)
    story_text: Optional[str] = None
    story_text_path: Optional[str] = None
    output_scene_txt_path: Optional[str] = None
    text_model: str = Field(default="gpt-4.1")


class GenerateScenesResponse(BaseModel):
    scenes: list
    output_scene_txt_path: Optional[str]


class GenerateCutsRequest(BaseModel):
    entity_set_name: Optional[str] = Field(default=None)
    work_dir: Optional[str] = Field(default=None)
    scenes: Optional[list] = None
    scenes_txt_path: Optional[str] = None
    entity_list_path: Optional[str] = None
    story_text: Optional[str] = None
    story_text_path: Optional[str] = None
    cuts_output_path: Optional[str] = None
    text_model: str = Field(default="gpt-4.1")


class GenerateCutsResponse(BaseModel):
    cut_list: list
    cuts_output_path: str


class GenerateCutImagesRequest(BaseModel):
    entity_set_name: Optional[str] = Field(default=None)
    work_dir: Optional[str] = Field(default=None)
    entity_list_path: Optional[str] = None
    cut_list_path: Optional[str] = None
    cut_image_output_dir: Optional[str] = None
    entity_image_dir: Optional[str] = None
    image_model: str = Field(default="gpt-image-1")
    image_style: str = Field(default="realistic")
    image_quality: str = Field(default="low")
    image_size: str = Field(default="1536x1024")


class GenerateCutImagesResponse(BaseModel):
    cut_image_paths: List[str]


class GenerateCutVideosRequest(BaseModel):
    entity_set_name: Optional[str] = Field(default=None)
    work_dir: Optional[str] = Field(default=None)
    cut_image_dir: Optional[str] = None
    cut_image_paths: Optional[List[str]] = None
    cut_list_path: Optional[str] = None
    video_output_dir: Optional[str] = None
    video_model: str = Field(default="veo-3.0-fast-generate-preview")


class GenerateCutVideosResponse(BaseModel):
    video_clip_paths: List[str]


class ConcatVideosRequest(BaseModel):
    entity_set_name: Optional[str] = Field(default=None)
    work_dir: Optional[str] = Field(default=None)
    video_clip_paths: Optional[List[str]] = None
    video_output_dir: Optional[str] = None
    clip_list_path: Optional[str] = None
    final_output_path: Optional[str] = None


class ConcatVideosResponse(BaseModel):
    final_output_path: str


# -----------------------------
# FastAPI 앱 설정
# -----------------------------
app = FastAPI(title="Consistent AI Video Generator API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 1) 시놉시스 분석
@app.post("/analyze-synopsis", response_model=SynopsisAnalyzeResponse)
def analyze_synopsis(
    entity_set_name: Optional[str] = Form(None),
    work_dir: Optional[str] = Form(None),
    synopsis_text: Optional[str] = Form(None),
    synopsis_text_path: Optional[str] = Form(None),
    synopsis_text_file: Optional[UploadFile] = File(None),
    analyzer_save_dir: Optional[str] = Form(None),
    text_model: str = Form("gpt-4.1"),
):
    os.environ.setdefault("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))

    # 기본 경로 유도
    paths = derive_paths(work_dir, entity_set_name)
    analyzer_dir = analyzer_save_dir or paths["REFERENCE_ANALYZER_DIR"]

    ensure_dir(analyzer_dir)

    analyzer = reference.SynopsisAnalyzer(save_dir=analyzer_dir)
    # 현재 SynopsisAnalyzer는 모델을 외부에서 받지 않으므로 입력 모델은 무시됨
    uploaded_text = read_upload_text_sync(synopsis_text_file)
    synopsis = uploaded_text if uploaded_text is not None else load_text_from_path_or_content(synopsis_text_path, synopsis_text)

    # synopsis 텍스트 저장 및 기본값 처리
    synopsis_txt_default_path = os.path.join(paths["REFERENCE_PATH"], "synopsis_text.txt")
    provided_synopsis = (synopsis_text_file is not None) or (synopsis_text_path is not None) or (synopsis_text is not None)
    if provided_synopsis:
        # 사용자가 입력한 경우 항상 저장
        save_text(synopsis_txt_default_path, synopsis or "")
    else:
        # 입력이 없으면 기본 파일에서 로드 시도
        if os.path.exists(synopsis_txt_default_path):
            with open(synopsis_txt_default_path, "r", encoding="utf-8") as f:
                synopsis = f.read()
        else:
            raise HTTPException(status_code=400, detail="synopsis_text is required (no input and no default file found)")
    entity_dict_draft_list = analyzer.analyze(synopsis)

    saved_txt = os.path.join(analyzer_dir, "entity_draft.txt")
    saved_json = os.path.join(analyzer_dir, "entity_dict_draft.json")
    return SynopsisAnalyzeResponse(entity_dict_draft_list=entity_dict_draft_list, saved_txt_path=saved_txt, saved_json_path=saved_json)


# 2-1) 레퍼런스(entity) 이미지 생성 및 entity_list 생성
@app.post("/create-entities", response_model=CreateEntitiesResponse)
def create_entities(
    entity_set_name: Optional[str] = Form(None),
    work_dir: Optional[str] = Form(None),
    entity_dict_draft_list: Optional[str] = Form(None),  # JSON 문자열
    entity_draft_json_path: Optional[str] = Form(None),
    entity_draft_json_file: Optional[UploadFile] = File(None),
    reference_image_dir: Optional[str] = Form(None),
    entity_list_output_path: Optional[str] = Form(None),
    image_model: str = Form("gpt-image-1"),
    image_style: str = Form("realistic"),
    image_quality: str = Form("low"),
    image_size: str = Form("1536x1024"),
):
    paths = derive_paths(work_dir, entity_set_name)
    reference_image_dir = reference_image_dir or paths["REFERENCE_IMAGES_DIR"]
    entity_list_output_path = entity_list_output_path or paths["REFERENCE_ENTITY_LIST_PATH"]

    ensure_dir(reference_image_dir)
    ensure_dir(os.path.dirname(entity_list_output_path))

    # 입력 엔티티 로드
    entities = parse_json_str(entity_dict_draft_list)
    if entities is None and entity_draft_json_file is not None:
        try:
            text = read_upload_text_sync(entity_draft_json_file)
            if text:
                entities = json.loads(text)
        except Exception:
            entities = None
    if entities is None:
        json_path = entity_draft_json_path or (paths["REFERENCE_ANALYZER_DIR"] and os.path.join(paths["REFERENCE_ANALYZER_DIR"], "entity_dict_draft.json"))
        if json_path and os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                entities = json.load(f)
    if entities is None:
        entities = []

    character_creator = reference.CharacterImageCreator()
    location_creator = reference.LocationImageCreator()
    object_creator = reference.ObjectImageCreator()

    for creator in (character_creator, location_creator, object_creator):
        creator.set_base_dir(reference_image_dir)
        creator.set_image_model(image_model)
        creator.set_style(image_style)
        creator.set_image_quality(image_quality)
        creator.set_image_size(image_size)
        # Gemini 모델인 경우 aspect ratio 설정
        if image_model == "gemini-2.5-flash-imag(Nano Banana)":
            creator.set_aspect_ratio("1:1")

    entity_list = []
    with open(entity_list_output_path, "w", encoding="utf-8") as f:
        for entity in entities:
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
            entity_list.append(result)
            f.write(str(result) + "\n")

    return CreateEntitiesResponse(entity_list=entity_list, entity_list_output_path=entity_list_output_path)


# 2-2) 멀티모달 기반 entity_list 수정 또는 생성 (이미지 업로드 지원)
@app.post("/multimodal/edit-or-add")
async def multimodal_edit_or_add(
    operation: str = Form(..., description="'edit' 또는 'add'"),
    entity_set_name: Optional[str] = Form(None),
    work_dir: Optional[str] = Form(None),
    entity_list_path: Optional[str] = Form(None, description="기존 엔티티 리스트 파일 경로"),
    reference_image_dir: Optional[str] = Form(None, description="레퍼런스 이미지 저장 경로"),
    index: Optional[int] = Form(None, description="수정할 엔티티 인덱스 (edit용)"),
    type_: Optional[str] = Form(None, description="추가할 타입 (add용)"),
    name: Optional[str] = Form(None, description="수정/추가 이름"),
    description: Optional[str] = Form(None, description="설명 힌트"),
    extra_prompt: Optional[str] = Form(None, description="추가 프롬프트"),
    text_model: str = Form("gpt-4.1"),
    image_model: str = Form("gpt-image-1"),
    image_style: str = Form("realistic"),
    image_quality: str = Form("low"),
    image_size: str = Form("1024x1024"),
    image: Optional[UploadFile] = File(None),
):
    paths = derive_paths(work_dir, entity_set_name)
    reference_image_dir = reference_image_dir or paths["REFERENCE_IMAGES_DIR"]
    entity_list_path = entity_list_path or paths["REFERENCE_ENTITY_LIST_PATH"]

    ensure_dir(reference_image_dir)

    # 엔티티 리스트 로드
    entity_list = load_entity_list(entity_list_path)

    # 업로드 이미지(옵션) 저장
    image_path: Optional[str] = None
    if image is not None:
        # 파일명을 간단히 정규화
        safe_name = os.path.basename(image.filename)
        image_path = os.path.join(reference_image_dir, f"uploaded_{safe_name}")
        with open(image_path, "wb") as f:
            f.write(await image.read())

    editor = EntityMultimodalEditor(
        entity_image_base_dir=reference_image_dir,
        text_model=text_model,
        image_model=image_model,
        image_style=image_style,
        image_quality=image_quality,
        image_size=image_size,
    )
    
    # Gemini 모델인 경우 aspect ratio 설정
    if image_model == "gemini-2.5-flash-imag(Nano Banana)":
        editor.set_aspect_ratio("1:1")

    # 수정/추가 실행
    updated_list = edit_or_add_entity(
        entity_list,
        operation=operation,
        editor=editor,
        index=index,
        type_=type_,
        name=name,
        description=description,
        image_path=image_path,
        extra_prompt=extra_prompt,
    )

    # 저장
    EntityMultimodalEditor.save_entity_list(entity_list_path, updated_list)

    return {
        "entity_list": updated_list,
        "entity_list_path": entity_list_path,
    }


# 3) 씬 생성
@app.post("/generate-scenes", response_model=GenerateScenesResponse)
def generate_scenes(
    entity_set_name: Optional[str] = Form(None),
    work_dir: Optional[str] = Form(None),
    story_text: Optional[str] = Form(None),
    story_text_path: Optional[str] = Form(None),
    story_text_file: Optional[UploadFile] = File(None),
    output_scene_txt_path: Optional[str] = Form(None),
    text_model: str = Form("gpt-4.1"),
):
    story_text_content = read_upload_text_sync(story_text_file)
    story_text_content = story_text_content if story_text_content is not None else load_text_from_path_or_content(story_text_path, story_text)

    paths = derive_paths(work_dir, entity_set_name)

    # story_text 저장/기본값 처리
    story_txt_default_path = os.path.join(paths["STORY_PATH"], "story_text.txt")
    synopsis_txt_default_path = os.path.join(paths["REFERENCE_PATH"], "synopsis_text.txt")
    provided_story = (story_text_file is not None) or (story_text_path is not None) or (story_text is not None)
    if provided_story:
        save_text(story_txt_default_path, story_text_content or "")
    else:
        if os.path.exists(story_txt_default_path):
            with open(story_txt_default_path, "r", encoding="utf-8") as f:
                story_text_content = f.read()
        elif os.path.exists(synopsis_txt_default_path):
            with open(synopsis_txt_default_path, "r", encoding="utf-8") as f:
                story_text_content = f.read()
            save_text(story_txt_default_path, story_text_content)
        else:
            raise HTTPException(status_code=400, detail="story_text is required (no input and no default file found)")

    scene_gen = story.SceneGenerator()
    scenes = scene_gen.generate_scenes(story_text_content, model=text_model)

    output_scene_txt_path = output_scene_txt_path or paths["SCENE_TXT_PATH"]

    output_path = None
    if output_scene_txt_path:
        ensure_dir(os.path.dirname(output_scene_txt_path))
        with open(output_scene_txt_path, "w", encoding="utf-8") as f:
            for scene in scenes:
                f.write(str(scene) + "\n")
        output_path = output_scene_txt_path

    return GenerateScenesResponse(scenes=scenes, output_scene_txt_path=output_path)


# 4) 컷 생성
@app.post("/generate-cuts", response_model=GenerateCutsResponse)
def generate_cuts(
    entity_set_name: Optional[str] = Form(None),
    work_dir: Optional[str] = Form(None),
    scenes: Optional[str] = Form(None),  # JSON 문자열 배열
    scenes_txt_path: Optional[str] = Form(None),
    scenes_txt_file: Optional[UploadFile] = File(None),
    entity_list_path: Optional[str] = Form(None),
    entity_list_file: Optional[UploadFile] = File(None),
    story_text: Optional[str] = Form(None),
    story_text_path: Optional[str] = Form(None),
    story_text_file: Optional[UploadFile] = File(None),
    cuts_output_path: Optional[str] = Form(None),
    text_model: str = Form("gpt-4.1"),
):
    # 씬 로드
    scenes_list = parse_json_str(scenes)
    if scenes_list is None:
        import ast
        scenes_list = []
        uploaded_scenes_text = read_upload_text_sync(scenes_txt_file)
        if uploaded_scenes_text is not None:
            scenes_list = parse_scenes_from_text(uploaded_scenes_text)
        scenes_txt = scenes_txt_path
        if not scenes_txt:
            paths = derive_paths(work_dir, entity_set_name)
            scenes_txt = paths["SCENE_TXT_PATH"]
        if scenes_txt and os.path.exists(scenes_txt):
            with open(scenes_txt, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        scenes_list.append(ast.literal_eval(line.strip()))
                    except Exception:
                        continue
    if scenes_list is None:
        scenes_list = []

    # 스토리 텍스트 로드
    uploaded_story_text = read_upload_text_sync(story_text_file)
    story_text_content = uploaded_story_text if uploaded_story_text is not None else load_text_from_path_or_content(story_text_path, story_text)

    # 엔티티 리스트 로드
    paths = derive_paths(work_dir, entity_set_name)
    if entity_list_file is not None:
        entity_list = parse_entity_list_from_text(read_upload_text_sync(entity_list_file))
    else:
        entity_list_path = entity_list_path or paths["REFERENCE_ENTITY_LIST_PATH"]
        entity_list = load_entity_list(entity_list_path)
    cuts_output = cuts_output_path or paths["CUT_TXT_PATH"]

    cut_generator = story.CutGenerator()
    cut_list = []
    for scene in scenes_list:
        cuts = cut_generator.cut_scene(scene, entity_list, story_text=story_text_content, model=text_model)
        cut_list.append(cuts)

    ensure_dir(os.path.dirname(cuts_output))
    with open(cuts_output, "w", encoding="utf-8") as f:
        for cuts in cut_list:
            f.write(str(cuts) + "\n")

    return GenerateCutsResponse(cut_list=cut_list, cuts_output_path=cuts_output)


# 5) 컷 이미지 생성
@app.post("/generate-cut-images", response_model=GenerateCutImagesResponse)
def generate_cut_images(
    entity_set_name: Optional[str] = Form(None),
    work_dir: Optional[str] = Form(None),
    entity_list_path: Optional[str] = Form(None),
    entity_list_file: Optional[UploadFile] = File(None),
    cut_list_path: Optional[str] = Form(None),
    cut_list_file: Optional[UploadFile] = File(None),
    cut_image_output_dir: Optional[str] = Form(None),
    entity_image_dir: Optional[str] = Form(None),
    image_model: str = Form("gpt-image-1"),
    image_style: str = Form("realistic"),
    image_quality: str = Form("low"),
    image_size: str = Form("1536x1024"),
    scene_num: Optional[int] = Form(None),
    cut_num: Optional[int] = Form(None),
    selected_cuts: Optional[str] = Form(None),  # JSON string of selected cuts
):
    paths = derive_paths(work_dir, entity_set_name)
    entity_list_path = entity_list_path or paths["REFERENCE_ENTITY_LIST_PATH"]
    cut_list_path = cut_list_path or paths["CUT_TXT_PATH"]
    cut_image_output_dir = cut_image_output_dir or paths["CUT_IMG_DIR"]
    entity_image_dir = entity_image_dir or paths["REFERENCE_IMAGES_DIR"]

    # 로드
    if entity_list_file is not None:
        entity_list = parse_entity_list_from_text(read_upload_text_sync(entity_list_file))
    else:
        entity_list = load_entity_list(entity_list_path)
    if cut_list_file is not None:
        cuts_by_scene = parse_cut_list_from_text(read_upload_text_sync(cut_list_file))
    else:
        cuts_by_scene = load_cut_list(cut_list_path)

    ensure_dir(cut_image_output_dir)

    cut_image_paths: List[str] = []

    # selected_cuts 파라미터가 있으면 선택된 컷만 처리
    if selected_cuts:
        import json
        selected_list = json.loads(selected_cuts)
        for cut_info in selected_list:
            s_num = cut_info["scene_num"]
            c_num = cut_info["cut_num"]
            if s_num < 1 or s_num > len(cuts_by_scene):
                continue
            scene_cuts = cuts_by_scene[s_num - 1]
            if c_num < 1 or c_num > len(scene_cuts):
                continue
            cut = scene_cuts[c_num - 1]
            # cut 객체에 cut_num 추가
            cut["cut_num"] = c_num
            generator = video.CutImageGenerator(
                scene_num=s_num,
                cut=cut,
                output_path=cut_image_output_dir,
                entity_image_path=entity_image_dir,
                entity=entity_list,
                ai_model=image_model,
                style=image_style,
                quality=image_quality,
                size=image_size,
            )
            filename = generator.execute()
            cut_image_paths.append(filename)
    # 단일 컷 지정 시 처리
    elif scene_num is not None and cut_num is not None:
        if scene_num < 1 or scene_num > len(cuts_by_scene):
            raise HTTPException(status_code=400, detail="scene_num out of range")
        scene_cuts = cuts_by_scene[scene_num - 1]
        if cut_num < 1 or cut_num > len(scene_cuts):
            raise HTTPException(status_code=400, detail="cut_num out of range")
        cut = scene_cuts[cut_num - 1]
        # cut 객체에 cut_num 추가
        cut["cut_num"] = cut_num
        generator = video.CutImageGenerator(
            scene_num=scene_num,
            cut=cut,
            output_path=cut_image_output_dir,
            entity_image_path=entity_image_dir,
            entity=entity_list,
            ai_model=image_model,
            style=image_style,
            quality=image_quality,
            size=image_size,
        )
        filename = generator.execute()
        cut_image_paths.append(filename)
    else:
        # 전체 컷 처리
        s_idx = 1
        for scene in cuts_by_scene:
            c_idx = 1
            for cut in scene:
                # cut 객체에 cut_num 추가
                cut["cut_num"] = c_idx
                cut_image_generator = video.CutImageGenerator(
                    scene_num=s_idx,
                    cut=cut,
                    output_path=cut_image_output_dir,
                    entity_image_path=entity_image_dir,
                    entity=entity_list,
                    ai_model=image_model,
                    style=image_style,
                    quality=image_quality,
                    size=image_size,
                )
                filename = cut_image_generator.execute()
                cut_image_paths.append(filename)
                c_idx += 1
            s_idx += 1

    cut_image_paths.sort()
    return GenerateCutImagesResponse(cut_image_paths=cut_image_paths)


# 6) 컷 영상 생성
@app.post("/generate-cut-videos", response_model=GenerateCutVideosResponse)
def generate_cut_videos(
    entity_set_name: Optional[str] = Form(None),
    work_dir: Optional[str] = Form(None),
    cut_image_dir: Optional[str] = Form(None),
    cut_image_paths: Optional[str] = Form(None),  # JSON string of image paths
    cut_list_path: Optional[str] = Form(None),
    cut_list_file: Optional[UploadFile] = File(None),
    video_output_dir: Optional[str] = Form(None),
    video_model: str = Form("veo-3.0-fast-generate-preview"),
    scene_num: Optional[int] = Form(None),
    cut_num: Optional[int] = Form(None),
):
    # 컷 이미지 목록 로드
    image_paths: List[str] = []
    if cut_image_paths:
        # cut_image_paths가 문자열로 전달되면 JSON으로 파싱
        if isinstance(cut_image_paths, str):
            import json
            try:
                cut_image_paths = json.loads(cut_image_paths)
            except:
                cut_image_paths = [cut_image_paths]
        
        # relative path를 absolute path로 변환
        base_path = os.path.join(work_dir, entity_set_name)
        for relative_path in cut_image_paths:
            if relative_path:
                full_path = os.path.join(base_path, relative_path)
                if os.path.exists(full_path):
                    image_paths.append(full_path)
    else:
        paths = derive_paths(work_dir, entity_set_name)
        cid = cut_image_dir or paths["CUT_IMG_DIR"]
        # 단일 컷 지정 시 해당 파일만 사용
        if scene_num is not None and cut_num is not None:
            # 컷 리스트를 사용해 파일명 구성
            paths2 = derive_paths(work_dir, entity_set_name)
            if cut_list_file is not None:
                cuts_by_scene = parse_cut_list_from_text(read_upload_text_sync(cut_list_file))
            else:
                clp = cut_list_path or paths2["CUT_TXT_PATH"]
                cuts_by_scene = load_cut_list(clp)
            if scene_num < 1 or scene_num > len(cuts_by_scene):
                raise HTTPException(status_code=400, detail="scene_num out of range")
            scene_cuts = cuts_by_scene[scene_num - 1]
            if cut_num < 1 or cut_num > len(scene_cuts):
                raise HTTPException(status_code=400, detail="cut_num out of range")
            cut = scene_cuts[cut_num - 1]
            cut_id = cut.get("cut_id", cut_num)
            expected = os.path.join(cid, f"S{scene_num:04d}-C{cut_id:04d}.png")
            if not os.path.exists(expected):
                raise HTTPException(status_code=400, detail=f"cut image not found: {expected}")
            image_paths = [expected]
        else:
            # 전체 이미지 사용
            for filename in os.listdir(cid):
                if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                    image_paths.append(os.path.join(cid, filename))
            image_paths.sort()

    # 컷 리스트 로드
    paths2 = derive_paths(work_dir, entity_set_name)
    if cut_list_file is not None:
        cut_list = parse_cut_list_from_text(read_upload_text_sync(cut_list_file))
    else:
        clp = cut_list_path or paths2["CUT_TXT_PATH"]
        cut_list = load_cut_list(clp)

    paths3 = derive_paths(work_dir, entity_set_name)
    vod = video_output_dir or paths3["VIDEO_OUTPUT_DIR"]
    ensure_dir(vod)

    video_generator = video.VideoGenerator(cut_list, vod, cut_image_list=image_paths, ai_model=video_model)
    video_generator.execute()

    # 생성된 영상 스캔
    video_clip_paths: List[str] = []
    for filename in os.listdir(vod):
        if filename.lower().endswith(".mp4"):
            video_clip_paths.append(os.path.join(vod, filename))
    video_clip_paths.sort()

    return GenerateCutVideosResponse(video_clip_paths=video_clip_paths)


# 7) 컷 영상 연결
@app.post("/concat-videos", response_model=ConcatVideosResponse)
def concat_videos(
    entity_set_name: Optional[str] = Form(None),
    work_dir: Optional[str] = Form(None),
    video_clip_paths: Optional[List[str]] = Form(None),
    video_output_dir: Optional[str] = Form(None),
    clip_list_path: Optional[str] = Form(None),
    final_output_path: Optional[str] = Form(None),
):
    paths = derive_paths(work_dir, entity_set_name)
    clip_list_path = clip_list_path or paths["CLIP_LIST_PATH"]
    final_output_path = final_output_path or paths["FINAL_OUTPUT_PATH"]
    video_output_dir = video_output_dir or paths["VIDEO_OUTPUT_DIR"]

    ensure_dir(os.path.dirname(clip_list_path))
    ensure_dir(os.path.dirname(final_output_path))

    # 입력 리스트 구성
    clip_paths: List[str] = []
    if video_clip_paths:
        clip_paths = video_clip_paths
    else:
        for filename in os.listdir(video_output_dir):
            if filename.lower().endswith(".mp4"):
                clip_paths.append(os.path.join(video_output_dir, filename))
        clip_paths.sort()

    with open(clip_list_path, "w", encoding="utf-8") as f:
        for video_path in clip_paths:
            abs_path = os.path.abspath(video_path)
            f.write(f"file '{abs_path}'\n")

    # ffmpeg-python 사용 시도, 실패 시 subprocess 폴백
    try:
        import ffmpeg  # type: ignore
        (
            ffmpeg
            .input(clip_list_path, format="concat", safe=0)
            .output(final_output_path, c="copy")
            .run(overwrite_output=True)
        )
    except Exception:
        import subprocess
        subprocess.run([
            "ffmpeg", "-f", "concat", "-safe", "0",
            "-i", clip_list_path, "-c", "copy", final_output_path
        ], check=True)

    return ConcatVideosResponse(final_output_path=final_output_path)


@app.get("/health")
def health():
    return {"status": "ok"}


# 8) 기존 entity_list 로드
@app.get("/load-entity-list")
def get_entity_list(
    work_dir: str,
    entity_set_name: str
):
    paths = derive_paths(work_dir, entity_set_name)
    entity_list_path = paths["REFERENCE_ENTITY_LIST_PATH"]
    
    if not entity_list_path or not os.path.exists(entity_list_path):
        raise HTTPException(status_code=404, detail="Entity list not found")
    
    entities = load_entity_list(entity_list_path)
    # 원본 상대 경로를 그대로 반환
    return {"entity_list": entities}


# 9) 기존 scenes 로드
@app.get("/load-scenes")
def get_scenes(
    work_dir: str,
    entity_set_name: str
):
    paths = derive_paths(work_dir, entity_set_name)
    scenes_path = paths["SCENE_TXT_PATH"]
    
    if not scenes_path or not os.path.exists(scenes_path):
        raise HTTPException(status_code=404, detail="Scenes not found")
    
    scenes = parse_scenes_from_text(open(scenes_path, "r", encoding="utf-8").read())
    return {"scenes": scenes}


# 10) 기존 cuts 로드
@app.get("/load-cuts")
def get_cuts(
    work_dir: str,
    entity_set_name: str
):
    paths = derive_paths(work_dir, entity_set_name)
    cuts_path = paths["CUT_TXT_PATH"]
    
    if not cuts_path or not os.path.exists(cuts_path):
        raise HTTPException(status_code=404, detail="Cuts not found")
    
    cuts = load_cut_list(cuts_path)
    return {"cuts": cuts}


# 11) 정적 이미지 파일 서빙
@app.get("/static/image")
@app.head("/static/image")
def serve_image(
    work_dir: str,
    entity_set_name: str,
    relative_path: str
):
    """이미지 파일을 서빙하는 엔드포인트"""
    # 보안: 경로 탐색 공격 방지
    if ".." in relative_path:
        raise HTTPException(status_code=400, detail="Invalid path")
    
    # 경로 구성
    # relative_path가 video/로 시작하면 base_dir부터, 아니면 reference/images부터
    if relative_path.startswith("video/"):
        # video 경로는 entity_set_name 아래에 있음
        base_path = os.path.join(work_dir, entity_set_name)
        full_path = os.path.join(base_path, relative_path)
    else:
        # 레퍼런스 이미지는 reference/images 아래에 있음
        paths = derive_paths(work_dir, entity_set_name)
        reference_images_dir = paths["REFERENCE_IMAGES_DIR"]
        full_path = os.path.join(reference_images_dir, relative_path)
    
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail=f"Image not found: {full_path}")
    
    # 이미지 파일인지 확인
    if not full_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
        raise HTTPException(status_code=400, detail="Not an image file")
    
    # 적절한 MIME 타입 설정
    if full_path.lower().endswith('.png'):
        media_type = "image/png"
    elif full_path.lower().endswith('.jpg') or full_path.lower().endswith('.jpeg'):
        media_type = "image/jpeg"
    elif full_path.lower().endswith('.gif'):
        media_type = "image/gif"
    elif full_path.lower().endswith('.webp'):
        media_type = "image/webp"
    else:
        media_type = "image/png"
    
    return FileResponse(full_path, media_type=media_type)


# 12) 시놉시스 텍스트 로드
@app.get("/load-synopsis-text")
def load_synopsis_text(
    work_dir: str,
    entity_set_name: str
):
    paths = derive_paths(work_dir, entity_set_name)
    synopsis_path = os.path.join(paths["REFERENCE_PATH"], "synopsis_text.txt")
    
    if os.path.exists(synopsis_path):
        with open(synopsis_path, "r", encoding="utf-8") as f:
            return {"text": f.read()}
    return {"text": ""}


# 13) 스토리 텍스트 로드
@app.get("/load-story-text")
def load_story_text(
    work_dir: str,
    entity_set_name: str
):
    paths = derive_paths(work_dir, entity_set_name)
    story_path = os.path.join(paths["STORY_PATH"], "story_text.txt")
    synopsis_path = os.path.join(paths["REFERENCE_PATH"], "synopsis_text.txt")
    
    # 스토리 파일이 있으면 우선 반환
    if os.path.exists(story_path):
        with open(story_path, "r", encoding="utf-8") as f:
            return {"text": f.read(), "source": "story"}
    # 없으면 시놉시스 파일 반환
    elif os.path.exists(synopsis_path):
        with open(synopsis_path, "r", encoding="utf-8") as f:
            return {"text": f.read(), "source": "synopsis"}
    return {"text": "", "source": "none"}


# 14) 기존 프로젝트 목록 조회
@app.get("/list-projects")
def list_projects(work_dir: str):
    if not os.path.exists(work_dir):
        return {"projects": []}
    
    projects = []
    for item in os.listdir(work_dir):
        item_path = os.path.join(work_dir, item)
        # 디렉토리이고 reference 폴더가 있으면 프로젝트로 간주
        if os.path.isdir(item_path):
            reference_path = os.path.join(item_path, "reference")
            if os.path.exists(reference_path):
                projects.append(item)
    
    return {"projects": sorted(projects)}


# 15) 생성된 컷 이미지 목록 조회
@app.get("/load-cut-images")
def load_cut_images(work_dir: str, entity_set_name: str):
    paths = derive_paths(work_dir, entity_set_name)
    images_dir = paths["CUT_IMG_DIR"]  # 올바른 키 이름으로 수정
    
    if not os.path.exists(images_dir):
        return {"images": []}
    
    images = []
    for filename in sorted(os.listdir(images_dir)):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            # S01-C01 형식에서 씬/컷 번호 추출
            import re
            match = re.match(r"S(\d+)-C(\d+)", filename)
            if match:
                images.append({
                    "scene_num": int(match.group(1)),
                    "cut_num": int(match.group(2)),
                    "filename": filename,
                    "path": f"video/cut-images/{filename}"
                })
    
    return {"images": images}


# 16) 생성된 컷 영상 목록 조회
@app.get("/load-cut-videos")
def load_cut_videos(work_dir: str, entity_set_name: str):
    paths = derive_paths(work_dir, entity_set_name)
    videos_dir = paths["VIDEO_OUTPUT_DIR"]
    
    if not os.path.exists(videos_dir):
        return {"videos": []}
    
    videos = []
    for filename in sorted(os.listdir(videos_dir)):
        if filename.lower().endswith('.mp4'):
            # S01-C01 형식에서 씬/컷 번호 추출
            import re
            match = re.match(r"S(\d+)-C(\d+)", filename)
            if match:
                videos.append({
                    "scene_num": int(match.group(1)),
                    "cut_num": int(match.group(2)),
                    "filename": filename,
                    "path": f"video/output/{filename}"
                })
    
    return {"videos": videos}


# 17) 비디오 파일 서빙
@app.get("/static/video")
@app.head("/static/video")
def serve_video(work_dir: str, entity_set_name: str, relative_path: str, response: Response):
    """Serve video files"""
    video_path = os.path.join(work_dir, entity_set_name, relative_path)
    
    # Debug logging
    logger.info(f"Requested video path: {video_path}")
    logger.info(f"Decoded relative_path: {relative_path}")
    logger.info(f"File exists: {os.path.exists(video_path)}")
    
    if not os.path.exists(video_path):
        logger.error(f"Video not found at: {video_path}")
        raise HTTPException(status_code=404, detail=f"Video not found: {video_path}")
    
    # Add CORS headers
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, HEAD, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    
    return FileResponse(video_path, media_type="video/mp4")

# 18) 최종 비디오 파일 서빙 (파일명 없이 프로젝트로 접근)
@app.get("/final-video")
@app.head("/final-video")
def serve_final_video(work_dir: str, entity_set_name: str, response: Response):
    """Serve final concatenated video by project info only"""
    final_video_name = f"{entity_set_name}_concat_video.mp4"
    video_path = os.path.join(work_dir, entity_set_name, "video", final_video_name)
    
    # Debug logging
    logger.info(f"Final video path: {video_path}")
    logger.info(f"File exists: {os.path.exists(video_path)}")
    
    if not os.path.exists(video_path):
        logger.error(f"Final video not found at: {video_path}")
        raise HTTPException(status_code=404, detail=f"Final video not found")
    
    # Add CORS headers
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, HEAD, OPTIONS"  
    response.headers["Access-Control-Allow-Headers"] = "*"
    
    return FileResponse(video_path, media_type="video/mp4")


# 19) 서버 IP 주소 감지
@app.get("/server-info")
def get_server_info():
    """서버의 네트워크 정보 반환"""
    import socket
    import subprocess
    
    try:
        # 로컬 IP 주소 감지
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        
        # 대체 방법으로 ifconfig 사용
        try:
            result = subprocess.run(['ifconfig'], capture_output=True, text=True)
            ifconfig_output = result.stdout
        except:
            ifconfig_output = ""
        
        return {
            "local_ip": local_ip,
            "hostname": socket.gethostname(),
            "api_url": f"http://{local_ip}:8000",
            "debug_info": {
                "ifconfig": ifconfig_output[:1000] if ifconfig_output else "Not available"
            }
        }
    except Exception as e:
        return {
            "local_ip": "127.0.0.1",
            "hostname": "localhost",
            "api_url": "http://127.0.0.1:8000",
            "error": str(e)
        }


