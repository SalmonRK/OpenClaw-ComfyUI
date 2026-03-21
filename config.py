import os
import sys

SKILL_ROOT = os.path.dirname(os.path.abspath(__file__))
WORKFLOW_DIR = os.path.join(SKILL_ROOT, "workflows")
PRIVATE_WORKFLOW_DIR = os.path.join(WORKFLOW_DIR, "Private")

# Default OUTPUT_DIR: <workspace-rei>/../../media/comfy
_DEFAULT_OUTPUT = os.path.abspath(os.path.join(SKILL_ROOT, "..", "..", "..", "media", "comfy"))


def load_config():
    """Load config from .env file. Exit if not found."""
    env_path = os.path.join(SKILL_ROOT, ".env")
    config = {}

    if not os.path.exists(env_path):
        print("CRITICAL: ComfyUI .env not found at", env_path)
        print("Please create it with COMFY_HOST and COMFY_PORT.")
        sys.exit(1)

    with open(env_path, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                config[key.strip()] = value.strip()

    host = config.get("COMFY_HOST", "127.0.0.1")
    port = config.get("COMFY_PORT", "8188")
    output_dir = config.get("OUTPUT_DIR", _DEFAULT_OUTPUT)

    return {
        "HOST": host,
        "PORT": port,
        "COMFY_URL": f"http://{host}:{port}",
        "OUTPUT_DIR": output_dir,
        "WORKFLOW_DIR": WORKFLOW_DIR,
        "PRIVATE_WORKFLOW_DIR": PRIVATE_WORKFLOW_DIR,
        "SKILL_ROOT": SKILL_ROOT,
    }
