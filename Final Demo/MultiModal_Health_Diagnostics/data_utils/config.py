from pathlib import Path
import json
from typing import Dict, Any

from pathlib import Path
import json
from typing import Dict, Any
import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed

# ... rest of your existing code ...

# Update SETTINGS section (around line 40)
SETTINGS = {
    "max_file_size_mb": 10,
    "supported_formats": ["pdf", "png", "jpg", "jpeg", "csv", "txt"],
    "groq_api_key": os.getenv("GROQ_API_KEY", ""),  # Add this
    "ocr_lang": "eng"
}

# Base paths
BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Config file paths
PARAM_RANGES_PATH = CONFIG_DIR / "parameterranges.json"
CONTEXT_RANGES_PATH = CONFIG_DIR / "contextualranges.json"
DISEASE_RULES_PATH = CONFIG_DIR / "diseaserules.json"
GUIDELINES_PATH = DATA_DIR / "guidelines.json"

# Create directories
for dir_path in [CONFIG_DIR, DATA_DIR, LOGS_DIR]:
    dir_path.mkdir(exist_ok=True)

# Load configs (cached)
_cache = {}

def load_config(config_name: str) -> Dict[str, Any]:
    """Load JSON config with caching."""
    if config_name in _cache:
        return _cache[config_name]
    
    path_map = {
        "param_ranges": PARAM_RANGES_PATH,
        "context_ranges": CONTEXT_RANGES_PATH,
        "disease_rules": DISEASE_RULES_PATH,
        "guidelines": GUIDELINES_PATH
    }
    
    if config_name not in path_map:
        raise ValueError(f"Unknown config: {config_name}")
    
    with open(path_map[config_name], 'r') as f:
        _cache[config_name] = json.load(f)
    
    return _cache[config_name]

# Settings
SETTINGS = {
    "max_file_size_mb": 10,
    "supported_formats": ["pdf", "png", "jpg", "jpeg", "csv", "txt"],
    "ocr_lang": "eng"
}

if __name__ == "__main__":
    print(f"Base: {BASE_DIR}")
    print(f"Configs: {PARAM_RANGES_PATH.exists()}")
