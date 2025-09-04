"""
Storage management for EnvStarter environments and configuration.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from envstarter.core.models import Environment, Application, Website


class ConfigManager:
    """Manages configuration and environment storage."""
    
    def __init__(self):
        self.app_data_dir = self._get_app_data_dir()
        self.config_file = self.app_data_dir / "config.json"
        self.environments_file = self.app_data_dir / "environments.json"
        
        # Ensure directories exist
        self.app_data_dir.mkdir(parents=True, exist_ok=True)
        
        self._ensure_default_files()
    
    def _get_app_data_dir(self) -> Path:
        """Get the application data directory."""
        if os.name == 'nt':  # Windows
            app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
            return Path(app_data) / "EnvStarter"
        else:
            # For development/testing on non-Windows
            return Path.home() / ".envstarter"
    
    def _ensure_default_files(self):
        """Create default configuration files if they don't exist."""
        if not self.config_file.exists():
            default_config = {
                "version": "1.0.0",
                "first_run": True,
                "auto_start": True,
                "minimize_to_tray": True,
                "show_notifications": True,
                "theme": "system",
                "last_selected_environment": None,
                "window_position": {"x": -1, "y": -1},
                "window_size": {"width": 600, "height": 400}
            }
            self._save_json(self.config_file, default_config)
        
        if not self.environments_file.exists():
            # Create sample environments
            sample_environments = self._create_sample_environments()
            self._save_json(self.environments_file, {"environments": [env.to_dict() for env in sample_environments]})
    
    def _create_sample_environments(self) -> List[Environment]:
        """Create sample environments for first-time users."""
        environments = []
        
        # Development Environment
        dev_env = Environment(
            name="Development",
            description="Full development setup with IDE and tools",
            applications=[
                Application(name="Visual Studio Code", path="code", arguments=""),
                Application(name="Git Bash", path="C:\\Program Files\\Git\\git-bash.exe", arguments="")
            ],
            websites=[
                Website(name="GitHub", url="https://github.com"),
                Website(name="Stack Overflow", url="https://stackoverflow.com"),
                Website(name="Localhost Dev Server", url="http://localhost:3000")
            ]
        )
        environments.append(dev_env)
        
        # Support Environment
        support_env = Environment(
            name="Support",
            description="Customer support tools and communication",
            applications=[
                Application(name="Notepad++", path="notepad++", arguments="")
            ],
            websites=[
                Website(name="Gmail", url="https://mail.google.com"),
                Website(name="Teams", url="https://teams.microsoft.com"),
                Website(name="Zendesk", url="https://support.zendesk.com")
            ]
        )
        environments.append(support_env)
        
        # Gaming Environment
        gaming_env = Environment(
            name="Gaming",
            description="Gaming setup with communication tools",
            applications=[
                Application(name="Steam", path="C:\\Program Files (x86)\\Steam\\steam.exe", arguments="-silent"),
                Application(name="Discord", path="C:\\Users\\%USERNAME%\\AppData\\Local\\Discord\\app-1.0.9011\\Discord.exe", arguments="")
            ],
            websites=[
                Website(name="Twitch", url="https://twitch.tv"),
                Website(name="Reddit Gaming", url="https://reddit.com/r/gaming")
            ]
        )
        environments.append(gaming_env)
        
        return environments
    
    def _save_json(self, file_path: Path, data: Dict[str, Any]):
        """Save data to JSON file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving to {file_path}: {e}")
    
    def _load_json(self, file_path: Path) -> Dict[str, Any]:
        """Load data from JSON file."""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading from {file_path}: {e}")
        return {}
    
    def get_config(self) -> Dict[str, Any]:
        """Get application configuration."""
        return self._load_json(self.config_file)
    
    def save_config(self, config: Dict[str, Any]):
        """Save application configuration."""
        self._save_json(self.config_file, config)
    
    def update_config(self, **kwargs):
        """Update specific configuration values."""
        config = self.get_config()
        config.update(kwargs)
        self.save_config(config)
    
    def is_first_run(self) -> bool:
        """Check if this is the first run of the application."""
        config = self.get_config()
        return config.get("first_run", True)
    
    def mark_first_run_complete(self):
        """Mark first run as completed."""
        self.update_config(first_run=False)
    
    def get_environments(self) -> List[Environment]:
        """Get all environments."""
        data = self._load_json(self.environments_file)
        environments = []
        
        for env_data in data.get("environments", []):
            try:
                env = Environment.from_dict(env_data)
                environments.append(env)
            except Exception as e:
                print(f"Error loading environment: {e}")
        
        return environments
    
    def save_environments(self, environments: List[Environment]):
        """Save all environments."""
        data = {
            "environments": [env.to_dict() for env in environments],
            "last_updated": datetime.now().isoformat()
        }
        self._save_json(self.environments_file, data)
    
    def add_environment(self, environment: Environment) -> bool:
        """Add a new environment."""
        environments = self.get_environments()
        
        # Check for duplicate names
        if any(env.name.lower() == environment.name.lower() for env in environments):
            return False
        
        environment.created_at = datetime.now().isoformat()
        environment.modified_at = environment.created_at
        environments.append(environment)
        self.save_environments(environments)
        return True
    
    def update_environment(self, environment: Environment) -> bool:
        """Update an existing environment."""
        environments = self.get_environments()
        
        for i, env in enumerate(environments):
            if env.id == environment.id:
                environment.modified_at = datetime.now().isoformat()
                environments[i] = environment
                self.save_environments(environments)
                return True
        
        return False
    
    def delete_environment(self, environment_id: str) -> bool:
        """Delete an environment."""
        environments = self.get_environments()
        
        for i, env in enumerate(environments):
            if env.id == environment_id:
                environments.pop(i)
                self.save_environments(environments)
                return True
        
        return False
    
    def get_environment_by_id(self, environment_id: str) -> Optional[Environment]:
        """Get environment by ID."""
        environments = self.get_environments()
        
        for env in environments:
            if env.id == environment_id:
                return env
        
        return None
    
    def get_environment_by_name(self, name: str) -> Optional[Environment]:
        """Get environment by name."""
        environments = self.get_environments()
        
        for env in environments:
            if env.name.lower() == name.lower():
                return env
        
        return None