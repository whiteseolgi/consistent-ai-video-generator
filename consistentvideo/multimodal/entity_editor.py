import os
import base64
import json
from typing import List, Tuple, Optional, Dict, Any
import logging

from openai import OpenAI

from consistentvideo.reference.entity_creator import (
    CharacterImageCreator,
    LocationImageCreator,
    ObjectImageCreator,
)


EntityTuple = Tuple[str, str, str, Optional[str]]


class EntityMultimodalEditor:
    """
    엔티티 리스트에서 항목을 선택해 수정하거나, 새로 추가할 수 있는 편집기.
    - 이미지가 제공되면 gpt-4.1으로 이미지를 분석해 설명(description)을 갱신
    - 부가 프롬프트를 입력받아 설명에 반영
    - 갱신/추가된 엔티티는 gpt-image-1로 레퍼런스 이미지를 재생성
    """

    def __init__(self, entity_image_base_dir: str, *, text_model: str = "gpt-4.1", image_model: str = "gpt-image-1", image_style: str = "realistic", image_quality: str = "low", image_size: str = "1024x1024"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.entity_image_base_dir = entity_image_base_dir
        self.text_model = text_model
        self.image_model = image_model
        self.image_style = image_style
        self.image_quality = image_quality
        self.image_size = image_size
        self.aspect_ratio = "1:1"

        self.character_creator = CharacterImageCreator()
        self.location_creator = LocationImageCreator()
        self.object_creator = ObjectImageCreator()

        self.character_creator.set_base_dir(entity_image_base_dir)
        self.location_creator.set_base_dir(entity_image_base_dir)
        self.object_creator.set_base_dir(entity_image_base_dir)
        
        # 이미지 모델 설정
        self.character_creator.set_image_model(image_model)
        self.location_creator.set_image_model(image_model)
        self.object_creator.set_image_model(image_model)
        
        # 스타일, 품질, 크기 설정
        self.character_creator.set_style(image_style)
        self.location_creator.set_style(image_style)
        self.object_creator.set_style(image_style)
        
        self.character_creator.set_image_quality(image_quality)
        self.location_creator.set_image_quality(image_quality)
        self.object_creator.set_image_quality(image_quality)
        
        self.character_creator.set_image_size(image_size)
        self.location_creator.set_image_size(image_size)
        self.object_creator.set_image_size(image_size)
        
        # Gemini 모델인 경우 aspect ratio 설정
        if image_model == "gemini-2.5-flash-imag(Nano Banana)":
            self.character_creator.set_aspect_ratio(self.aspect_ratio)
            self.location_creator.set_aspect_ratio(self.aspect_ratio)
            self.object_creator.set_aspect_ratio(self.aspect_ratio)
    
    def set_aspect_ratio(self, ratio: str):
        """Gemini 모델용 aspect ratio 설정"""
        self.aspect_ratio = ratio
        self.character_creator.set_aspect_ratio(ratio)
        self.location_creator.set_aspect_ratio(ratio)
        self.object_creator.set_aspect_ratio(ratio)

    def _analyze_image_with_gpt_4_1(self, image_path: str, system_prompt: Optional[str] = None, context_text: Optional[str] = None) -> str:
        if not image_path or not os.path.exists(image_path):
            return ""

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        system_prompt = system_prompt or (
            "You are an expert computer vision assistant. Analyze the given image and return a concise, factual description in Korean."
        )

        # data URL 형태로 이미지 전달
        data_url = f"data:image/png;base64,{image_b64}"

        response = self.client.chat.completions.create(
            model=self.text_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": (
                            "이미지를 분석해 인물/장소/오브젝트의 특징을 한국어로 간단히 기술해 주세요." + (
                                f"\n참고 텍스트:\n{context_text}" if context_text else ""
                            )
                        )},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                },
            ],
            temperature=0.2,
        )

        return response.choices[0].message.content.strip()

    def _synthesize_structured_description(
        self,
        type_: str,
        existing_description: Optional[str],
        image_analysis: Optional[str],
        extra_prompt: Optional[str],
        user_hint: Optional[str] = None,
    ) -> str:
        """
        synopsis_analyzer.py가 생성하는 형태의 구조화된 description(JSON 문자열)로 변환.
        - character: 연령대/인종/성별/헤어 스타일/헤어 컬러/신장/체중/체형/패션 스타일/추가 특징
        - location: 실내외/공간 특징/추가 설명
        - object: 크기/색깔/형체/카테고리/태그
        """
        schema_instruction = {
            "character": (
                "다음 키만 포함된 JSON을 출력: 연령대, 인종, 성별, 헤어 스타일, 헤어 컬러, 신장, 체중, 체형, 패션 스타일, 추가 특징"
            ),
            "location": (
                "다음 키만 포함된 JSON을 출력: 실내외, 공간 특징, 추가 설명"
            ),
            "object": (
                "다음 키만 포함된 JSON을 출력: 크기, 색깔, 형체, 카테고리, 태그"
            ),
        }.get(type_, "그럴듯한 키로 JSON을 출력")

        system_prompt = (
            "You are a precise information structuring assistant. "
            "Return ONLY a JSON object in Korean with the requested keys, no markdown, no extra commentary."
        )

        context_parts = []
        if existing_description:
            context_parts.append(f"기존 설명: {existing_description}")
        if image_analysis:
            context_parts.append(f"이미지 분석: {image_analysis}")
        if extra_prompt:
            context_parts.append(f"추가 프롬프트: {extra_prompt}")
        if user_hint:
            context_parts.append(f"사용자 힌트: {user_hint}")

        user_content = (
            f"엔티티 타입: {type_}. {schema_instruction}.\n" + "\n".join(context_parts)
        )

        try:
            response = self.client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                temperature=0.1,
            )
            text = response.choices[0].message.content.strip()
            # JSON 검증 후 문자열로 반환
            try:
                data = json.loads(text)
                return json.dumps(data, ensure_ascii=False)
            except Exception:
                # JSON으로 파싱되지 않으면 그대로 반환
                return text
        except Exception:
            # 완전 실패 시 기존 설명 폴백
            return existing_description or ""

    def _regenerate_reference_image(self, type_: str, name: str, description: str, reference_image_path: Optional[str] = None) -> Optional[str]:
        if type_ == "character":
            self.character_creator.set_image_model(self.image_model)
            self.character_creator.set_style(self.image_style)
            self.character_creator.set_image_quality(self.image_quality)
            self.character_creator.set_image_size(self.image_size)
            return self.character_creator.create(type_, name, description, reference_image_path=reference_image_path)[3]
        if type_ == "location":
            self.location_creator.set_image_model(self.image_model)
            self.location_creator.set_style(self.image_style)
            self.location_creator.set_image_quality(self.image_quality)
            self.location_creator.set_image_size(self.image_size)
            return self.location_creator.create(type_, name, description, reference_image_path=reference_image_path)[3]
        if type_ == "object":
            self.object_creator.set_image_model(self.image_model)
            self.object_creator.set_style(self.image_style)
            self.object_creator.set_image_quality(self.image_quality)
            self.object_creator.set_image_size(self.image_size)
            return self.object_creator.create(type_, name, description, reference_image_path=reference_image_path)[3]
        return None

    def edit_entity(
        self,
        entity_list: List[EntityTuple],
        index: int,
        *,
        new_name: Optional[str] = None,
        new_description: Optional[str] = None,
        image_path: Optional[str] = None,
        extra_prompt: Optional[str] = None,
    ) -> EntityTuple:
        type_, name, description, image = entity_list[index]

        context_text = "\n".join(
            [
                f"기존 description: {description}" if description else "",
                f"사용자 새 설명 힌트: {new_description}" if new_description else "",
                f"추가 프롬프트: {extra_prompt}" if extra_prompt else "",
            ]
        ).strip()

        analyzed_desc = self._analyze_image_with_gpt_4_1(image_path, context_text=context_text) if image_path else ""

        # 최종 description은 synopsis_analyzer의 구조(JSON 문자열)로 '덮어쓰기'
        final_description = self._synthesize_structured_description(
            type_, existing_description=description, image_analysis=analyzed_desc, extra_prompt=extra_prompt, user_hint=new_description
        ) or description

        final_name = new_name or name

        new_image_filename = self._regenerate_reference_image(type_, final_name, final_description, reference_image_path=image_path)
        if not new_image_filename:
            logging.getLogger(__name__).warning("[Multimodal] 이미지 재생성 실패로 엔티티 편집을 적용하지 않습니다 (index=%s, name=%s)", index, name)
            # 업데이트하지 않고 원본 유지
            return (type_, name, description, image)

        return (type_, final_name, final_description, new_image_filename)

    def add_entity(
        self,
        entity_list: List[EntityTuple],
        *,
        type_: str,
        name: str,
        description: Optional[str] = None,
        image_path: Optional[str] = None,
        extra_prompt: Optional[str] = None,
    ) -> EntityTuple:
        context_text = "\n".join(
            [
                f"기존 description: {description}" if description else "",
                f"추가 프롬프트: {extra_prompt}" if extra_prompt else "",
            ]
        ).strip()

        analyzed_desc = self._analyze_image_with_gpt_4_1(image_path, context_text=context_text) if image_path else ""

        # 최종 description은 synopsis_analyzer의 구조(JSON 문자열)로 '덮어쓰기'
        final_description = self._synthesize_structured_description(
            type_, existing_description=description or "", image_analysis=analyzed_desc, extra_prompt=extra_prompt, user_hint=None
        )

        new_image_filename = self._regenerate_reference_image(type_, name, final_description, reference_image_path=image_path)
        if not new_image_filename:
            logging.getLogger(__name__).warning("[Multimodal] 이미지 생성 실패로 엔티티 추가를 건너뜁니다 (name=%s)", name)
            # 생성 실패 시 호출자에서 append하지 않도록 이미지 None으로 표시
            return (type_, name, final_description, None)

        return (type_, name, final_description, new_image_filename)

    @staticmethod
    def save_entity_list(file_path: str, entity_list: List[EntityTuple]) -> None:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            for entity in entity_list:
                f.write(str(entity) + "\n")


