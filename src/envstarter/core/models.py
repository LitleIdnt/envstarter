"""
Data models for EnvStarter environments and applications.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path
import uuid


@dataclass
class Application:
    """Represents an application to be launched."""
    name: str
    path: str
    arguments: str = ""
    working_directory: Optional[str] = None
    wait_for_exit: bool = False
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "path": self.path,
            "arguments": self.arguments,
            "working_directory": self.working_directory,
            "wait_for_exit": self.wait_for_exit
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Application':
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data["name"],
            path=data["path"],
            arguments=data.get("arguments", ""),
            working_directory=data.get("working_directory"),
            wait_for_exit=data.get("wait_for_exit", False)
        )
    
    def is_valid(self) -> bool:
        """Check if application path exists and is executable."""
        path = Path(self.path)
        return path.exists() and (path.suffix.lower() in ['.exe', '.msi', '.bat', '.cmd'] or path.is_dir())


@dataclass
class Website:
    """Represents a website to be opened."""
    name: str
    url: str
    browser: Optional[str] = None  # Specific browser path, None for system default
    new_tab: bool = True
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "browser": self.browser,
            "new_tab": self.new_tab
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Website':
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data["name"],
            url=data["url"],
            browser=data.get("browser"),
            new_tab=data.get("new_tab", True)
        )
    
    def is_valid(self) -> bool:
        """Check if URL is valid."""
        return bool(self.url and (self.url.startswith("http://") or self.url.startswith("https://")))


@dataclass
class Environment:
    """Represents a complete work environment."""
    name: str
    description: str = ""
    applications: List[Application] = field(default_factory=list)
    websites: List[Website] = field(default_factory=list)
    startup_delay: int = 0  # Seconds to wait before starting
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: Optional[str] = None
    modified_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "applications": [app.to_dict() for app in self.applications],
            "websites": [site.to_dict() for site in self.websites],
            "startup_delay": self.startup_delay,
            "created_at": self.created_at,
            "modified_at": self.modified_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Environment':
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data["name"],
            description=data.get("description", ""),
            applications=[Application.from_dict(app) for app in data.get("applications", [])],
            websites=[Website.from_dict(site) for site in data.get("websites", [])],
            startup_delay=data.get("startup_delay", 0),
            created_at=data.get("created_at"),
            modified_at=data.get("modified_at")
        )
    
    def get_total_items(self) -> int:
        """Get total number of items (apps + websites) in this environment."""
        return len(self.applications) + len(self.websites)
    
    def is_valid(self) -> bool:
        """Check if environment has valid items."""
        if not self.name:
            return False
        
        # Check if at least one application or website exists and is valid
        valid_apps = [app for app in self.applications if app.is_valid()]
        valid_sites = [site for site in self.websites if site.is_valid()]
        
        return len(valid_apps) > 0 or len(valid_sites) > 0