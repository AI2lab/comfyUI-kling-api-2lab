from .kling import Kolors_virtual_try_on,Kolors_image,Kling_text2video_preset_camara_control,Kling_text2video_custom_camara_control,Kling_text2video,Kling_image2video

# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    Kolors_image.NAME: Kolors_image,
    Kling_text2video.NAME: Kling_text2video,
    Kling_text2video_preset_camara_control.NAME: Kling_text2video_preset_camara_control,
    Kling_text2video_custom_camara_control.NAME: Kling_text2video_custom_camara_control,
    Kling_image2video.NAME: Kling_image2video,
    Kolors_virtual_try_on.NAME: Kolors_virtual_try_on,
}

# display name
NODE_DISPLAY_NAME_MAPPINGS = {
    Kolors_image.NAME: "Kolors image",
    Kling_text2video.NAME: "Kling text to video",
    Kling_text2video_preset_camara_control.NAME: "Kling text to video (preset camara control)",
    Kling_text2video_custom_camara_control.NAME: "Kling text to video (custom camara control)",
    Kling_image2video.NAME: "Kling image to video",
    Kolors_virtual_try_on.NAME: "Kolors virtual try on",
}

__all__ = [NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS]