def edit_or_add_entity(
    entity_list: List[EntityTuple],
    *,
    operation: str,  # "edit" | "add"
    editor: EntityMultimodalEditor,
    index: Optional[int] = None,
    type_: Optional[str] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    image_path: Optional[str] = None,
    extra_prompt: Optional[str] = None,
) -> List[EntityTuple]:
    updated = list(entity_list)

    if operation == "edit":
        if index is None:
            raise ValueError("index is required for edit operation")
        updated[index] = editor.edit_entity(
            updated, index,
            new_name=name,
            new_description=description,
            image_path=image_path,
            extra_prompt=extra_prompt,
        )
    elif operation == "add":
        if not (type_ and name):
            raise ValueError("type_ and name are required for add operation")
        new_entity = editor.add_entity(
            updated,
            type_=type_,
            name=name,
            description=description,
            image_path=image_path,
            extra_prompt=extra_prompt,
        )
        # 이미지 생성 실패 시(파일명이 None) 추가하지 않음
        if new_entity[3] is None:
            logging.getLogger(__name__).warning("[Multimodal] 이미지 생성 실패로 엔티티 추가를 반영하지 않습니다 (name=%s)", name)
        else:
            updated.append(new_entity)
    else:
        raise ValueError("operation must be 'edit' or 'add'")

    return updated


