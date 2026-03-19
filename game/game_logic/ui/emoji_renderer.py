"""
Emoji rendering using pygame-emojis library.
Replaces manual emoji detection and font switching.
"""
import logging
from typing import Optional, Dict, Tuple
import pygame

try:
    from pygame_emojis import load_emoji
    EMOJI_LIBRARY_AVAILABLE = True
except ImportError:
    EMOJI_LIBRARY_AVAILABLE = False
    load_emoji = None

logger = logging.getLogger(__name__)


class EmojiRenderer:
    """
    Handles emoji rendering using pygame-emojis library.
    Falls back to text replacements if library is unavailable.
    """
    
    # Emoji to text fallback mapping
    EMOJI_FALLBACKS = {
        '😡': '[HATRED]',
        '💻': '[CODING]',
        '💰': '[MONEY]',
        '💪': '[GYM]',
        '🧠': '[THERAPY]',
        '🌙': '[NIGHT SHIFT]',
        '⚙️': '[SETTINGS]',
        '⬅️': '[BACK]',
        '✅': '[OK]',
        '❌': '[X]',
        '🎭': '[MASK]',
        '💊': '[PILL]',
        '⚠️': '[WARNING]',
        '🎯': '[TARGET]',
    }
    
    def __init__(self):
        """Initialize emoji renderer."""
        self.emoji_cache: Dict[Tuple[str, Tuple[int, int]], pygame.Surface] = {}
        self.available = EMOJI_LIBRARY_AVAILABLE
        
        if not self.available:
            logger.warning("pygame-emojis not available, using text fallbacks")
    
    def has_emoji(self, text: str) -> bool:
        """
        Check if text contains emoji characters.
        
        Args:
            text: Text to check
            
        Returns:
            True if text contains emojis
        """
        if not self.available:
            return False
        
        # Check for common emoji characters
        for char in text:
            code_point = ord(char)
            # Comprehensive emoji Unicode ranges
            if (0x1F300 <= code_point <= 0x1F9FF) or \
               (0x1F600 <= code_point <= 0x1F64F) or \
               (0x1F680 <= code_point <= 0x1F6FF) or \
               (0x2600 <= code_point <= 0x26FF) or \
               (0x2700 <= code_point <= 0x27BF) or \
               (0x1F900 <= code_point <= 0x1F9FF) or \
               (0x1F1E0 <= code_point <= 0x1F1FF):
                return True
        return False
    
    def render_emoji(self, emoji_char: str, size: Tuple[int, int] = (32, 32)) -> Optional[pygame.Surface]:
        """
        Render an emoji character as a pygame Surface.
        
        Args:
            emoji_char: Single emoji character to render
            size: Size of the emoji surface (width, height)
            
        Returns:
            pygame.Surface with emoji, or None if rendering failed
        """
        if not self.available:
            return None
        
        # Check cache first
        cache_key = (emoji_char, size)
        if cache_key in self.emoji_cache:
            return self.emoji_cache[cache_key]
        
        try:
            emoji_surface = load_emoji(emoji_char, size)
            if emoji_surface:
                self.emoji_cache[cache_key] = emoji_surface
                return emoji_surface
        except Exception as e:
            logger.warning(f"Failed to load emoji {emoji_char}: {e}")
        
        return None
    
    def replace_emojis_with_text(self, text: str) -> str:
        """
        Replace emojis with text fallbacks.
        Used when emoji library is unavailable.
        
        Args:
            text: Text containing emojis
            
        Returns:
            Text with emojis replaced by fallback strings
        """
        result = text
        for emoji, replacement in self.EMOJI_FALLBACKS.items():
            result = result.replace(emoji, replacement)
        return result
    
    def extract_emojis_from_text(self, text: str) -> list[Tuple[int, str]]:
        """
        Extract emoji characters and their positions from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of tuples (position, emoji_char)
        """
        emojis = []
        for i, char in enumerate(text):
            if self.has_emoji(char):
                emojis.append((i, char))
        return emojis
