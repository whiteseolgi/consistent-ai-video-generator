from model_selector import MultiModalLoaderModelSelector
from base import EntityReconstructorBase
from ..video.model_selector import CutImageGeneratorModelSelector
import os

class EntityReconstructor(EntityReconstructorBase):
    '''
    multi_modal_data = 멀티모달 데이터
    entity_image_directory_path = 엔티티 이미지 디렉토리 경로
    '''
    def __init__(self, multi_modal_data : str = None, entity_image_directory_path : str = None):
        super.__init__(multi_modal_data = multi_modal_data, entity_image_directory_path = entity_image_directory_path)

    def execute(self):
        if not super.multi_modal_data:
            raise ValueError("Multi-modal data doesn't exist")
        
        entity_reconstructor_model = MultiModalLoaderModelSelector().call_MultiModalLoader_ai(
            ai_model="gpt-4.1", 
            prompt_text=super.multi_modal_data,
            prompt_images=super.entity_image_directory_path
            )
        
        
        new_entity_list = entity_reconstructor_model.execute()  # 새로운 엔티티 리스트 반환

        for i, entity in enumerate(new_entity_list):
            entity_type, entity_name, json_attr, image_name = entity

            prompt = None
            if entity_name == "기타":
                continue
            elif entity_type == "character":
                prompt = f"""A hyper-realistic front-facing portrait of a person, studio lighting, no background.
                            Name: {entity_name}, Description: {json_attr}.
                            Photographic realism. No illustration or cartoon style. Do not include any background."""
            elif entity_type == "location":
                prompt = f"""A realistic photo of a location, wide-angle shot, natural lighting, no people.
                            Location: {entity_name}, Features: {json_attr}.
                            Cinematic realism, urban or natural environment as appropriate. Do not include any people."""
            elif entity_type == "object":
                prompt = f"""A high-resolution photograph of a real-world object, no background.
                            Object: {entity_name}, Features: {json_attr}.
                            Do not include any characters or scenes. No illustration, realistic lighting and texture."""
            else:
                continue

            prompt_image = os.path.join(super.entity_image_directory_path, image_name)

            entity_image_regenerator_model = CutImageGeneratorModelSelector().call_CutImageGenerator_ai(
                ai_model = "gpt-image-1", 
                prompt_text = prompt, 
                prompt_images = prompt_image
            )

            regenerated_entity_image = entity_image_regenerator_model.execute()

            name, ext = os.path.splitext(image_name)
            new_image_name = f"{name}_multi_modal_regenerated{ext}"
            save_path = os.path.join(super.entity_image_directory_path, new_image_name)
            regenerated_entity_image.save(save_path)

            new_entity_list[i] = (entity_type, entity_name, json_attr, new_image_name)

        return new_entity_list

