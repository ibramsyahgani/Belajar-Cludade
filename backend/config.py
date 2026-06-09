import os
import yaml
from dotenv import load_dotenv

load_dotenv()


def load_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_config(config_data: dict):
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)


def get_gemini_api_key():
    return os.getenv("GEMINI_API_KEY", "")


def get_admin_password():
    return os.getenv("ADMIN_PASSWORD", "admin123")
