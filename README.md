# ComfyUI-OpenClaw Skill

A professional, token-saving agent skill for connecting and controlling ComfyUI via API.

## Skill Structure
- **Connection:** Managed via `skills/comfyui/.env` (Private, gitignored).
- **Config:** Shared `config.py` module — single source of truth for both scripts.
- **Workflow Directory:** `skills/comfyui/workflows/`
- **Private Workflows:** `skills/comfyui/workflows/Private/` (gitignored).
- **Core Scripts:**
    - `comfy_client.py`: Image Generation/Editing.
    - `ltx2_video.py`: Private Video Animation.

## Tools (CLI)

### 1. Image Generation/Edit
`python3 skills/comfyui/comfy_client.py <template_id> "<prompt>" [input_image_path] [portrait|landscape]`

### 2. Private Video Animation
`python3 skills/comfyui/ltx2_video.py <input_image_path> "<movement_prompt>"`

## Strategy & Security
- **Token Efficiency:** Refer to templates by ID; use partial file reads for large JSONs.
- **Private Security:** All sensitive Host IPs/Ports kept in `.env` (excluded from GitHub).
- **Proactive Delivery:** Automatically sends results to Telegram and opens on MacBook.
- **Character System:** Strict LoRA injection for MariClaw/AsukaClaw; auto-disabled for other prompts.
