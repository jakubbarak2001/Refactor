"""
GUI Interaction implementation using pygame.
Renders game scenes with backgrounds, character sprites, and text.
"""
import os
import sys
import pygame
from typing import Optional, List, Tuple

from game.game_logic.interaction import InteractionInterface
from game.game_logic.asset_manager import AssetManager, resource_path
from game.game_logic.interaction import TerminalInteraction


# Initialize pygame
pygame.init()
pygame.font.init()


def _safe_print(*args, **kwargs):
    """Safely print to stdout, ignoring errors if stdout is closed."""
    try:
        print(*args, **kwargs)
    except (ValueError, OSError):
        # stdout is closed or unavailable, ignore
        pass


class GUIInteraction(InteractionInterface):
    """
    Pygame-based GUI implementation of InteractionInterface.
    Displays backgrounds, character sprites, text, and decision buttons.
    """
    
    # Window configuration
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720
    FPS = 60
    
    # Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    DARK_GRAY = (64, 64, 64)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    
    def __init__(self):
        """Initialize the GUI renderer."""
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("REFACTOR")
        self.clock = pygame.time.Clock()
        self.asset_manager = AssetManager("assets.json")
        
        # Scrolling state for decision buttons
        self.decision_scroll_offset = 0
        self.max_scroll_offset = 0
        
        # Load fonts - try to use emoji-supporting fonts
        self.emoji_supported = False
        try:
            # Try Windows emoji font first
            emoji_fonts = ['Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji', 'Apple Color Emoji']
            emoji_font = None
            for font_name in emoji_fonts:
                try:
                    if pygame.font.match_font(font_name):
                        test_font = pygame.font.SysFont(font_name, 24)
                        # Test if font can render an emoji
                        test_surface = test_font.render('😡', True, (255, 255, 255))
                        # Check if we got a reasonable width (emoji should be wider than a few pixels)
                        if test_surface.get_width() > 10:
                            emoji_font = font_name
                            self.emoji_supported = True
                            break
                except:
                    continue
            
            # Use monospace/hacker fonts (Mr. Robot style)
            hacker_fonts = ['Consolas', 'Courier New', 'Monaco', 'Lucida Console', 'Courier']
            text_font_name = None
            for font_name in hacker_fonts:
                if pygame.font.match_font(font_name):
                    text_font_name = font_name
                    break
            
            # Use emoji font if found, otherwise fallback
            if emoji_font:
                if text_font_name:
                    # Use monospace font for text, emoji font for emojis
                    self.font_large = pygame.font.SysFont(text_font_name, 36, bold=True)
                    self.font_medium = pygame.font.SysFont(text_font_name, 24)
                    self.font_small = pygame.font.SysFont(text_font_name, 18)
                    self.font_bold = pygame.font.SysFont(text_font_name, 24, bold=True)
                    self.emoji_font_large = pygame.font.SysFont(emoji_font, 36)
                    self.emoji_font_medium = pygame.font.SysFont(emoji_font, 24)
                    self.emoji_font_small = pygame.font.SysFont(emoji_font, 18)
                else:
                    self.font_large = pygame.font.SysFont(emoji_font, 36, bold=True)
                    self.font_medium = pygame.font.SysFont(emoji_font, 24)
                    self.font_small = pygame.font.SysFont(emoji_font, 18)
                    self.font_bold = pygame.font.SysFont(emoji_font, 24, bold=True)
                    self.emoji_font_large = self.font_large
                    self.emoji_font_medium = self.font_medium
                    self.emoji_font_small = self.font_small
                _safe_print(f"[GUI] Using emoji font: {emoji_font}, hacker font: {text_font_name or 'default'}")
            else:
                # Fallback to system default
                if text_font_name:
                    self.font_large = pygame.font.SysFont(text_font_name, 36, bold=True)
                    self.font_medium = pygame.font.SysFont(text_font_name, 24)
                    self.font_small = pygame.font.SysFont(text_font_name, 18)
                    self.font_bold = pygame.font.SysFont(text_font_name, 24, bold=True)
                else:
                    self.font_large = pygame.font.SysFont(None, 36)
                    self.font_medium = pygame.font.SysFont(None, 24)
                    self.font_small = pygame.font.SysFont(None, 18)
                    self.font_bold = pygame.font.SysFont(None, 24, bold=True)
                self.emoji_font_large = self.font_large
                self.emoji_font_medium = self.font_medium
                self.emoji_font_small = self.font_small
                _safe_print("[GUI] Emoji font not available, using text replacements")
        except Exception as e:
            # Final fallback
            self.font_large = pygame.font.SysFont('courier', 36, bold=True)
            self.font_medium = pygame.font.SysFont('courier', 24)
            self.font_small = pygame.font.SysFont('courier', 18)
            self.font_bold = pygame.font.SysFont('courier', 24, bold=True)
            self.emoji_font_large = self.font_large
            self.emoji_font_medium = self.font_medium
            self.emoji_font_small = self.font_small
            _safe_print(f"[GUI] Font initialization error: {e}")
        
        # Hacker theme colors (Mr. Robot style)
        self.HACKER_GREEN = (0, 255, 0)  # Bright green
        self.HACKER_CYAN = (0, 255, 255)  # Cyan
        self.HACKER_DARK_GREEN = (0, 200, 0)  # Darker green
        self.HACKER_BG = (5, 5, 10)  # Very dark blue-black
        self.HACKER_TEXT_BG = (0, 0, 0)  # Pure black
        self.HACKER_BORDER = (0, 255, 100)  # Green-cyan border
        
        # Current scene state
        self.current_background = None
        self.current_character_sprite = None
        self.current_text = ""
        
        # Button state
        self.buttons = []
        self.selected_choice = None
        self.hovered_button_index = None  # Track which button is being hovered
    
    def _parse_rich_markup(self, text: str) -> list:
        """
        Parse Rich markup and return list of (text, color, bold) tuples.
        Converts Rich markup to hacker/cyberpunk colors (Mr. Robot theme).
        """
        import re
        segments = []
        # Color mapping from Rich colors to hacker theme RGB tuples
        color_map = {
            'red': (255, 0, 100),  # Bright red-pink (error/warning)
            'bright_red': (255, 50, 150),  # Bright pink-red
            'green': (0, 255, 0),  # Terminal green
            'bright_green': (100, 255, 100),  # Bright green
            'yellow': (255, 255, 0),  # Yellow
            'bright_yellow': (255, 255, 150),  # Bright yellow
            'blue': (0, 150, 255),  # Blue
            'bright_blue': (100, 200, 255),  # Bright blue
            'cyan': (0, 255, 255),  # Cyan (hacker accent)
            'bright_cyan': (100, 255, 255),  # Bright cyan
            'magenta': (255, 0, 255),  # Magenta
            'white': (0, 255, 0),  # Green (default hacker text)
            'bright_white': (150, 255, 150),  # Light green
            'dim': (0, 150, 0),  # Dim green
            'bold': (0, 255, 0),  # Bright green
            'default': (0, 255, 0),  # Terminal green
        }
        
        # Simple parser for basic Rich markup
        current_text = ""
        current_color = (255, 255, 255)  # Default white
        is_bold = False
        i = 0
        
        while i < len(text):
            if text[i] == '[' and i + 1 < len(text):
                # Check for closing tag
                if text[i+1] == '/':
                    # Closing tag - find the ']'
                    end = text.find(']', i)
                    if end != -1:
                        # Save current segment
                        if current_text:
                            segments.append((current_text, current_color, is_bold))
                            current_text = ""
                        tag = text[i+2:end]
                        if tag == 'bold' or tag == '/bold':
                            is_bold = False
                        elif tag in color_map:
                            current_color = (255, 255, 255)  # Reset to white
                        i = end + 1
                        continue
                else:
                    # Opening tag - find the ']'
                    end = text.find(']', i)
                    if end != -1:
                        # Save current segment
                        if current_text:
                            segments.append((current_text, current_color, is_bold))
                            current_text = ""
                        tag = text[i+1:end].lower()
                        if tag == 'bold':
                            is_bold = True
                        elif tag in color_map:
                            current_color = color_map[tag]
                        elif tag.startswith('bold ') or tag.endswith(' bold'):
                            # Handle "bold red" or "red bold"
                            parts = tag.split()
                            is_bold = True
                            for part in parts:
                                if part in color_map and part != 'bold':
                                    current_color = color_map[part]
                                    break
                        i = end + 1
                        continue
            
            current_text += text[i]
            i += 1
        
        # Add remaining text
        if current_text:
            segments.append((current_text, current_color, is_bold))
        
        # If no markup found, return whole text
        if not segments:
            return [(text, (255, 255, 255), False)]
        
        return segments
    
    def _strip_rich_markup(self, text: str) -> str:
        """
        Strip Rich markup tags from text for pygame rendering.
        Removes tags like [bold], [red], [/bold], etc.
        """
        import re
        # Remove Rich markup tags: [tag], [/tag], [tag]content[/tag]
        text = re.sub(r'\[/?[^\]]+\]', '', text)
        return text
    
    def _has_emoji(self, text: str) -> bool:
        """
        Check if text contains any emoji characters.
        Uses comprehensive emoji Unicode ranges.
        """
        if not self.emoji_supported:
            return False
        
        for char in text:
            code_point = ord(char)
            # Comprehensive emoji ranges
            if (code_point >= 0x1F300 and code_point <= 0x1F9FF) or \
               (code_point >= 0x1F600 and code_point <= 0x1F64F) or \
               (code_point >= 0x1F680 and code_point <= 0x1F6FF) or \
               (code_point >= 0x2600 and code_point <= 0x26FF) or \
               (code_point >= 0x2700 and code_point <= 0x27BF) or \
               (code_point >= 0x1F900 and code_point <= 0x1F9FF) or \
               (code_point >= 0x1F1E0 and code_point <= 0x1F1FF) or \
               (code_point >= 0x1F000 and code_point <= 0x1F02F) or \
               (code_point >= 0x1F0A0 and code_point <= 0x1F0FF):
                return True
        return False
    
    def _replace_emojis_with_text(self, text: str) -> str:
        """
        Replace emojis with text alternatives for pygame rendering.
        Only used as fallback if emoji font is not available.
        """
        # Map emojis to text equivalents
        emoji_replacements = {
            '😡': '[HATRED]',
            '💻': '[CODING]',
            '💰': '[MONEY]',
            '💪': '[GYM]',
            '🧠': '[THERAPY]',
            '🌙': '[NIGHT SHIFT]',
            '⚙️': '[SETTINGS]',
            '⬅️': '[BACK]',
            '⚠️': '[WARNING]',
            '🎯': '[TARGET]',
        }
        
        for emoji, replacement in emoji_replacements.items():
            text = text.replace(emoji, replacement)
        
        return text
    
    def _can_render_emoji(self) -> bool:
        """Check if current font can render emojis."""
        return self.emoji_supported
    
    def _load_image(self, path: Optional[str]) -> Optional[pygame.Surface]:
        """Load an image from path, return None if not found."""
        if not path or not os.path.exists(path):
            return None
        try:
            img = pygame.image.load(path)
            return img.convert_alpha() if path.endswith('.png') else img.convert()
        except Exception as e:
            _safe_print(f"[GUI] Error loading image {path}: {e}")
            return None
    
    def _scale_background(self, bg_surface: pygame.Surface) -> pygame.Surface:
        """Scale background to fit window while maintaining aspect ratio."""
        bg_width, bg_height = bg_surface.get_size()
        scale_x = self.WINDOW_WIDTH / bg_width
        scale_y = self.WINDOW_HEIGHT / bg_height
        scale = max(scale_x, scale_y)  # Cover entire window
        
        new_width = int(bg_width * scale)
        new_height = int(bg_height * scale)
        return pygame.transform.scale(bg_surface, (new_width, new_height))
    
    def _scale_character(self, char_surface: pygame.Surface) -> pygame.Surface:
        """Scale character sprite to appropriate size."""
        # Scale to fit ~40% of screen height
        target_height = int(self.WINDOW_HEIGHT * 0.4)
        char_width, char_height = char_surface.get_size()
        scale = target_height / char_height
        new_width = int(char_width * scale)
        new_height = int(char_height * scale)
        return pygame.transform.scale(char_surface, (new_width, new_height))
    
    def _render_text_with_shadow(self, font, text: str, color: tuple, x: int, y: int):
        """Render text with hacker-style glow effect."""
        # Render glow effect (green glow for terminal feel)
        if color == (0, 255, 0) or color == self.HACKER_GREEN or color == self.WHITE:
            # Green text gets green glow
            glow_color = (0, 100, 0)
            for offset_x, offset_y in [(1, 1), (-1, -1), (1, -1), (-1, 1), (0, 1), (0, -1), (1, 0), (-1, 0)]:
                glow_surface = font.render(text, True, glow_color)
                self.screen.blit(glow_surface, (x + offset_x, y + offset_y))
        else:
            # Other colors get black shadow
            shadow_surface = font.render(text, True, (0, 0, 0))
            self.screen.blit(shadow_surface, (x + 1, y + 1))
        
        # Render main text
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))
        return text_surface
    
    def _draw_text_box(self, text: str, y_offset: int = 0, show_prompt: bool = True):
        """Draw a hacker/terminal style text box (Mr. Robot theme)."""
        # Parse Rich markup first to get colored segments
        if not isinstance(text, str):
            text = str(text)
        
        box_height = 380  # Increased height for better spacing
        box_y = self.WINDOW_HEIGHT - box_height - y_offset
        padding = 30  # More padding
        
        # Calculate available width (account for character sprite on right)
        # Character sprite is positioned on right, typically ~300-400px wide with frame
        character_width = 0
        # Check if character sprite exists and is displayed
        if hasattr(self, 'current_character_sprite') and self.current_character_sprite is not None:
            # Character frame is ~380px wide (sprite ~300px + frame + margins)
            character_width = 400
        
        # Text box width should not overlap with character sprite
        text_box_width = self.WINDOW_WIDTH - character_width
        
        # Draw terminal-style background (pure black with scanline effect)
        bg_surface = pygame.Surface((text_box_width, box_height))
        bg_surface.fill(self.HACKER_TEXT_BG)  # Pure black
        
        # Add subtle scanline effect (every 2 pixels)
        for y in range(0, box_height, 2):
            pygame.draw.line(bg_surface, (5, 5, 5), (0, y), (text_box_width, y))
        
        self.screen.blit(bg_surface, (0, box_y))
        
        # Draw hacker-style border (green/cyan glow effect)
        border_color = self.HACKER_BORDER  # Green-cyan
        border_thickness = 2
        
        # Outer glow effect (simulated with multiple lines)
        glow_colors = [
            (0, 100, 50, 50),  # Dim outer glow
            (0, 150, 75, 100),  # Medium glow
            border_color  # Main border
        ]
        
        # Top border with glow
        for i, glow_color in enumerate(glow_colors):
            alpha = glow_color[3] if len(glow_color) > 3 else 255
            glow_surface = pygame.Surface((text_box_width, border_thickness + i * 2))
            glow_surface.set_alpha(alpha)
            glow_surface.fill(glow_color[:3])
            self.screen.blit(glow_surface, (0, box_y - i))
        
        # Bottom border with glow
        for i, glow_color in enumerate(glow_colors):
            alpha = glow_color[3] if len(glow_color) > 3 else 255
            glow_surface = pygame.Surface((text_box_width, border_thickness + i * 2))
            glow_surface.set_alpha(alpha)
            glow_surface.fill(glow_color[:3])
            self.screen.blit(glow_surface, (0, box_y + box_height - border_thickness - i * 2))
        
        # Main borders (only on left side to avoid character overlap)
        pygame.draw.rect(self.screen, border_color, (0, box_y, text_box_width, border_thickness))
        pygame.draw.rect(self.screen, border_color, (0, box_y + box_height - border_thickness, text_box_width, border_thickness))
        
        # Left side borders with terminal-style corners
        corner_size = 10
        # Top-left corner
        pygame.draw.line(self.screen, border_color, (0, box_y), (corner_size, box_y), border_thickness)
        pygame.draw.line(self.screen, border_color, (0, box_y), (0, box_y + corner_size), border_thickness)
        # Bottom-left corner
        pygame.draw.line(self.screen, border_color, (0, box_y + box_height - border_thickness), (corner_size, box_y + box_height - border_thickness), border_thickness)
        pygame.draw.line(self.screen, border_color, (0, box_y + box_height - corner_size), (0, box_y + box_height), border_thickness)
        
        # Right side border (only if no character sprite)
        if character_width == 0:
            # Top-right corner
            pygame.draw.line(self.screen, border_color, (text_box_width - corner_size, box_y), (text_box_width, box_y), border_thickness)
            pygame.draw.line(self.screen, border_color, (text_box_width, box_y), (text_box_width, box_y + corner_size), border_thickness)
            # Bottom-right corner
            pygame.draw.line(self.screen, border_color, (text_box_width - corner_size, box_y + box_height - border_thickness), (text_box_width, box_y + box_height - border_thickness), border_thickness)
            pygame.draw.line(self.screen, border_color, (text_box_width, box_y + box_height - corner_size), (text_box_width, box_y + box_height), border_thickness)
        
        # Parse and render text with hacker/terminal typography
        # Calculate available text area (accounting for padding on both sides)
        available_width = text_box_width - (padding * 2)  # Left and right padding
        line_height = 32  # Monospace line spacing
        start_y = box_y + padding
        current_y = start_y
        prompt_area_height = 60  # Space reserved for prompt at bottom
        max_text_y = box_y + box_height - prompt_area_height  # Maximum Y position for text
        
        # Split text into lines and render each with color support
        paragraphs = text.split('\n\n')
        for para_idx, paragraph in enumerate(paragraphs):
            if para_idx > 0:
                current_y += line_height // 2  # Extra space between paragraphs
            
            lines = paragraph.split('\n')
            for line in lines:
                # Check if we have room for another line
                if current_y + line_height > max_text_y:
                    break
                
                # Parse Rich markup for this line
                segments = self._parse_rich_markup(line)
                x = padding  # Start at left padding
                
                for segment_text, color, is_bold in segments:
                    if not segment_text.strip():
                        continue
                    
                    # Handle emojis - use emoji font if available
                    has_emoji = self._has_emoji(segment_text)
                    display_text = segment_text if self.emoji_supported else self._replace_emojis_with_text(segment_text)
                    
                    # Choose font (bold or regular, emoji or text)
                    if is_bold:
                        font = self.emoji_font_medium if (has_emoji and self.emoji_supported) else self.font_bold
                    else:
                        font = self.emoji_font_medium if (has_emoji and self.emoji_supported) else self.font_medium
                    
                    # Render segment with word wrapping and shadows
                    try:
                        # Split into words for proper wrapping
                        words = display_text.split(' ')
                        for word in words:
                            if not word:
                                continue
                            
                            # Measure word width (with space after it)
                            word_with_space = word + ' '
                            test_surface = font.render(word_with_space, True, (255, 255, 255))
                            word_width = test_surface.get_width()
                            
                            # Check if word fits on current line, wrap if needed
                            # Right edge of text box is at: padding + available_width = text_box_width - padding
                            max_x = text_box_width - padding
                            
                            if x + word_width > max_x:
                                # Word doesn't fit, move to next line
                                current_y += line_height
                                x = padding  # Reset to left padding
                                
                                # Check if we've exceeded the text area
                                if current_y + line_height > max_text_y:
                                    break
                            
                            # Only render if we're still within bounds
                            if current_y + line_height <= max_text_y and x + word_width <= max_x:
                                # Render with shadow for readability
                                self._render_text_with_shadow(font, word_with_space, color, x, current_y)
                                x += word_width
                            else:
                                # Out of bounds, stop rendering
                                break
                                
                    except Exception as e:
                        # Fallback: render as white text with shadow (but still check bounds)
                        try:
                            safe_text = display_text.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
                            test_surface = font.render(safe_text, True, color)
                            text_width = test_surface.get_width()
                            
                            # Check if it fits
                            if x + text_width <= text_box_width - padding and current_y + line_height <= max_text_y:
                                self._render_text_with_shadow(font, safe_text, color, x, current_y)
                                x += text_width
                        except:
                            pass
                
                # Move to next line after processing all segments
                current_y += line_height
                if current_y + line_height > max_text_y:
                    break
        
        # Draw hacker-style "Press Enter to continue" prompt
        if show_prompt:
            prompt_text = "> Press Enter to continue"
            # Terminal-style prompt (dim green with blinking cursor effect)
            prompt_color = (0, 200, 0)  # Dim green
            prompt_surface = self.font_small.render(prompt_text, True, prompt_color)
            prompt_x = self.WINDOW_WIDTH - prompt_surface.get_width() - padding
            prompt_y = box_y + box_height - 40
            # Draw with glow effect
            glow_surface = self.font_small.render(prompt_text, True, (0, 100, 0))
            self.screen.blit(glow_surface, (prompt_x + 1, prompt_y + 1))
            self.screen.blit(prompt_surface, (prompt_x, prompt_y))
            # Draw blinking cursor
            cursor_x = prompt_x + prompt_surface.get_width() + 5
            pygame.draw.rect(self.screen, self.HACKER_GREEN, (cursor_x, prompt_y, 8, prompt_surface.get_height()))
    
    def _calculate_text_height(self, option_text: str, button_width: int) -> int:
        """Calculate the height needed to display option text with proper wrapping."""
        # Strip Rich markup and handle emojis
        clean_text = self._strip_rich_markup(option_text)
        if not self.emoji_supported:
            clean_text = self._replace_emojis_with_text(clean_text)
        
        # Split by newlines first
        lines = clean_text.split('\n')
        
        # Calculate text area width (accounting for padding)
        text_area_width = button_width - 40  # 20px padding on each side
        line_height = 28
        min_height = 80  # Minimum button height (for header + padding)
        
        total_height = 0
        
        # Process each line
        for line in lines:
            if not line.strip():
                continue
            
            # Check for emojis
            has_emoji = self._has_emoji(line)
            font_to_use = self.emoji_font_small if (has_emoji and self.emoji_supported) else self.font_small
            
            # Word wrap this line
            words = line.strip().split()
            current_line = ""
            
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                test_surface = font_to_use.render(test_line, True, self.WHITE)
                text_width = test_surface.get_width()
                
                if text_width > text_area_width and current_line:
                    # This word would exceed width, so wrap
                    total_height += line_height
                    current_line = word
                else:
                    current_line = test_line
            
            # Add the remaining line
            if current_line:
                total_height += line_height
        
        # Add padding: top padding (15) + header space (28+5) + bottom padding (10)
        total_height += 15 + 28 + 5 + 10
        
        # Return max of calculated height or minimum
        return max(total_height, min_height)
    
    def _prepare_buttons(self, options: List[Tuple[str, str, str]], character: Optional[str] = None, scroll_offset: int = 0):
        """Prepare button rectangles without drawing. Returns list of button rects."""
        buttons = []
        button_spacing = 20
        button_x = 50
        
        # Calculate available width (account for character sprite on right)
        # Character sprite is positioned on right, typically ~300-400px wide with frame
        character_width = 0
        if character:
            # Reserve space for character sprite (sprite ~300px + frame + margins = ~400px)
            # Add extra margin for safety
            character_width = 450
        
        # Button width should not overlap with character sprite
        button_width = self.WINDOW_WIDTH - button_x - character_width - 50  # 50px right margin
        
        # Calculate button positioning
        bottom_margin = 50
        title_height = 80  # Reserve space for "DECISION" title at top
        available_height = self.WINDOW_HEIGHT - title_height - bottom_margin
        
        # Calculate dynamic button heights based on text content
        button_heights = []
        for option_num, difficulty_tag, option_text in options:
            height = self._calculate_text_height(option_text, button_width)
            button_heights.append(height)
        
        # Calculate total height needed
        if len(options) > 0:
            total_height = sum(button_heights) + (len(options) - 1) * button_spacing
        else:
            total_height = 0
        
        # Calculate maximum scroll offset (how much we can scroll down)
        if total_height > available_height:
            self.max_scroll_offset = total_height - available_height
        else:
            self.max_scroll_offset = 0
        
        # Clamp scroll offset to valid range
        scroll_offset = max(0, min(scroll_offset, self.max_scroll_offset))
        
        # Position buttons from top (with scroll offset applied)
        start_y = title_height + 10  # Start below title
        
        for i, (option_num, difficulty_tag, option_text) in enumerate(options):
            # Calculate y position based on cumulative heights, with scroll offset
            y_offset = sum(button_heights[:i]) + i * button_spacing
            y = start_y + y_offset - scroll_offset
            
            button_height = button_heights[i]
            button_rect = pygame.Rect(button_x, y, button_width, button_height)
            buttons.append((button_rect, option_num, option_text))
        
        return buttons
    
    def _draw_scrollbar(self):
        """Draw a scrollbar indicator on the right side when scrolling is available."""
        if self.max_scroll_offset <= 0:
            return
        
        # Scrollbar dimensions
        scrollbar_width = 8
        scrollbar_x = self.WINDOW_WIDTH - scrollbar_width - 10
        scrollbar_y_start = 80  # Below title
        scrollbar_height_total = self.WINDOW_HEIGHT - scrollbar_y_start - 50  # Above bottom margin
        
        # Calculate scrollbar thumb position and size
        viewport_height = self.WINDOW_HEIGHT - 80 - 50  # Available height for buttons
        total_content_height = self.max_scroll_offset + viewport_height
        thumb_height = max(20, int((viewport_height / total_content_height) * scrollbar_height_total))
        thumb_y = scrollbar_y_start + int((self.decision_scroll_offset / self.max_scroll_offset) * (scrollbar_height_total - thumb_height)) if self.max_scroll_offset > 0 else scrollbar_y_start
        
        # Draw scrollbar track (background)
        pygame.draw.rect(self.screen, (30, 30, 30), (scrollbar_x, scrollbar_y_start, scrollbar_width, scrollbar_height_total))
        
        # Draw scrollbar thumb
        pygame.draw.rect(self.screen, self.HACKER_CYAN, (scrollbar_x, thumb_y, scrollbar_width, thumb_height))
    
    def _draw_buttons(self, options: List[Tuple[str, str, str]], character: Optional[str] = None):
        """Draw decision buttons with better styling and hover effects."""
        # Buttons are already prepared in show_decision with scroll offset
        
        # Color scheme based on difficulty
        difficulty_colors = {
            "EASY": (50, 255, 50),      # Green
            "HARD": (255, 255, 0),      # Yellow
            "INSANE": (255, 50, 50),    # Red
            "MEDIUM": (255, 255, 50),   # Yellow
        }
        
        for i, (option_num, difficulty_tag, option_text) in enumerate(options):
            
            # Determine button color based on text content (hacker theme)
            button_color = (0, 0, 0)  # Black background
            border_color = self.HACKER_GREEN  # Default green border
            difficulty_name = None
            for diff_name, diff_color in difficulty_colors.items():
                if diff_name in option_text.upper():
                    difficulty_name = diff_name
                    # Use yellow for HARD, red for INSANE, bright green for EASY
                    if diff_name == "HARD":
                        border_color = (255, 255, 0)  # Yellow
                    elif diff_name == "INSANE":
                        border_color = (255, 0, 100)  # Red-pink
                    else:
                        border_color = self.HACKER_GREEN
                    break
            
            # Check if this button is being hovered
            is_hovered = (self.hovered_button_index == i)
            
            # Get button rect from pre-populated list
            button_rect, _, _ = self.buttons[i]
            
            # Only draw buttons that are visible on screen (with some margin for partial visibility)
            if button_rect.y + button_rect.height < 80 or button_rect.y > self.WINDOW_HEIGHT - 50:
                continue  # Skip drawing buttons outside viewport
            
            # Draw button with hacker/terminal style
            # If hovered, add slight background highlight
            if is_hovered:
                # Hovered button gets a subtle background glow
                hover_bg = pygame.Surface((button_rect.width, button_rect.height))
                hover_bg.set_alpha(40)
                hover_bg.fill(border_color)
                self.screen.blit(hover_bg, (button_rect.x, button_rect.y))
            else:
                pygame.draw.rect(self.screen, (0, 0, 0), button_rect)  # Black background
            
            # Draw border - thicker and brighter when hovered
            border_thickness = 4 if is_hovered else 2
            # Make border color brighter when hovered
            if is_hovered:
                # Brighten the border color
                hover_border_color = tuple(min(255, c + 50) for c in border_color)
            else:
                hover_border_color = border_color
            
            pygame.draw.rect(self.screen, hover_border_color, button_rect, border_thickness)
            
            # Add inner glow - stronger when hovered
            inner_rect = pygame.Rect(button_rect.x + 2, button_rect.y + 2, button_rect.width - 4, button_rect.height - 4)
            glow_surface = pygame.Surface((inner_rect.width, inner_rect.height))
            glow_alpha = 60 if is_hovered else 30
            glow_surface.set_alpha(glow_alpha)
            glow_surface.fill(border_color)
            self.screen.blit(glow_surface, (inner_rect.x, inner_rect.y))
            
            # Add outer glow effect when hovered
            if is_hovered:
                # Draw multiple layers of glow around the button
                for glow_offset in [3, 5, 7]:
                    glow_rect = pygame.Rect(
                        button_rect.x - glow_offset,
                        button_rect.y - glow_offset,
                        button_rect.width + glow_offset * 2,
                        button_rect.height + glow_offset * 2
                    )
                    glow_surface = pygame.Surface((glow_rect.width, glow_rect.height))
                    glow_alpha = max(0, 30 - glow_offset * 3)
                    glow_surface.set_alpha(glow_alpha)
                    glow_surface.fill(border_color)
                    self.screen.blit(glow_surface, (glow_rect.x, glow_rect.y))
            
            # Draw text with proper wrapping and emoji support
            clean_text = self._strip_rich_markup(option_text)
            # Only replace emojis if emoji font is not supported
            if not self.emoji_supported:
                clean_text = self._replace_emojis_with_text(clean_text)
            
            # Split text into lines (by \n)
            lines = clean_text.split('\n')
            
            # Calculate text area (leave padding)
            text_area_x = button_rect.x + 20
            text_area_y = button_rect.y + 15
            text_area_width = button_rect.width - 40
            line_height = 28  # Increased line height for readability
            
            # Draw option number and difficulty/header at top (with emoji support)
            # Use brighter color when hovered
            header_color = hover_border_color if is_hovered else border_color
            header_font = self.emoji_font_medium if self.emoji_supported else self.font_medium
            
            if difficulty_name:
                # Draw number + difficulty name as header
                header_text = f"{option_num}. {difficulty_name}"
                header_surface = header_font.render(header_text, True, header_color)
                self.screen.blit(header_surface, (text_area_x, text_area_y))
                text_area_y += line_height + 5  # Space after header
            else:
                # Draw option number as header
                header_text = f"{option_num}."
                header_surface = header_font.render(header_text, True, header_color)
                self.screen.blit(header_surface, (text_area_x, text_area_y))
                text_area_y += line_height + 5  # Space after header
            
            # Now render all lines (including first line) with word wrapping
            # Don't remove first line - render everything with proper wrapping
            # Draw stats lines with word wrapping
            for line in lines:
                if not line.strip():
                    continue
                
                # Check for emojis in the line
                has_emoji = self._has_emoji(line)
                font_to_use = self.emoji_font_small if (has_emoji and self.emoji_supported) else self.font_small
                
                # Word wrap long lines to fit within button width
                words = line.strip().split()
                current_line = ""
                
                for word in words:
                    test_line = current_line + (" " if current_line else "") + word
                    # Measure actual text width using font rendering
                    test_surface = font_to_use.render(test_line, True, self.WHITE)
                    text_width = test_surface.get_width()
                    
                    if text_width > text_area_width and current_line:
                        # Render current line and start new one
                        line_surface = font_to_use.render(current_line.strip(), True, self.WHITE)
                        self.screen.blit(line_surface, (text_area_x, text_area_y))
                        text_area_y += line_height
                        current_line = word
                    else:
                        current_line = test_line
                
                # Render remaining line
                if current_line:
                    line_surface = font_to_use.render(current_line.strip(), True, self.WHITE)
                    self.screen.blit(line_surface, (text_area_x, text_area_y))
                    text_area_y += line_height
                
                # Check if we've exceeded button height
                if text_area_y + line_height > button_rect.y + button_rect.height - 10:
                    break
    
    def _render_scene(self, character: Optional[str] = None, expression: str = "neutral", bg: Optional[str] = None):
        """Render the current scene."""
        # Load and draw background
        if bg:
            bg_path = self.asset_manager.get_background(bg)
            if bg_path:
                bg_surface = self._load_image(bg_path)
                if bg_surface:
                    bg_surface = self._scale_background(bg_surface)
                    # Center background
                    bg_x = (self.WINDOW_WIDTH - bg_surface.get_width()) // 2
                    bg_y = (self.WINDOW_HEIGHT - bg_surface.get_height()) // 2
                    self.screen.blit(bg_surface, (bg_x, bg_y))
                    self.current_background = bg_surface
        else:
            self.screen.fill(self.HACKER_BG)  # Dark blue-black background
        
        # Load and draw character
        if character:
            char_path = self.asset_manager.get_character_sprite(character, expression)
            if char_path:
                char_surface = self._load_image(char_path)
                if char_surface:
                    char_surface = self._scale_character(char_surface)
                    # Position character on the right side
                    char_x = self.WINDOW_WIDTH - char_surface.get_width() - 50
                    char_y = self.WINDOW_HEIGHT - char_surface.get_height() - 250
                    
                    # Draw frame/border around character
                    frame_padding = 10  # Padding around the character
                    frame_thickness = 4  # Border thickness
                    frame_x = char_x - frame_padding
                    frame_y = char_y - frame_padding
                    frame_width = char_surface.get_width() + (frame_padding * 2)
                    frame_height = char_surface.get_height() + (frame_padding * 2)
                    
                    # Draw outer dark border
                    pygame.draw.rect(self.screen, self.BLACK, 
                                   (frame_x, frame_y, frame_width, frame_height))
                    # Draw inner hacker-style green border
                    pygame.draw.rect(self.screen, self.HACKER_BORDER, 
                                   (frame_x, frame_y, frame_width, frame_height), 
                                   frame_thickness)
                    
                    # Draw character on top
                    self.screen.blit(char_surface, (char_x, char_y))
                    self.current_character_sprite = char_surface
    
    def ask(
        self, 
        options: tuple, 
        character: Optional[str] = None, 
        expression: str = "neutral", 
        bg: Optional[str] = None
    ) -> str:
        """Display options and wait for user selection via keyboard or direct keypress."""
        self.selected_choice = None
        
        # Render scene
        self._render_scene(character, expression, bg)
        
        # Draw prompt and options
        prompt_text = f"Enter choice ({', '.join(options)}): "
        options_text = "\n".join([f"  [{opt}]" for opt in options])
        full_text = prompt_text + "\n\n" + options_text
        
        # Draw text box with prompt
        self._draw_text_box(full_text)
        
        pygame.display.flip()
        
        # Wait for keyboard input - allow direct keypress or typed input
        input_text = ""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    # Check if a number key was pressed that matches an option
                    if event.unicode in options:
                        return event.unicode
                    elif event.key == pygame.K_RETURN:
                        if input_text.strip() in options:
                            return input_text.strip()
                        else:
                            input_text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif event.unicode.isdigit() or event.unicode.isalpha():
                        input_text += event.unicode
            
            # Redraw
            self._render_scene(character, expression, bg)
            display_text = full_text + "\n\n" + (f"Input: {input_text}" if input_text else "")
            self._draw_text_box(display_text)
            pygame.display.flip()
            self.clock.tick(self.FPS)
    
    def show_decision(
        self, 
        option_texts: list[tuple[str, str, str]],
        character: Optional[str] = None,
        expression: str = "neutral",
        bg: Optional[str] = None
    ) -> str:
        """Display decision options with buttons."""
        self.selected_choice = None
        self.buttons = []
        
        # Format option texts (apply formatting, but strip Rich markup for GUI)
        formatted_options = []
        for option_num, difficulty_tag, option_text in option_texts:
            formatted_text = TerminalInteraction.format_colonel_text(option_text)
            formatted_text = TerminalInteraction.format_hatred_text(formatted_text)
            formatted_text = TerminalInteraction.format_coding_text(formatted_text)
            formatted_text = TerminalInteraction.format_money_text(formatted_text)
            # Strip Rich markup for GUI display (keep emojis)
            formatted_text = self._strip_rich_markup(formatted_text)
            formatted_options.append((option_num, difficulty_tag, formatted_text))
        
        running = True
        self.hovered_button_index = None  # Reset hover state
        self.buttons = []  # Initialize buttons list
        self.decision_scroll_offset = 0  # Reset scroll offset
        
        while running:
            # Recalculate buttons with current scroll offset
            self.buttons = self._prepare_buttons(formatted_options, character, self.decision_scroll_offset)
            
            # Get mouse position for hover detection
            mouse_pos = pygame.mouse.get_pos()
            
            # Render scene first (before handling events)
            self._render_scene(character, expression, bg)
            
            # Draw decision title (at top) with hacker style
            title_text = "> DECISION"
            title_surface = self.font_large.render(title_text, True, self.HACKER_CYAN)
            # Add glow effect
            glow_surface = self.font_large.render(title_text, True, (0, 150, 150))
            self.screen.blit(glow_surface, (22, 22))
            self.screen.blit(title_surface, (20, 20))
            
            # Draw scrollbar if scrolling is needed
            if self.max_scroll_offset > 0:
                self._draw_scrollbar()
            
            # Check which button is being hovered (before drawing)
            self.hovered_button_index = None
            for i, (button_rect, _, _) in enumerate(self.buttons):
                # Only check buttons that are visible on screen
                if (button_rect.y + button_rect.height >= 80 and button_rect.y < self.WINDOW_HEIGHT - 50):
                    if button_rect.collidepoint(mouse_pos):
                        self.hovered_button_index = i
                        break
            
            # Draw buttons (with hover effects, pass character to avoid overlap)
            self._draw_buttons(formatted_options, character)
            
            pygame.display.flip()
            
            # Handle events after drawing
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEWHEEL:
                    # Handle mouse wheel scrolling
                    scroll_speed = 50  # Pixels per scroll
                    if event.y > 0:  # Scroll up
                        self.decision_scroll_offset = max(0, self.decision_scroll_offset - scroll_speed)
                    elif event.y < 0:  # Scroll down
                        self.decision_scroll_offset = min(self.max_scroll_offset, self.decision_scroll_offset + scroll_speed)
                elif event.type == pygame.MOUSEMOTION:
                    # Update hover state on mouse movement
                    mouse_pos = event.pos
                    self.hovered_button_index = None
                    for i, (button_rect, _, _) in enumerate(self.buttons):
                        # Only check visible buttons
                        if (button_rect.y + button_rect.height >= 80 and button_rect.y < self.WINDOW_HEIGHT - 50):
                            if button_rect.collidepoint(mouse_pos):
                                self.hovered_button_index = i
                                break
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        mouse_pos = event.pos
                        # Check button clicks (only visible buttons)
                        for button_rect, option_num, _ in self.buttons:
                            if (button_rect.y + button_rect.height >= 80 and button_rect.y < self.WINDOW_HEIGHT - 50):
                                if button_rect.collidepoint(mouse_pos):
                                    return option_num
                elif event.type == pygame.KEYDOWN:
                    # Handle keyboard scrolling
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        scroll_speed = 50
                        self.decision_scroll_offset = max(0, self.decision_scroll_offset - scroll_speed)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        scroll_speed = 50
                        self.decision_scroll_offset = min(self.max_scroll_offset, self.decision_scroll_offset + scroll_speed)
                    elif event.key == pygame.K_PAGEUP:
                        scroll_speed = 300
                        self.decision_scroll_offset = max(0, self.decision_scroll_offset - scroll_speed)
                    elif event.key == pygame.K_PAGEDOWN:
                        scroll_speed = 300
                        self.decision_scroll_offset = min(self.max_scroll_offset, self.decision_scroll_offset + scroll_speed)
                    # Allow keyboard selection too
                    for option_num, _, _ in formatted_options:
                        if event.unicode == option_num:
                            return option_num
            
            self.clock.tick(self.FPS)
    
    def show_outcome(
        self, 
        outcome_text: str,
        character: Optional[str] = None,
        expression: str = "neutral",
        bg: Optional[str] = None
    ) -> None:
        """Display outcome message."""
        # Format text
        formatted_text = TerminalInteraction.format_colonel_text(outcome_text)
        formatted_text = TerminalInteraction.format_hatred_text(formatted_text)
        formatted_text = TerminalInteraction.format_coding_text(formatted_text)
        formatted_text = TerminalInteraction.format_money_text(formatted_text)
        
        # Render scene
        self._render_scene(character, expression, bg)
        
        # Draw outcome box
        box_height = 150
        box_y = self.WINDOW_HEIGHT - box_height - 20
        
        outcome_surface = pygame.Surface((self.WINDOW_WIDTH, box_height))
        outcome_surface.set_alpha(250)
        outcome_surface.fill(self.HACKER_TEXT_BG)  # Pure black
        self.screen.blit(outcome_surface, (0, box_y))
        
        # Hacker-style border
        pygame.draw.rect(self.screen, self.HACKER_CYAN, (0, box_y, self.WINDOW_WIDTH, box_height), 2)
        
        # Draw title with hacker style
        title_text = "> OUTCOME"
        title_surface = self.font_large.render(title_text, True, self.HACKER_CYAN)
        # Add glow effect
        glow_surface = self.font_large.render(title_text, True, (0, 150, 150))
        self.screen.blit(glow_surface, (22, box_y + 12))
        self.screen.blit(title_surface, (20, box_y + 10))
        
        # Strip Rich markup and handle emojis
        display_text = self._strip_rich_markup(formatted_text)
        display_text = display_text if self.emoji_supported else self._replace_emojis_with_text(display_text)
        
        # Word wrap the outcome text with emoji support
        words = display_text.split(' ')
        lines = []
        current_line = []
        current_width = 0
        max_width = self.WINDOW_WIDTH - 40
        
        for word in words:
            # Check if word contains emoji
            has_emoji = self._has_emoji(word)
            font_to_use = self.emoji_font_medium if (has_emoji and self.emoji_supported) else self.font_medium
            
            # Measure word width with appropriate font
            word_with_space = word + ' '
            word_surface = font_to_use.render(word_with_space, True, self.HACKER_GREEN)
            word_width = word_surface.get_width()
            
            # Check if adding this word would exceed width
            if current_width + word_width > max_width and current_line:
                # Save current line and start new one
                lines.append(' '.join(current_line))
                current_line = [word]
                current_width = word_width
            else:
                current_line.append(word)
                current_width += word_width
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw wrapped lines with proper font for each line (checking for emojis)
        line_height = 28
        start_y = box_y + 50
        for i, line in enumerate(lines[:6]):  # Max 6 lines for outcome
            # Check if line has emoji for rendering
            line_has_emoji = self._has_emoji(line)
            render_font = self.emoji_font_medium if (line_has_emoji and self.emoji_supported) else self.font_medium
            
            # Render with shadow for readability
            self._render_text_with_shadow(render_font, line, self.HACKER_GREEN, 20, start_y + i * line_height)
        
        # Draw "Press Enter to continue" prompt
        prompt_text = "Press Enter to continue"
        prompt_surface = self.font_small.render(prompt_text, True, self.HACKER_CYAN)
        prompt_x = self.WINDOW_WIDTH - prompt_surface.get_width() - 20
        prompt_y = box_y + box_height - 30
        self.screen.blit(prompt_surface, (prompt_x, prompt_y))
        
        pygame.display.flip()
        
        # Wait for Enter key only
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        waiting = False
            
            pygame.display.flip()
            self.clock.tick(self.FPS)
    
    def print_text(
        self, 
        text: str,
        character: Optional[str] = None,
        expression: str = "neutral",
        bg: Optional[str] = None,
        wait_for_input: bool = True,
        animated: bool = False,
        animation_delay: float = 0.03
    ) -> None:
        """Display text.
        
        Args:
            text: Text to display
            character: Optional character name for visual display
            expression: Character expression/emotion
            bg: Optional background scene identifier
            wait_for_input: If True, waits for Enter key. If False, just displays text without waiting.
            animated: If True, displays text with typewriter effect character-by-character
            animation_delay: Delay between characters in seconds (default 0.03)
        """
        # Format text
        formatted_text = TerminalInteraction.format_colonel_text(text)
        formatted_text = TerminalInteraction.format_hatred_text(formatted_text)
        formatted_text = TerminalInteraction.format_coding_text(formatted_text)
        formatted_text = TerminalInteraction.format_money_text(formatted_text)
        
        if animated:
            # Display with typewriter effect
            self._print_text_animated(formatted_text, character, expression, bg, wait_for_input, animation_delay)
        else:
            # Display normally
            # Render scene
            self._render_scene(character, expression, bg)
            
            # Draw text box (show prompt only if waiting for input)
            self._draw_text_box(formatted_text, show_prompt=wait_for_input)
            
            pygame.display.flip()
            
            # Wait for Enter key only if wait_for_input is True
            if wait_for_input:
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                                waiting = False
                    
                    pygame.display.flip()
                    self.clock.tick(self.FPS)
    
    def _print_text_animated(
        self,
        text: str,
        character: Optional[str] = None,
        expression: str = "neutral",
        bg: Optional[str] = None,
        wait_for_input: bool = True,
        delay: float = 0.03
    ) -> None:
        """Display text with typewriter effect character-by-character."""
        # Render scene (static background)
        self._render_scene(character, expression, bg)
        
        # Split text into characters, preserving newlines and spaces
        # We'll build the text progressively
        displayed_text = ""
        full_text = text
        
        # Calculate timing - use clock for smooth animation
        last_char_time = 0
        char_delay_ms = int(delay * 1000)  # Convert to milliseconds
        
        running = True
        skip_animation = False
        
        while running:
            current_time = pygame.time.get_ticks()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        if len(displayed_text) < len(full_text):
                            # Skip animation, show full text
                            displayed_text = full_text
                            skip_animation = True
                        else:
                            # Animation complete, exit
                            if wait_for_input:
                                running = False
                            else:
                                return
                    elif event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
                        # Allow spacebar or ESC to skip animation
                        displayed_text = full_text
                        skip_animation = True
            
            # Add next character if enough time has passed and animation not skipped
            if not skip_animation and len(displayed_text) < len(full_text):
                if current_time - last_char_time >= char_delay_ms:
                    # Add next character(s)
                    # Handle newlines and spaces specially for better flow
                    next_char = full_text[len(displayed_text)]
                    if next_char == '\n':
                        displayed_text += '\n'
                    elif next_char == ' ':
                        displayed_text += ' '
                    else:
                        displayed_text += next_char
                    
                    last_char_time = current_time
            elif skip_animation and len(displayed_text) < len(full_text):
                # Instantly complete animation
                displayed_text = full_text
            
            # Render scene
            self._render_scene(character, expression, bg)
            
            # Draw text box with current displayed text
            self._draw_text_box(displayed_text, show_prompt=(len(displayed_text) >= len(full_text) and wait_for_input))
            
            pygame.display.flip()
            self.clock.tick(self.FPS)
            
            # If animation is complete and not waiting for input, exit
            if len(displayed_text) >= len(full_text) and not wait_for_input:
                return
    
    def continue_prompt(
        self,
        character: Optional[str] = None,
        expression: str = "neutral",
        bg: Optional[str] = None
    ) -> None:
        """Display a "Press Enter to continue" prompt in GUI mode."""
        # Render scene if provided
        if bg or character:
            self._render_scene(character, expression, bg)
        else:
            # Just show black background
            self.screen.fill(self.BLACK)
        
        # Draw prompt box
        box_height = 100
        box_y = self.WINDOW_HEIGHT - box_height - 20
        
        prompt_surface = pygame.Surface((self.WINDOW_WIDTH, box_height))
        prompt_surface.set_alpha(250)
        prompt_surface.fill(self.HACKER_TEXT_BG)  # Pure black
        self.screen.blit(prompt_surface, (0, box_y))
        
        pygame.draw.rect(self.screen, self.HACKER_CYAN, (0, box_y, self.WINDOW_WIDTH, box_height), 2)
        
        # Draw prompt text with hacker style
        prompt_text = "> PRESS ENTER TO CONTINUE"
        text_surface = self.font_medium.render(prompt_text, True, self.HACKER_CYAN)
        text_x = (self.WINDOW_WIDTH - text_surface.get_width()) // 2
        text_y = box_y + (box_height - text_surface.get_height()) // 2
        self.screen.blit(text_surface, (text_x, text_y))
        
        pygame.display.flip()
        
        # Wait for Enter key only
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        waiting = False
            
            pygame.display.flip()
            self.clock.tick(self.FPS)