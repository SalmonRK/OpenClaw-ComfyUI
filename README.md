# ComfyUI-OpenClaw Skill 🎨✨

A professional, token-saving agent skill for connecting and controlling ComfyUI via API. Designed for high efficiency, automatic asset handling, and seamless integration with OpenClaw.

## 🏗️ Skill Structure
- **Connection:** Managed via `~/.openclaw/skills/comfyui/.env` (Private).
- **Global Skill Path:** `~/.openclaw/skills/comfyui/` (Shared across all agent workspaces).
- **Workflow Directory:** `skills/comfyui/workflows/`
- **Private Workflows:** `skills/comfyui/workflows/Private/` (Excluded via `.gitignore`).
- **Core Scripts:**
    - `comfy_client.py`: Standard Image Generation/Editing.
    - `ltx2_video.py`: Private Video Animation.

## 🛠️ Tools (CLI)
Invoke via the `exec` command using the global skill path:

### 1. Image Generation/Edit
`python3 ~/.openclaw/skills/comfyui/comfy_client.py <template_id> "<prompt>" [input_image_path/orientation] [orientation]`

### 2. Private Video Animation
`python3 ~/.openclaw/skills/comfyui/ltx2_video.py <input_image_path> "<movement_prompt>"`

## 🚀 Strategy & Security
- **Token Efficiency:** Refer to templates by ID; use partial file reads for large JSONs.
- **Private Security:** All sensitive Host IPs/Ports are kept in a local `.env` file (Excluded from GitHub).
- **Proactive Delivery:** Automatically sends results to Telegram and opens them on the MacBook.
- **Expert Personas Integration:** Optimized for specialized agents (Ava, Mari, Rei, Asuka) to produce high-quality character-consistent portraits.
