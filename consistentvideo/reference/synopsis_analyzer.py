SYSTEM_PROMPT = """
파일에서 다음과 같은 형태로 정보 추출. (해당 정보가 없다면 임의로 설정해서 값을 할당해야 함.)
a. 인물: 이름, 연령대, 인종, 성별, 헤어 스타일, 헤어 컬러, 신장, 체중, 체형, 패션 스타일, 추가 특징
b. 장소: 장소명, 실내외, 공간 특징, 추가 설명
c. 사물: 크기, 색깔, 형체, 카테고리, 태그

스토리 상 중요하지 않은 인물, 장소, 사물은 '기타'로 정리.
다른 텍스트 없이, 다음의 예시와 같은 형태로 출력.

출력 예시
a. 인물
1. 김신 (도깨비)
이름: 김신 (도깨비)
연령대: 30~40대(외견상 불멸이지만 젊고 강인한 장군 이미지)
인종: 동아시아(한국인)
성별: 남성
헤어 스타일: 긴 듯 단정한 장발(고려 장군→도깨비, 현대엔 약간 웨이브된 단정한 머리)
헤어 컬러: 흑갈색
신장: 185cm(추정, 장군+불멸 존재로 위풍당당)
체중: 78kg(추정)
체형: 근육질의 균형잡힌 체형
패션 스타일: 고전(장군복, 비늘갑옷), 현대(고급 롱코트, 포멀룩)
추가 특징: 신비로운 분위기, 불멸자, 검이 몸에 박혀 있음

2. 삼신
이름: 삼신
연령대: 60~70대(노파로 위장)
인종: 동아시아(한국인)
성별: 여성
헤어 스타일: 흰색 할머니 파마머리(변장 시)
헤어 컬러: 백발
신장: 155cm(추정)
체중: 50kg(추정)
체형: 왜소, 노인 체형
패션 스타일: 할머니 재래시장 옷, 때로 신비로운 흰 옷
추가 특징: 신의 존재, 유머러스하면서도 신비로운 느낌

3. 저승사자
이름: 저승사자
연령대: 30대(명확치 않으나 젊은 남성 외견)
인종: 동아시아(한국인)
성별: 남성
헤어 스타일: 짧은 블랙 헤어, 앞머리가 살짝 있는 댄디컷
헤어 컬러: 검정색
신장: 182cm(추정)
체중: 74kg(추정)
체형: 마르고 긴 체형
패션 스타일: 검정 정장, 중절모
추가 특징: 창백한 얼굴, 무표정, 사후세계와 연결

4. 지은탁
이름: 지은탁
연령대: 10대 후반20대 초반(처음엔 아동청소년)
인종: 동아시아(한국인)
성별: 여성
헤어 스타일: 긴 생머리, 평범하고 자연스러운
헤어 컬러: 검정~초콜릿 브라운
신장: 162cm(추정)
체중: 48kg(추정)
체형: 날씬함
패션 스타일: 교복, 캐주얼, 따뜻한 니트 등
추가 특징: 미소, 투명하고 밝은 표정, 특별한 낙인(붉은 점), 영혼을 봄

5. 은탁모
이름: 은탁모
연령대: 30~40대(사망 당시 기준)
인종: 동아시아(한국인)
성별: 여성
헤어 스타일: 단정한 단발
헤어 컬러: 검정색
신장: 158cm(추정)
체중: 50kg(추정)
체형: 보통
패션 스타일: 평범한 가정주부 복장
추가 특징: 유령 상태, 모성애 강함

6. 유덕화
이름: 유덕화
연령대: 10대(중학생~고등학생)
인종: 동아시아(한국인)
성별: 남성
헤어 스타일: 단정한 짧은 머리
헤어 컬러: 검정
신장: 170cm(추정)
체중: 60kg(추정)
체형: 마름
패션 스타일: 학생복 혹은 캐주얼
추가 특징: 밝고 선량한 인상

7. 유회장
이름: 유회장
연령대: 70대
인종: 동아시아(한국인)
성별: 남성
헤어 스타일: 짧은 흰머리
헤어 컬러: 백발
신장: 170cm(추정)
체중: 65kg(추정)
체형: 노년 보통 체격
패션 스타일: 정장, 전통 한복
추가 특징: 충직함

기타:
소년: 입양아, 10세 내외, 동아시아, 남, 평범한 단발머리
왕: 10대 후반 ~ 20대 초반, 남, 동아시아, 곱게 다듬은 머리, 황금색 도포, 군주
간신: 40대 남성, 동아시아, 교활한 인상
손자: 10대, 남, 동아시아
금발남: 20대 초반, 백인, 남성, 금발 짧은 머리, 캐주얼 복장
수진, 고딩1: 10대 여학생들, 동아시아, 교복, 긴 생머리, 검정색 혹은 갈색 머리

b. 장소
장소 1
장소명: 메밀꽃 들판
실내외: 실외
공간 특징: 거대한 들판, 푸른 밤, 달빛, 검 꽂혀 있음
추가 설명: 신비로운 분위기, 나비 출몰, 운명적 장소

장소 2
장소명: 외국 거리/주택가
실내외: 실외
공간 특징: 이국적 풍경, 고급스러운 주택
추가 설명: 금발남, 입양 소년과의 만남, 따스한 햇살

장소3
장소명: 저승 찻집
실내외: 실내
공간 특징: 고풍스러운 찻집, 어스름한 조명, 차분
추가 설명: 저승사자가 망자를 인도

장소4
장소명: 고려 전쟁터
실내외: 실외
공간 특징: 피로 물든 대지, 깃발, 소란스러움
추가 설명: 장군 김신의 전투 장면

장소5
장소명: 고층 빌딩 옥상
실내외: 실외
공간 특징: 서울 시내 고층건물 옥상, 붉은 달, 강한 고독미
추가 설명: 도깨비의 고독, 운명적 상징
기타:
궁궐(실외/실내), 병원(실내), 고등학교(실내/외), 시장통(실외), 바닷가(실외), 도깨비 집(실내), 어린 은탁 집(실내), 서울 거리(실외) 등

c. 사물 정보
1. 검
크기: 1m 이상(장검, 도깨비 검)
색깔: 칼날은 은빛, 손잡이와 장식은 어두운 톤
형체: 고전적 화려한 양날검, 장식적
카테고리: 무기
태그: 불멸, 저주, 신비, 주인-신부-인연

2. 흰 나비
크기: 손바닥만 한 크기(가상, 실제보다 큼)
색깔: 순백
형체: 나비 형태
카테고리: 동물(상징)
태그: 신, 삼신, 부활, 운명

3. 옥반지
크기: 손가락 한 마디(반지)
색깔: 연옥색(밝은 초록)
형체: 원형 링
카테고리: 액세서리/장신구
태그: 연결, 삼신, 은탁, 인연

"""

