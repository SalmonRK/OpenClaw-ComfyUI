# ComfyUI-OpenClaw Skill

A professional, token-saving agent skill for connecting and controlling ComfyUI via API. Designed for high efficiency, automatic asset handling, and seamless integration with OpenClaw.

## Skill Structure
- **Connection:** Managed via `skills/comfyui/.env` (Private, gitignored).
- **Setup:** If `.env` is missing, the script exits with an error. Agent must ask the user for `COMFY_HOST` and `COMFY_PORT`.
- **Config Module:** `skills/comfyui/config.py` — shared config loader for all scripts.
- **Workflow Directory:** `skills/comfyui/workflows/`
- **Output Directory:** Configured via `OUTPUT_DIR` in `.env` (default: `~/.openclaw/media/comfy/`)
- **Core Scripts:**
    - `comfy_client.py`: Image Generation/Editing.
    - `ltx2_video.py`: Private Video Animation.

## Tools (CLI)
Invoke via the `exec` command:
1. `python3 skills/comfyui/comfy_client.py <template_id> "<prompt>" [input_image_path] [portrait|landscape]`
2. `python3 skills/comfyui/ltx2_video.py <input_image_path> "<movement_prompt>"` (Private Video Animation)

### Parameters:
- **template_id:**
    1. `gen_z`: Text-to-Image (uses `image_z_image_turbo.json`)
    2. `qwen_edit`: Image-to-Image / Editing (uses `qwen_image_edit_2511.json`) — supports automatic image upload.
- **prompt:** The description of the image to generate or edits to perform.
- **input_image_path:** (Optional) Local path for image tasks. Auto-uploaded to ComfyUI and injected into all `LoadImage` nodes.
- **movement_prompt:** Describe the movement for video (e.g., "gentle hair breeze").
- **orientation:** (Optional) `portrait` (720x1280, default) or `landscape` (1280x720). Can appear in any position after prompt.

### Character System (Strict LoRA Injection)
The skill automatically detects specific character names in the prompt and injects the corresponding LoRA:
- **MariClaw:** Detects "MariClaw" → Injects `MariClaw-Z-Image-Turbo_lora_v1.safetensors` (Strength: 0.8).
- **AsukaClaw:** Detects "AsukaClaw" → Injects `AsukaClaw-Z-Image-Turbo_lora_v1.safetensors` (Strength: 0.8).
- **Other/Generic:** LoRA strengths set to **0.0** — clean results without accidental LoRA interference.

### Prompt Injection Logic
- **gen_z template:** Prompt injected into `CLIPTextEncode` nodes and nodes 45/50.
- **qwen_edit template:** Prompt injected into `TextEncodeQwenImageEditPlus` nodes with `_meta.title` ending in `(Positive)` only. This ensures only the positive prompt node is modified.

### Private Video Animation (Experimental)
- **Script:** `skills/comfyui/ltx2_video.py`
- **Capability:** Image-to-Video Animation (LTX-2 model).
- **Constraint:** ใช้ prompt ที่มีการเคลื่อนไหวพื้นฐานที่ไม่ซับซ้อนเท่านั้น (เช่น ขยับหัว ยิ้ม ลมพัดผม)
- **Performance:** ใช้เวลาสร้าง 5-10 นาที (รันแบบ Background อัตโนมัติ).
- **Automation:** เมื่อเสร็จจะส่งเข้า Telegram และเปิดบน Mac ทันที.
- **Smart Tech:** ใช้ระบบสุ่ม Seed อัตโนมัติและจำลอง Client ID เพื่อความเสถียรสูงสุดผ่าน API.

## How to Add New Workflows
1. Place your new API-formatted JSON workflow in `skills/comfyui/workflows/`.
2. Update the `WORKFLOW_MAP` dictionary in `comfy_client.py` with a new ID and file path.
3. (Optional) If the workflow uses unique node types, adjust the injection logic in `main()`.

## Token-Saving & Efficiency Strategy
- **Template Mapping:** Never send full workflow JSONs in the chat. Refer to them by `template_id`.
- **Vision-Saving:** Prioritize using **file path from metadata** instead of analyzing image content via vision unless explicitly asked.
- **Direct Delivery:** Deliver images via Telegram or local `open` to avoid bloating context.
- **Sub-agent Orchestration:** For multi-scene projects, use sub-agents to process long-running tasks (like `ltx2_video`) in the background.
