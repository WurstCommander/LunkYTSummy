import configparser
import os
import sys


class ConfigManager:

  def __init__(self, config_file: str | None = None):
    if config_file:
      self.config_file = config_file
      return

    if getattr(sys, "frozen", False):
      base_dir = os.path.dirname(sys.executable)
    else:
      base_dir = os.path.dirname(os.path.abspath(__file__))

    self.config_file = os.path.join(base_dir, "key.ini")

  def load_api_key(self) -> str | None:
    """Liest den API-Key aus der key.ini."""
    if os.path.exists(self.config_file):
      config = configparser.ConfigParser()
      try:
        config.read(self.config_file, encoding="utf-8")
        if "GEMINI" in config and "api_key" in config["GEMINI"]:
          key = config["GEMINI"]["api_key"].strip()
          if key:
            print(f"Loaded API key from key.ini: {key[:4]}...{key[-4:]}")
            return key
      except Exception:
        pass
    return None

  def save_api_key(self, key: str):
    """Speichert den API-Key dauerhaft in der key.ini."""
    config = configparser.ConfigParser()
    config["GEMINI"] = {"api_key": key.strip()}
    with open(self.config_file, "w", encoding="utf-8") as config_file:
      config.write(config_file)