import os
import json
from openai import OpenAI
from .synopsis_parser import parse_characters, parse_locations, parse_objects
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)


class SynopsisAnalyzer:
    def __init__(self, save_dir="first_results"):
        self.save_dir = save_dir
        # os.makedirs(self.save_dir, exist_ok=True)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        self.system_prompt = SYSTEM_PROMPT

    def analyze(self, synopsis_text: str) -> list:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": synopsis_text},
        ]

        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1", messages=messages, temperature=0.3
            )

            result_text = response.choices[0].message.content

            # Save to first_results/
            # base_name = os.path.splitext(os.path.basename(original_filename))[0]
            result_file = f"entity_draft.txt"
            os.makedirs(self.save_dir, exist_ok=True)
            result_path = os.path.join(self.save_dir, result_file)
            with open(result_path, "w", encoding="utf-8") as f:
                f.write(result_text)
            logger.info(f"시놉시스 1차 결과 저장: {result_path}")

            # Parse to structured list
            character_block = (
                result_text.split("b. 장소")[0].replace("a. 인물", "").strip()
            )
            location_block = result_text.split("b. 장소")[1].split("c. 사물")[0].strip()
            object_block = result_text.split("c. 사물")[-1].strip()

            characters = parse_characters(character_block)
            locations = parse_locations(location_block)
            objects = parse_objects(object_block)

            entities = []
            for item in characters + locations + objects:
                name = item.get("name", "")
                if item.get("type") == "character":
                    desc = json.dumps(item.get("attributes", {}), ensure_ascii=False)
                    entities.append(
                        {"type": "character", "name": name, "description": desc}
                    )
                elif item.get("type") == "location":
                    desc = json.dumps(item.get("attributes", {}), ensure_ascii=False)
                    entities.append(
                        {"type": "location", "name": name, "description": desc}
                    )
                elif item.get("type") == "object":
                    desc = json.dumps(item.get("attributes", {}), ensure_ascii=False)
                    entities.append(
                        {"type": "object", "name": name, "description": desc}
                    )

            # Save to entities_attribute/
            entity_path = os.path.join(self.save_dir, f"entity_dict_draft.json")
            with open(entity_path, "w", encoding="utf-8") as f:
                json.dump(entities, f, ensure_ascii=False, indent=2)
            logger.info(f"엔티티 임시 사전 저장: {entity_path}")

            return entities

        except Exception as e:
            logger.error(f"시놉시스 분석 실패: {e}")
            return []
