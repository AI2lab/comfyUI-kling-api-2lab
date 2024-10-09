import os
import json
import traceback
import time
import jwt
import requests
from .constants import get_project_category, get_project_name, project_root,comfy_root
from PIL import Image
import base64
import io

kling_api_url = 'https://api.klingai.com'

output_folder = os.path.join(comfy_root, 'output')
configFile = os.path.join(project_root, 'config.json')
with open(configFile, 'r') as file:
    data = file.read()
json_data = json.loads(data)
ACCESS_KEY = json_data["ACCESS_KEY"]
SECRET_KEY = json_data["SECRET_KEY"]

NODE_CATEGORY = get_project_category("klingai")

class Kolors_image:
    NAME = get_project_name('Kolors_image')
    CATEGORY = NODE_CATEGORY
    RETURN_TYPES = ("LIST",)
    RETURN_NAMES = ("image_urls",)
    FUNCTION = "doWork"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": (["kling-v1"], {"default": "kling-v1"}),
                "prompt": ("STRING", {"multiline": True}),
                "negative_prompt": ("STRING", {"multiline": True}),
                "aspect_ratio": (["1:1", "2:3", "3:2", "3:4", "4:3", "9:16", "16:9"], {"default": "1:1"}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 9}),
            },
            "optional": {
                "ref_image_path": ("STRING", {"multiline": False}),
                "image_fidelity": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0}),
            }
        }

    def doWork(self,  model, prompt, negative_prompt, aspect_ratio, batch_size, ref_image_path=None, image_fidelity=None):
        api_token = encode_jwt_token(ACCESS_KEY, SECRET_KEY)

        submitUrl = f"{kling_api_url}/v1/images/generations"
        headers = {
            'content-type': 'application/json;charset=utf-8',
            'Authorization': f'Bearer {api_token}'
        }
        data = {
            "model":model,
            "prompt":prompt,
            "negative_prompt":negative_prompt,
            "n":batch_size,
            "aspect_ratio":aspect_ratio
        }
        if ref_image_path!=None and ref_image_path!="":
            if not os.path.exists(ref_image_path):
                raise Exception(f"ref_image_path not exist : {ref_image_path} ")
            ref_image = load_image_to_base64(ref_image_path)
            data["ref_image"] = ref_image
            data["image_fidelity"] = image_fidelity

        image_urls = []
        try:
            response = requests.post(submitUrl, headers=headers, json=data)
            print(response.text)

            responseJson = json.loads(response.text)
            # print(factxResponse)
            if 'code' not in responseJson:
                print(f"call kling api fail : {response.text}")
            elif responseJson['code']!=0:
                task_id = responseJson['data']['task_id']
                print(f"task {task_id} fail : {response.text}")
            else:
                task_id = responseJson['data']['task_id']
                count = 0
                while count<200:
                    print(f"waiting for result, count = {count}")
                    resultUrl = f"{kling_api_url}/v1/images/generations/{task_id}"
                    responseTask = requests.get(resultUrl, headers=headers)
                    responseJsonTask = json.loads(responseTask.text)
                    print(responseJsonTask)
                    if 'code' not in responseJsonTask:
                        print(f"task {task_id} fail : {response.text}")
                    elif responseJsonTask['code']!=0:
                        print(f"task {task_id} fail : {response.text}")
                    elif responseJsonTask['data']['task_status'] == "succeed":
                        images_result_list = responseJsonTask['data']['task_result']['images']
                        for images_result in images_result_list:
                            url = images_result['url']
                            image_urls.append(url)
                        break
                    elif responseJsonTask['data']['task_status']=="submitted" or responseJsonTask['data']['task_status']=="processing":
                        pass
                    else:
                        print(f"task {task_id} fail : {response.text}")
                        break

                    if count<60:
                        time.sleep(1)
                    else:
                        time.sleep(5)
                    count += 1

        except:
            print(traceback.format_exc())
        return (image_urls,)

