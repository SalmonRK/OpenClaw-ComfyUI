# ComfyUI-OpenClaw Skill 🎨✨

A professional, token-saving agent skill for connecting and controlling ComfyUI via API. Designed for high efficiency, automatic asset handling, and seamless integration with OpenClaw.

## 🏗️ Skill Structure
- **Connection:** Managed via `skills/comfyui/.env` (Private).
- **Setup:** If `.env` is missing, the script will exit and the agent must ask the user for the `COMFY_HOST` and `COMFY_PORT`.
- **Workflow Directory:** `skills/comfyui/workflows/`
- **Output Directory:** Configured via `TOOLS.md` (e.g., `outputs/comfy/`)
- **Core Script:** `skills/comfyui/comfy_client.py`

## 🛠️ Tools (CLI)
Invoke via the `exec` command:
1. `python3 skills/comfyui/comfy_client.py <template_id> "<prompt>" [input_image_path/orientation] [orientation]`
2. `python3 skills/comfyui/ltx2_video.py <input_image_path> "<movement_prompt>"` (Private Video Animation)

### Parameters:
- **template_id:**
    1. `gen_z`: Text-to-Image (uses `image_z_image_turbo.json`)
    2. `qwen_edit`: Image-to-Image / Editing (uses `qwen_image_edit_2511.json`) - *Supports automatic image upload.*
- **prompt:** The description of the image to generate or edits to perform.
- **input_image_path:** Local path for image/video tasks.
- **movement_prompt:** Describe the movement (e.g., "gentle hair breeze").
- **orientation:** (Optional) Set to `portrait` (720x1280) or `landscape` (1280x720). Defaults to `portrait`.

### 🎭 Character System (Strict LoRA Injection)
The skill automatically detects specific character names and injects the corresponding LoRA:
- **MariClaw:** Detects "MariClaw" → Injects `MariClaw-Z-Image-Turbo_lora_v1.safetensors` (Strength: 0.8).
- **AsukaClaw:** Detects "AsukaClaw" → Injects `AsukaClaw-Z-Image-Turbo_lora_v1.safetensors` (Strength: 0.8).
- **Other Names/Generic:** If the prompt specifies **any other name** or no character name is found, LoRA strengths are automatically set to **0.0**. This ensures clean, non-stylized results for general or realistic human requests without accidental LoRA interference.

### 🎞️ Private Video Animation (Experimental)
- **Script:** `skills/comfyui/ltx2_video.py`
- **Capability:** Image-to-Video Animation.
- **Constraint:** **ใช้ prompt ที่มีการเคลื่อนไหวพื้นฐานที่ไม่ซับซ้อนเท่านั้น** (เช่น ขยับหัว ยิ้ม ลมพัดผม)
- **Performance:** ใช้เวลาสร้าง 5-10 นาที (รันแบบ Background อัตโนมัติ).
- **Automation:** เมื่อเสร็จจะส่งเข้า Telegram และเปิดบน Mac ทันที.
- **Smart Tech:** ใช้ระบบสุ่ม Seed อัตโนมัติและจำลอง Client ID เพื่อความเสถียรสูงสุดผ่าน API.

## 💡 How to Add New Workflows
You can expand this skill easily:
1. Place your new API-formatted JSON workflow in `skills/comfyui/workflows/`.
2. Update the `WORKFLOW_MAP` dictionary in `skills/comfyui/comfy_client.py` with a new ID and the file path.
3. (Optional) If the workflow uses unique node types, adjust the injection logic in the script's `main()` function.

## 🚀 Token-Saving & Efficiency Strategy
- **Template Mapping:** Never send full workflow JSONs in the chat. Refer to them by `template_id`.
- **Vision-Saving Strategy:** To minimize token usage, the agent should prioritize using the **file path from metadata** instead of analyzing image content via vision capabilities unless explicitly asked.
- **Direct Delivery:** Deliver images directly via messaging (Telegram) or local openers (`open`) to avoid bloating context.
- **Sub-agent Orchestration:** For complex multi-scene projects (e.g., Ava Studio), use sub-agents to process long-running tasks (like `ltx2_video`) in the background.
- **Production Template:** Use `assets/production_template.json` to manage multi-scene workflows without re-reading all details into the main context. Use `grep` or specific `read` offsets to fetch only active scene data.
