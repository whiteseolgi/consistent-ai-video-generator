from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import os
import json

from SynopsisAnalyzer import SynopsisAnalyzer
from EntityCreator import CharacterImageCreator, LocationImageCreator, ObjectImageCreator

app = FastAPI()

# 디렉토리 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# 클래스 인스턴스
analyzer = SynopsisAnalyzer()
character_creator = CharacterImageCreator()
location_creator = LocationImageCreator()
object_creator = ObjectImageCreator()

@app.post("/analyze")
async def analyze_synopsis(file: UploadFile = File(...)):
    if not file.filename.endswith(".json"):
        return JSONResponse(status_code=400, content={"error": "Only .json files are supported."})

    try:
        # 1. 업로드 파일 저장
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())

         # 2. JSON → 문자열로 변환
        with open(file_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        synopsis_text = json.dumps(json_data, ensure_ascii=False, indent=2)

        # 3. 시놉시스 분석 및 파싱
        base_name = os.path.splitext(file.filename)[0]
        entity_list = analyzer.analyze(synopsis_text, original_filename=file.filename)

        # 4. Creator들에게 base 디렉토리 설정
        character_creator.set_base_dir(base_name)
        location_creator.set_base_dir(base_name)
        object_creator.set_base_dir(base_name)

        # 5. 이미지 생성 및 결과 수집
        results = []
        for entity in entity_list:
            type_ = entity.get("type")
            name = entity.get("name")
            description = entity.get("description")

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

            print(f"[RESULT] {result}")  # 터미널 출력
            results.append(result)

        return {
            "message": "분석 및 이미지 생성 완료",
            "entities": results
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"처리 중 오류 발생: {str(e)}"})