class Kling_text2video:
    NAME = get_project_name('Kling_text2video')
    CATEGORY = NODE_CATEGORY
    RETURN_TYPES = ("LIST",)
    RETURN_NAMES = ("video_urls",)
    FUNCTION = "doWork"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": (["kling-v1"], {"default": "kling-v1"}),
                "prompt": ("STRING", {"multiline": True}),
                "negative_prompt": ("STRING", {"multiline": True}),
                "cfg_scale": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0}),
                "mode": (["std","pro"], {"default": "std"}),
                "aspect_ratio": (["1:1", "2:3", "3:2", "3:4", "4:3", "9:16", "16:9"], {"default": "1:1"}),
                "duration": ([5,10], {"default": 5}),
            }
        }

    def doWork(self,  model, prompt, negative_prompt,cfg_scale,mode, aspect_ratio, duration):
        api_token = encode_jwt_token(ACCESS_KEY, SECRET_KEY)

        submitUrl = f"{kling_api_url}/v1/videos/text2video"
        headers = {
            'content-type': 'application/json;charset=utf-8',
            'Authorization': f'Bearer {api_token}'
        }
        data = {
            "model":model,
            "prompt":prompt,
            "negative_prompt":negative_prompt,
            "cfg_scale":cfg_scale,
            "mode":mode,
            "aspect_ratio":aspect_ratio,
            "duration":duration
        }

        video_urls = []
        try:
            response = requests.post(submitUrl, headers=headers, json=data)
            print(response.text)

            responseJson = json.loads(response.text)
            print(responseJson)
            if 'code' not in responseJson:
                print(f"call kling api fail : {response.text}")
            elif responseJson['code']!=0:
                task_id = responseJson['data']['task_id']
                print(f"task {task_id} fail : {response.text}")
            else:
                task_id = responseJson['data']['task_id']
                count = 0
                while count<200:
                    print(f"waiting for result, count = {count}")
                    resultUrl = f"{kling_api_url}/v1/videos/text2video/{task_id}"
                    responseTask = requests.get(resultUrl, headers=headers)
                    responseJsonTask = json.loads(responseTask.text)
                    print(responseJsonTask)
                    if 'code' not in responseJsonTask:
                        print(f"task {task_id} fail : {response.text}")
                    elif responseJsonTask['code']!=0:
                        print(f"task {task_id} fail : {response.text}")
                    elif responseJsonTask['data']['task_status'] == "succeed":
                        videos_result_list = responseJsonTask['data']['task_result']['videos']
                        for videos_result in videos_result_list:
                            url = videos_result['url']
                            video_urls.append(url)
                        break
                    elif responseJsonTask['data']['task_status']=="submitted" or responseJsonTask['data']['task_status']=="processing":
                        pass
                    else:
                        print(f"task {task_id} fail : {response.text}")
                        break

                    if count<90:
                        time.sleep(2)
                    else:
                        time.sleep(5)
                    count += 1

        except:
            print(traceback.format_exc())
        return (video_urls,)

