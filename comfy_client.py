import json
import requests
import sys
import os
import time

from config import load_config

# --- CONFIG ---
_cfg = load_config()
COMFY_HOST = _cfg["HOST"]
COMFY_PORT = _cfg["PORT"]
COMFY_URL = _cfg["COMFY_URL"]
OUTPUT_DIR = _cfg["OUTPUT_DIR"]
WORKFLOW_DIR = _cfg["WORKFLOW_DIR"]

WORKFLOW_MAP = {
    "gen_z": os.path.join(WORKFLOW_DIR, "image_z_image_turbo.json"),
    "qwen_edit": os.path.join(WORKFLOW_DIR, "qwen_image_edit_2511.json")
}

ORIENTATIONS = {
    "portrait": (720, 1280),
    "landscape": (1280, 720),
}

os.makedirs(OUTPUT_DIR, exist_ok=True)

TIMEOUT = 30
MAX_POLL = 150  # 150 * 2s = 5 min max wait

def upload_file(input_path):
    with open(input_path, 'rb') as f:
        files = {'image': f}
        res = requests.post(f"{COMFY_URL}/upload/image", files=files, timeout=TIMEOUT)
        return res.json()

def send_prompt(workflow_data):
    p = {"prompt": workflow_data}
    data = json.dumps(p).encode('utf-8')
    res = requests.post(f"{COMFY_URL}/prompt", data=data, timeout=TIMEOUT)
    return res.json()

def check_history(prompt_id):
    res = requests.get(f"{COMFY_URL}/history/{prompt_id}", timeout=TIMEOUT)
    return res.json()

def download_file(filename, subfolder, folder_type):
    url = f"{COMFY_URL}/view?filename={filename}&subfolder={subfolder}&type={folder_type}"
    res = requests.get(url, timeout=60)
    file_path = os.path.join(OUTPUT_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(res.content)
    return file_path

def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: python3 comfy_client.py <template_id> <prompt_text> [input_image_path] [portrait|landscape]"}))
        return

    template_id = sys.argv[1]
    prompt_text = sys.argv[2]
    extra_args = sys.argv[3:]

    # Parse orientation and input_image_path from extra args
    input_image_path = None
    width, height = ORIENTATIONS["portrait"]
    for arg in extra_args:
        if arg.lower() in ORIENTATIONS:
            width, height = ORIENTATIONS[arg.lower()]
        else:
            input_image_path = arg

    if template_id not in WORKFLOW_MAP:
        return

    with open(WORKFLOW_MAP[template_id], 'r') as f:
        workflow = json.load(f)

    # --- IMAGE UPLOAD & INJECTION (for workflows with LoadImage) ---
    if input_image_path:
        if os.path.exists(input_image_path):
            upload_res = upload_file(input_image_path)
            uploaded_filename = upload_res.get("name")
        else:
            uploaded_filename = input_image_path

        for node_id in workflow:
            node = workflow[node_id]
            if node.get("class_type") == "LoadImage":
                node["inputs"]["image"] = uploaded_filename

    # --- CHARACTER LOGIC (Node 52) ---
    prompt_lower = prompt_text.lower()
    
    if "52" in workflow:
        # Strict LoRA Injection: Only for specific characters
        if "mariclaw" in prompt_lower:
            workflow["52"]["inputs"]["lora_name"] = "Z-Image\\AvaClaw\\MariClaw-Z-Image-Turbo_lora_v1.safetensors"
            workflow["52"]["inputs"]["strength_model"] = 0.8
            workflow["52"]["inputs"]["strength_clip"] = 0.8
        elif "asukaclaw" in prompt_lower:
            workflow["52"]["inputs"]["lora_name"] = "Z-Image\\AvaClaw\\AsukaClaw-Z-Image-Turbo_lora_v1.safetensors"
            workflow["52"]["inputs"]["strength_model"] = 0.8
            workflow["52"]["inputs"]["strength_clip"] = 0.8
        else:
            # For any other name or generic prompt, disable LoRA
            workflow["52"]["inputs"]["strength_model"] = 0.0
            workflow["52"]["inputs"]["strength_clip"] = 0.0

    for node_id in workflow:
        node = workflow[node_id]
        if node.get("class_type") == "TextEncodeQwenImageEditPlus":
            if node.get("_meta", {}).get("title", "").endswith("(Positive)"):
                node["inputs"]["prompt"] = prompt_text
        elif node.get("class_type") == "CLIPTextEncode" or node_id in ["45", "50"]:
            if "inputs" in node:
                if "prompt" in node["inputs"]: node["inputs"]["prompt"] = prompt_text
                elif "text" in node["inputs"]: node["inputs"]["text"] = prompt_text
        
        if node.get("class_type") in ["EmptyLatentImage", "EmptySD3LatentImage"]:
            node["inputs"]["width"] = width
            node["inputs"]["height"] = height

    prompt_res = send_prompt(workflow)
    prompt_id = prompt_res.get("prompt_id")
    
    if not prompt_id:
        print(json.dumps({"error": "Failed to get prompt_id", "response": prompt_res}))
        return

    print(f"Connected to {COMFY_HOST}:{COMFY_PORT}. Job: {prompt_id}", file=sys.stderr)
    for _ in range(MAX_POLL):
        history = check_history(prompt_id)
        if prompt_id in history:
            outputs = history[prompt_id].get("outputs", {})
            results = []
            for node_id in outputs:
                if "images" in outputs[node_id]:
                    for img in outputs[node_id]["images"]:
                        local = download_file(img["filename"], img["subfolder"], img["type"])
                        results.append(local)
            print(json.dumps({"status": "success", "files": results}))
            return
        time.sleep(2)
    print(json.dumps({"error": "Timeout waiting for job", "prompt_id": prompt_id}))

if __name__ == "__main__":
    main()
