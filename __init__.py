from .kling import Kolors_virtual_try_on

# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    # Kling_txt2vid.NAME: Kling_txt2vid,
    # Kling_img2vid.NAME: Kling_img2vid,
    Kolors_virtual_try_on.NAME: Kolors_virtual_try_on,
}

# display name
NODE_DISPLAY_NAME_MAPPINGS = {
    # Kling_txt2vid.NAME: "Kling text to video",
    # Kling_img2vid.NAME: "Kling image to video",
    Kolors_virtual_try_on.NAME: "Kolors virtual try on",
}

__all__ = [NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS]