class Kling_text2video_preset_camara_control:
    NAME = get_project_name('Kling_text2video_preset_camara_control')
    CATEGORY = NODE_CATEGORY
    RETURN_TYPES = ("LIST",)
    RETURN_NAMES = ("video_urls",)
    FUNCTION = "doWork"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": (["kling-v1"], {"default": "kling-v1"}),
                "prompt": ("STRING", {"multiline": True}),
                "negative_prompt": ("STRING", {"multiline": True}),
                "cfg_scale": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0}),
                "mode": (["std"], {"default": "std"}),
                "aspect_ratio": (["1:1", "2:3", "3:2", "3:4", "4:3", "9:16", "16:9"], {"default": "1:1"}),
                "duration": ([5], {"default": 5}),
                "camera_control_type":(["down_back", "forward_up", "right_turn_forward", "left_turn_forward"],)
            }
        }

    def doWork(self,  model, prompt, negative_prompt,cfg_scale,mode, aspect_ratio, duration,camera_control_type):
        api_token = encode_jwt_token(ACCESS_KEY, SECRET_KEY)

        submitUrl = f"{kling_api_url}/v1/videos/text2video"
        headers = {
            'content-type': 'application/json;charset=utf-8',
            'Authorization': f'Bearer {api_token}'
        }
        camera_control = {
            "type":camera_control_type,
        }
        data = {
            "model":model,
            "prompt":prompt,
            "negative_prompt":negative_prompt,
            "cfg_scale":cfg_scale,
            "mode":mode,
            "aspect_ratio":aspect_ratio,
            "duration":duration,
            "camera_control":camera_control
        }

        video_urls = []
        try:
            response = requests.post(submitUrl, headers=headers, json=data)
            print(response.text)

            responseJson = json.loads(response.text)
            print(responseJson)
            if 'code' not in responseJson:
                print(f"call kling api fail : {response.text}")
            elif responseJson['code']!=0:
                task_id = responseJson['data']['task_id']
                print(f"task {task_id} fail : {response.text}")
            else:
                task_id = responseJson['data']['task_id']
                count = 0
                while count<200:
                    print(f"waiting for result, count = {count}")
                    resultUrl = f"{kling_api_url}/v1/videos/text2video/{task_id}"
                    responseTask = requests.get(resultUrl, headers=headers)
                    responseJsonTask = json.loads(responseTask.text)
                    print(responseJsonTask)
                    if 'code' not in responseJsonTask:
                        print(f"task {task_id} fail : {response.text}")
                    elif responseJsonTask['code']!=0:
                        print(f"task {task_id} fail : {response.text}")
                    elif responseJsonTask['data']['task_status'] == "succeed":
                        videos_result_list = responseJsonTask['data']['task_result']['videos']
                        for videos_result in videos_result_list:
                            url = videos_result['url']
                            video_urls.append(url)
                        break
                    elif responseJsonTask['data']['task_status']=="submitted" or responseJsonTask['data']['task_status']=="processing":
                        pass
                    else:
                        print(f"task {task_id} fail : {response.text}")
                        break

                    if count<90:
                        time.sleep(2)
                    else:
                        time.sleep(5)
                    count += 1

        except:
            print(traceback.format_exc())
        return (video_urls,)

class Kling_text2video_custom_camara_control:
    NAME = get_project_name('Kling_text2video_custom_camara_control')
    CATEGORY = NODE_CATEGORY
    RETURN_TYPES = ("LIST",)
    RETURN_NAMES = ("video_urls",)
    FUNCTION = "doWork"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": (["kling-v1"], {"default": "kling-v1"}),
                "prompt": ("STRING", {"multiline": True}),
                "negative_prompt": ("STRING", {"multiline": True}),
                "cfg_scale": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0}),
                "mode": (["std"], {"default": "std"}),
                "aspect_ratio": (["1:1", "2:3", "3:2", "3:4", "4:3", "9:16", "16:9"], {"default": "1:1"}),
                "duration": ([5], {"default": 5}),
                "camera_control_type":(["simple"],),
                "camera_control_direction":(["horizontal","vertical","pan","tilt","roll","zoom"], {"default": "horizontal"}),
                "camera_control_range": ("FLOAT", {"default": 0, "min": -10.0, "max": 10.0}),
            }
        }

    def doWork(self,  model, prompt, negative_prompt,cfg_scale,mode, aspect_ratio, duration,camera_control_type,camera_control_direction,camera_control_range):
        api_token = encode_jwt_token(ACCESS_KEY, SECRET_KEY)

        submitUrl = f"{kling_api_url}/v1/videos/text2video"
        headers = {
            'content-type': 'application/json;charset=utf-8',
            'Authorization': f'Bearer {api_token}'
        }
        camera_control_config={}
        camera_control_config[camera_control_direction] = camera_control_range
        camera_control = {
            "type":camera_control_type,
            "config":camera_control_config
        }
        data = {
            "model":model,
            "prompt":prompt,
            "negative_prompt":negative_prompt,
            "cfg_scale":cfg_scale,
            "mode":mode,
            "aspect_ratio":aspect_ratio,
            "duration":duration,
            "camera_control":camera_control
        }

        video_urls = []
        try:
            response = requests.post(submitUrl, headers=headers, json=data)
            print(response.text)

            responseJson = json.loads(response.text)
            print(responseJson)
            if 'code' not in responseJson:
                print(f"call kling api fail : {response.text}")
            elif responseJson['code']!=0:
                task_id = responseJson['data']['task_id']
                print(f"task {task_id} fail : {response.text}")
            else:
                task_id = responseJson['data']['task_id']
                count = 0
                while count<200:
                    print(f"waiting for result, count = {count}")
                    resultUrl = f"{kling_api_url}/v1/videos/text2video/{task_id}"
                    responseTask = requests.get(resultUrl, headers=headers)
                    responseJsonTask = json.loads(responseTask.text)
                    print(responseJsonTask)
                    if 'code' not in responseJsonTask:
                        print(f"task {task_id} fail : {response.text}")
                    elif responseJsonTask['code']!=0:
                        print(f"task {task_id} fail : {response.text}")
                    elif responseJsonTask['data']['task_status'] == "succeed":
                        videos_result_list = responseJsonTask['data']['task_result']['videos']
                        for videos_result in videos_result_list:
                            url = videos_result['url']
                            video_urls.append(url)
                        break
                    elif responseJsonTask['data']['task_status']=="submitted" or responseJsonTask['data']['task_status']=="processing":
                        pass
                    else:
                        print(f"task {task_id} fail : {response.text}")
                        break

                    if count<90:
                        time.sleep(2)
                    else:
                        time.sleep(5)
                    count += 1

        except:
            print(traceback.format_exc())
        return (video_urls,)

