import json
import requests
import sys
import os
import time
import re

# --- DYNAMIC CONFIG ---
def load_comfy_env():
    env_path = os.path.join(SKILL_ROOT, ".env")
    config = {"HOST": "127.0.0.1", "PORT": "8188"}
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    if key == "COMFY_HOST": config["HOST"] = value
                    if key == "COMFY_PORT": config["PORT"] = value
        return config
    else:
        # If no .env, try to fallback to TOOLS.md (existing logic) or ask
        return None

env_config = load_comfy_env()
if env_config:
    COMFY_HOST = env_config["HOST"]
    COMFY_PORT = env_config["PORT"]
else:
    # Fallback to current TOOLS.md logic or prompt user if not found
    COMFY_HOST = "127.0.0.1"
    COMFY_PORT = "8188"
    if os.path.exists(TOOLS_PATH):
        with open(TOOLS_PATH, 'r') as f:
            content = f.read()
            host_match = re.search(r'Host:\s*([\d\.]+)', content)
            port_match = re.search(r'Port:\s*(\d+)', content)
            if host_match: COMFY_HOST = host_match.group(1).strip()
            if port_match: COMFY_PORT = port_match.group(1).strip()
    else:
        print("CRITICAL: ComfyUI .env not found. Please provide COMFY_HOST and COMFY_PORT.")
        sys.exit(1)

COMFY_URL = f"http://{COMFY_HOST}:{COMFY_PORT}"
ALLOWED_EXT = {'.jpg', '.jpeg', '.png', '.webp', '.mp4', '.mov', '.wav', '.mp3'}
WORKFLOW_MAP = {
    "gen_z": os.path.join(WORKFLOW_DIR, "image_z_image_turbo.json"),
    "qwen_edit": os.path.join(WORKFLOW_DIR, "qwen_image_edit_2511.json")
}

os.makedirs(OUTPUT_DIR, exist_ok=True)

def upload_file(input_path):
    with open(input_path, 'rb') as f:
        files = {'image': f}
        res = requests.post(f"{COMFY_URL}/upload/image", files=files)
        return res.json()

def send_prompt(workflow_data):
    p = {"prompt": workflow_data}
    data = json.dumps(p).encode('utf-8')
    res = requests.post(f"{COMFY_URL}/prompt", data=data)
    return res.json()

def check_history(prompt_id):
    res = requests.get(f"{COMFY_URL}/history/{prompt_id}")
    return res.json()

def download_file(filename, subfolder, folder_type):
    url = f"{COMFY_URL}/view?filename={filename}&subfolder={subfolder}&type={folder_type}"
    res = requests.get(url)
    file_path = os.path.join(OUTPUT_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(res.content)
    return file_path

def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: python3 comfy_client.py <template_id> <prompt_text>"}))
        return

    template_id = sys.argv[1]
    prompt_text = sys.argv[2]
    
    width, height = (720, 1280)

    if template_id not in WORKFLOW_MAP:
        return

    with open(WORKFLOW_MAP[template_id], 'r') as f:
        workflow = json.load(f)

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
        if node.get("class_type") in ["CLIPTextEncode", "TextEncodeQwenImageEditPlus"] or node_id in ["45", "50"]:
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
    while True:
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

if __name__ == "__main__":
    main()
