import json
import requests
import sys
import os
import time
import re
import random
import uuid

# --- DYNAMIC CONFIG ---
COMFY_HOST = "192.168.1.42"
COMFY_PORT = "8188"

SKILL_ROOT = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_ROOT = os.path.abspath(os.path.join(SKILL_ROOT, "..", ".."))
TOOLS_PATH = os.path.join(WORKSPACE_ROOT, "TOOLS.md")
OUTPUT_DIR = os.path.join(WORKSPACE_ROOT, "..", "media", "comfy")
WORKFLOW_DIR = os.path.join(SKILL_ROOT, "workflows")
PRIVATE_WORKFLOW_DIR = os.path.join(WORKFLOW_DIR, "Private")

# Check for host/port in TOOLS.md but default to the above if not found
if os.path.exists(TOOLS_PATH):
    with open(TOOLS_PATH, 'r') as f:
        content = f.read()
        # Look for the ComfyUI section specifically to avoid picking up other hosts
        comfy_section = re.search(r'### 🎨 Visual & Image Generation(.*?)(?=\n###|\Z)', content, re.DOTALL)
        if comfy_section:
            section_text = comfy_section.group(1)
            host_match = re.search(r'Host:\s*([\d\.]+)', section_text)
            port_match = re.search(r'Port:\s*(\d+)', section_text)
            if host_match: COMFY_HOST = host_match.group(1).strip()
            if port_match: COMFY_PORT = port_match.group(1).strip()

COMFY_URL = f"http://{COMFY_HOST}:{COMFY_PORT}"

def upload_file(input_path):
    with open(input_path, 'rb') as f:
        files = {'image': f}
        res = requests.post(f"{COMFY_URL}/upload/image", files=files)
        return res.json()

def send_prompt(workflow_data, client_id):
    p = {"prompt": workflow_data, "client_id": client_id}
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
        print(json.dumps({"error": "Usage: python3 ltx2_video.py <input_image_path> <movement_prompt>"}))
        return

    input_path = sys.argv[1]
    movement_prompt = sys.argv[2]
    
    workflow_path = os.path.join(PRIVATE_WORKFLOW_DIR, "LTX2-LD-I2V.json")
    with open(workflow_path, 'r') as f:
        workflow = json.load(f)

    uploaded_filename = None
    if os.path.exists(input_path):
        upload_res = upload_file(input_path)
        uploaded_filename = upload_res.get("name")
    else:
        uploaded_filename = input_path

    # Keep 100% of your JSON settings, only injecting image and user prompt
    for node_id, node in workflow.items():
        if node.get("class_type") == "LoadImage":
            node["inputs"]["image"] = uploaded_filename
        if node.get("class_type") == "LTX2PromptArchitect":
            node["inputs"]["user_input"] = movement_prompt
        # Force fresh run with a new seed
        if node.get("class_type") == "SeedGenerator":
            node["inputs"]["seed"] = random.randint(1, 1000000)

    client_id = str(uuid.uuid4())
    prompt_res = send_prompt(workflow, client_id)
    prompt_id = prompt_res.get("prompt_id")
    
    if not prompt_id:
        print(json.dumps({"error": "Failed to get prompt_id", "response": prompt_res}))
        return

    print(f"Connected to {COMFY_HOST}:{COMFY_PORT}. Client: {client_id}. Job: {prompt_id}. Waiting...", file=sys.stderr)
    
    while True:
        history = check_history(prompt_id)
        if prompt_id in history:
            outputs = history[prompt_id].get("outputs", {})
            results = []
            for node_id in outputs:
                node_output = outputs[node_id]
                for key in ['gifs', 'images', 'videos', 'video']:
                    if key in node_output:
                        for item in node_output[key]:
                            local = download_file(item["filename"], item.get("subfolder", ""), item.get("type", "output"))
                            results.append(local)
            
            if results:
                for file in results:
                    print(f"DELIVER:{file}")
            
            print(json.dumps({"status": "success", "files": results, "prompt_id": prompt_id}))
            return
        time.sleep(10)

if __name__ == "__main__":
    main()