class Kling_image2video:
    NAME = get_project_name('Kling_image2video')
    CATEGORY = NODE_CATEGORY
    RETURN_TYPES = ("LIST",)
    RETURN_NAMES = ("video_urls",)
    FUNCTION = "doWork"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": (["kling-v1"], {"default": "kling-v1"}),
                "ref_image_path": ("STRING", {"multiline": False}),
                "prompt": ("STRING", {"multiline": True}),
                "negative_prompt": ("STRING", {"multiline": True}),
                "cfg_scale": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0}),
                "mode": (["std","pro"], {"default": "std"}),
                "duration": ([5,10], {"default": 5}),
            },
            "optional":{
                "ref_tail_image_path": ("STRING", {"multiline": False}),
            }
        }

    def doWork(self,  model,ref_image_path, prompt, negative_prompt,cfg_scale,mode, duration,ref_tail_image_path=None):
        ref_image = load_image_to_base64(ref_image_path)

        api_token = encode_jwt_token(ACCESS_KEY, SECRET_KEY)

        submitUrl = f"{kling_api_url}/v1/videos/image2video"
        headers = {
            'content-type': 'application/json;charset=utf-8',
            'Authorization': f'Bearer {api_token}'
        }
        data = {
            "model":model,
            "image":ref_image,
            "prompt":prompt,
            "negative_prompt":negative_prompt,
            "cfg_scale":cfg_scale,
            "mode":mode,
            "duration":duration
        }
        if ref_tail_image_path is not None and ref_tail_image_path!='':
            ref_tail_image = load_image_to_base64(ref_tail_image_path)
            data["image_tail"] = ref_tail_image

        video_urls = []
        try:
            response = requests.post(submitUrl, headers=headers, json=data)
            print(response.text)

            responseJson = json.loads(response.text)
            print(responseJson)
            if 'code' not in responseJson:
                print(f"call kling api fail : {response.text}")
            elif responseJson['code']!=0:
                task_id = responseJson['data']['task_id']
                print(f"task {task_id} fail : {response.text}")
            else:
                task_id = responseJson['data']['task_id']
                count = 0
                while count<200:
                    print(f"waiting for result, count = {count}")
                    resultUrl = f"{kling_api_url}/v1/videos/image2video/{task_id}"
                    responseTask = requests.get(resultUrl, headers=headers)
                    responseJsonTask = json.loads(responseTask.text)
                    print(responseJsonTask)
                    if 'code' not in responseJsonTask:
                        print(f"task {task_id} fail : {response.text}")
                    elif responseJsonTask['code']!=0:
                        print(f"task {task_id} fail : {response.text}")
                    elif responseJsonTask['data']['task_status'] == "succeed":
                        videos_result_list = responseJsonTask['data']['task_result']['videos']
                        for videos_result in videos_result_list:
                            url = videos_result['url']
                            video_urls.append(url)
                        break
                    elif responseJsonTask['data']['task_status']=="submitted" or responseJsonTask['data']['task_status']=="processing":
                        pass
                    else:
                        print(f"task {task_id} fail : {response.text}")
                        break

                    if count<90:
                        time.sleep(2)
                    else:
                        time.sleep(5)
                    count += 1

        except:
            print(traceback.format_exc())
        return (video_urls,)

