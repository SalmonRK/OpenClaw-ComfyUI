import json
import requests
import sys
import os
import time

# --- CONFIG ---
COMFY_HOST = "192.168.1.38"
COMFY_PORT = "8190"
COMFY_URL = f"http://{COMFY_HOST}:{COMFY_PORT}"

SKILL_ROOT = os.path.dirname(os.path.abspath(__file__))
# Get workspace root (assumed to be 2 levels up from skills/comfyui/)
WORKSPACE_ROOT = os.path.abspath(os.path.join(SKILL_ROOT, "..", ".."))
OUTPUT_DIR = os.path.join(WORKSPACE_ROOT, "outputs", "comfy")
WORKFLOW_DIR = os.path.join(SKILL_ROOT, "workflows")

WORKFLOW_MAP = {
    "gen_z": os.path.join(WORKFLOW_DIR, "image_z_image_turbo.json"),
    "qwen_edit": os.path.join(WORKFLOW_DIR, "qwen_image_edit_2511.json")
}

os.makedirs(OUTPUT_DIR, exist_ok=True)

def upload_image(input_path):
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

def download_image(filename, subfolder, folder_type):
    url = f"{COMFY_URL}/view?filename={filename}&subfolder={subfolder}&type={folder_type}"
    res = requests.get(url)
    file_path = os.path.join(OUTPUT_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(res.content)
    return file_path

def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: python3 comfy_client.py <template_id> <prompt_text> [input_image_path]"}))
        return

    template_id = sys.argv[1]
    prompt_text = sys.argv[2]
    input_image_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    if template_id not in WORKFLOW_MAP:
        print(json.dumps({"error": f"Unknown template: {template_id}"}))
        return

    with open(WORKFLOW_MAP[template_id], 'r') as f:
        workflow = json.load(f)

    # Handle Image Upload if needed
    uploaded_filename = None
    if input_image_path:
        print(f"Uploading image: {input_image_path}...", file=sys.stderr)
        upload_res = upload_image(input_image_path)
        uploaded_filename = upload_res.get("name")
        if not uploaded_filename:
            print(json.dumps({"error": "Upload failed", "res": upload_res}))
            return

    # Inject values into Workflow
    for node_id in workflow:
        node = workflow[node_id]
        # Inject Prompt
        if node.get("class_type") == "CLIPTextEncode":
            if "inputs" in node and "text" in node["inputs"]:
                # Simple logic: replace if it contains "prompt" or is empty (adjust as needed)
                node["inputs"]["text"] = prompt_text
        
        # Inject Image for Edit
        if uploaded_filename and node.get("class_type") == "LoadImage":
            node["inputs"]["image"] = uploaded_filename

    # Send Job
    prompt_res = send_prompt(workflow)
    prompt_id = prompt_res.get("prompt_id")
    
    if not prompt_id:
        print(json.dumps({"error": "Failed to get prompt_id", "response": prompt_res}))
        return

    print(f"Job sent! ID: {prompt_id}. Waiting for result...", file=sys.stderr)
    while True:
        history = check_history(prompt_id)
        if prompt_id in history:
            outputs = history[prompt_id].get("outputs", {})
            for node_id in outputs:
                if "images" in outputs[node_id]:
                    img_data = outputs[node_id]["images"][0]
                    local_path = download_image(img_data["filename"], img_data["subfolder"], img_data["type"])
                    print(json.dumps({
                        "status": "success",
                        "prompt_id": prompt_id,
                        "local_path": local_path,
                        "filename": img_data["filename"]
                    }))
                    return
        time.sleep(2)

if __name__ == "__main__":
    main()
