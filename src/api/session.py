"""Manage global ClassInfo state across API requests."""
from src.core.models import ClassInfo, Final

class SessionManager:
    """Manages ClassInfo objects for the current session."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.agility_class = None
            cls._instance.jumping_class = None
            cls._instance.final = None
        return cls._instance
    
    def initialize_classes(self, agility_class: ClassInfo, jumping_class: ClassInfo, final: Final = None):
        """Store ClassInfo objects globally."""
        self.agility_class = agility_class
        self.jumping_class = jumping_class
        self.final = final
    
    def add_final(self, final: Final):
        """Store Final object globally."""
        self.final = final
    
    def clear(self):
        """Clear session data."""
        self.agility_class = None
        self.jumping_class = None
        self.final = None


# Global session instance - always returns same object
session = SessionManager()