class Kolors_virtual_try_on:
    NAME = get_project_name('Kolors_virtual_try_on')
    CATEGORY = NODE_CATEGORY
    RETURN_TYPES = ("LIST",)
    RETURN_NAMES = ("image_urls",)
    FUNCTION = "doWork"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "human_image_path": ("STRING", {"multiline": False}),
                "cloth_image_path": ("STRING", {"multiline": False})
            },
        }

    def doWork(self,  human_image_path, cloth_image_path):
        human_image = load_image_to_base64(human_image_path)
        cloth_image = load_image_to_base64(cloth_image_path)

        api_token = encode_jwt_token(ACCESS_KEY, SECRET_KEY)

        submitUrl = f"{kling_api_url}/v1/images/kolors-virtual-try-on"
        headers = {
            'content-type': 'application/json;charset=utf-8',
            'Authorization': f'Bearer {api_token}'
        }
        data = {
            "model_name":"kolors-virtual-try-on-v1",
            "human_image":human_image,
            "cloth_image":cloth_image,
        }
        image_urls = []
        try:
            response = requests.post(submitUrl, headers=headers, json=data)
            print(response.text)

            responseJson = json.loads(response.text)
            # print(factxResponse)
            if 'code' not in responseJson:
                print(f"call kling api fail : {response.text}")
            elif responseJson['code']!=0:
                task_id = responseJson['data']['task_id']
                print(f"task {task_id} fail : {response.text}")
            else:
                task_id = responseJson['data']['task_id']
                count = 0
                while count<200:
                    print(f"waiting for result, count = {count}")
                    resultUrl = f"{kling_api_url}/v1/images/kolors-virtual-try-on/{task_id}"
                    responseTask = requests.get(resultUrl, headers=headers)
                    responseJsonTask = json.loads(responseTask.text)
                    print(responseJsonTask)
                    if 'code' not in responseJsonTask:
                        print(f"task {task_id} fail : {response.text}")
                    elif responseJsonTask['code']!=0:
                        print(f"task {task_id} fail : {response.text}")
                    elif responseJsonTask['data']['task_status'] == "succeed":
                        images_result_list = responseJsonTask['data']['task_result']['images']
                        for images_result in images_result_list:
                            url = images_result['url']
                            image_urls.append(url)
                        break
                    elif responseJsonTask['data']['task_status']=="submitted" or responseJsonTask['data']['task_status']=="processing":
                        pass
                    else:
                        print(f"task {task_id} fail : {response.text}")
                        break

                    if count<60:
                        time.sleep(1)
                    else:
                        time.sleep(5)
                    count += 1
        except:
            print(traceback.format_exc())
        return (image_urls,)

def encode_jwt_token(ak, sk):
    headers = {
        "alg": "HS256",
        "typ": "JWT"
    }
    payload = {
        "iss": ak,
        "exp": int(time.time()) + 1800, # 有效时间，此处示例代表当前时间+1800s(30min)
        "nbf": int(time.time()) - 5 # 开始生效的时间，此处示例代表当前时间-5秒
    }
    token = jwt.encode(payload, sk, headers=headers)
    return token

def load_image_to_base64(image_path:str)->str:
    # 打开图片
    with Image.open(image_path) as img:
        # 将图片转换为RGB模式（如果需要）
        if img.mode != "RGB":
            img = img.convert("RGB")

        # 将图片保存到内存中的字节流
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")  # 你可以根据需要更改格式，如PNG

        # 获取字节流中的数据
        img_byte = buffered.getvalue()

        # 将字节数据编码为Base64字符串
        img_base64 = base64.b64encode(img_byte).decode('utf-8')

        return img_base64

