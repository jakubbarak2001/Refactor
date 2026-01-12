"""
Asset Manager for visual game assets.
Maps story events to character expressions and backgrounds.
"""
import json
import os
import sys
from typing import Optional, Dict, Tuple


def resource_path(relative_path):
    """Get absolute path to resource (Works for Dev & EXE)"""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)


class AssetManager:
    """
    Manages loading and mapping of visual assets (sprites, backgrounds).
    Uses JSON configuration to decouple asset paths from game logic.
    """
    
    def __init__(self, assets_json_path: str = "assets.json"):
        """
        Initialize the asset manager.
        
        Args:
            assets_json_path: Path to the JSON file containing asset mappings
        """
        self.assets_json_path = assets_json_path
        self.assets_data = self._load_assets()
    
    def _load_assets(self) -> Dict:
        """Load assets configuration from JSON file."""
        try:
            json_path = resource_path(self.assets_json_path)
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Return empty structure if file doesn't exist yet
                return {
                    "characters": {},
                    "backgrounds": {},
                    "scenes": {}
                }
        except Exception as e:
            print(f"[ASSET MANAGER] Warning: Could not load assets.json: {e}")
            return {
                "characters": {},
                "backgrounds": {},
                "scenes": {}
            }
    
    def get_character_sprite(self, character: str, expression: str = "default") -> Optional[str]:
        """
        Get the file path for a character sprite.
        
        Args:
            character: Character name (e.g., "colonel", "jb", "martin")
            expression: Expression/emotion (e.g., "angry", "neutral", "smiling")
            
        Returns:
            Full path to sprite image, or None if not found
        """
        try:
            char_data = self.assets_data.get("characters", {}).get(character, {})
            sprite_path = char_data.get(expression, char_data.get("default"))
            
            if sprite_path:
                return resource_path(sprite_path)
            return None
        except Exception as e:
            print(f"[ASSET MANAGER] Error getting character sprite: {e}")
            return None
    
    def get_background(self, background_name: str) -> Optional[str]:
        """
        Get the file path for a background image.
        
        Args:
            background_name: Background identifier (e.g., "parking_lot", "police_station_office")
            
        Returns:
            Full path to background image, or None if not found
        """
        try:
            bg_path = self.assets_data.get("backgrounds", {}).get(background_name)
            
            if bg_path:
                return resource_path(bg_path)
            return None
        except Exception as e:
            print(f"[ASSET MANAGER] Error getting background: {e}")
            return None
    
    def get_scene_assets(self, scene_name: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Get all assets for a scene (background, character, expression).
        
        Args:
            scene_name: Scene identifier (e.g., "car_incident_intro", "colonel_angry")
            
        Returns:
            Tuple of (background_path, character_name, character_expression)
            Any can be None if not specified
        """
        try:
            scene_data = self.assets_data.get("scenes", {}).get(scene_name, {})
            
            bg_name = scene_data.get("background")
            background_path = self.get_background(bg_name) if bg_name else None
            
            character = scene_data.get("character")
            expression = scene_data.get("character_expression")
            
            return (background_path, character, expression)
        except Exception as e:
            print(f"[ASSET MANAGER] Error getting scene assets: {e}")
            return (None, None, None)
    
    def get_character_sprite_from_scene(self, scene_name: str) -> Optional[str]:
        """
        Convenience method to get character sprite directly from scene.
        
        Args:
            scene_name: Scene identifier
            
        Returns:
            Full path to character sprite, or None if not found
        """
        _, character, expression = self.get_scene_assets(scene_name)
        
        if character and expression:
            return self.get_character_sprite(character, expression)
        elif character:
            return self.get_character_sprite(character, "default")
        
        return None
