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
        
        # Load fonts
        try:
            self.font_large = pygame.font.Font(None, 36)
            self.font_medium = pygame.font.Font(None, 24)
            self.font_small = pygame.font.Font(None, 18)
        except:
            # Fallback to default font
            self.font_large = pygame.font.SysFont('arial', 36)
            self.font_medium = pygame.font.SysFont('arial', 24)
            self.font_small = pygame.font.SysFont('arial', 18)
        
        # Current scene state
        self.current_background = None
        self.current_character_sprite = None
        self.current_text = ""
        
        # Button state
        self.buttons = []
        self.selected_choice = None
        
    def _load_image(self, path: Optional[str]) -> Optional[pygame.Surface]:
        """Load an image from path, return None if not found."""
        if not path or not os.path.exists(path):
            return None
        try:
            img = pygame.image.load(path)
            return img.convert_alpha() if path.endswith('.png') else img.convert()
        except Exception as e:
            print(f"[GUI] Error loading image {path}: {e}")
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
    
    def _draw_text_box(self, text: str, y_offset: int = 0):
        """Draw a text box at the bottom of the screen."""
        box_height = 200
        box_y = self.WINDOW_HEIGHT - box_height - y_offset
        
        # Draw semi-transparent background
        text_surface = pygame.Surface((self.WINDOW_WIDTH, box_height))
        text_surface.set_alpha(220)
        text_surface.fill(self.BLACK)
        self.screen.blit(text_surface, (0, box_y))
        
        # Draw border
        pygame.draw.rect(self.screen, self.WHITE, (0, box_y, self.WINDOW_WIDTH, box_height), 2)
        
        # Render text (word wrap)
        words = text.split(' ')
        lines = []
        current_line = []
        current_width = 0
        
        for word in words:
            word_surface = self.font_medium.render(word + ' ', True, self.WHITE)
            word_width = word_surface.get_width()
            
            if current_width + word_width > self.WINDOW_WIDTH - 40:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_width = word_width
            else:
                current_line.append(word)
                current_width += word_width
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw lines
        line_height = 30
        start_y = box_y + 20
        for i, line in enumerate(lines[:5]):  # Max 5 lines
            text_surface = self.font_medium.render(line, True, self.WHITE)
            self.screen.blit(text_surface, (20, start_y + i * line_height))
    
    def _draw_buttons(self, options: List[Tuple[str, str, str]]):
        """Draw decision buttons."""
        self.buttons = []
        button_height = 60
        button_spacing = 10
        # Position buttons at the bottom, with some padding
        total_height = len(options) * (button_height + button_spacing) - button_spacing
        start_y = self.WINDOW_HEIGHT - total_height - 20  # 20px from bottom
        
        for i, (option_num, difficulty_tag, option_text) in enumerate(options):
            y = start_y + i * (button_height + button_spacing)
            
            # Format text (remove Rich markup for now)
            clean_text = option_text.replace('[bold]', '').replace('[/bold]', '')
            clean_text = clean_text.replace('[green]', '').replace('[/green]', '')
            clean_text = clean_text.replace('[yellow]', '').replace('[/yellow]', '')
            clean_text = clean_text.replace('[red]', '').replace('[/red]', '')
            
            # Truncate if too long
            if len(clean_text) > 80:
                clean_text = clean_text[:77] + "..."
            
            button_text = f"{option_num}. {clean_text}"
            
            # Button rect
            button_rect = pygame.Rect(20, y, self.WINDOW_WIDTH - 40, button_height)
            self.buttons.append((button_rect, option_num, button_text))
            
            # Draw button
            pygame.draw.rect(self.screen, self.DARK_GRAY, button_rect)
            pygame.draw.rect(self.screen, self.WHITE, button_rect, 2)
            
            # Draw text
            text_surface = self.font_small.render(button_text, True, self.WHITE)
            text_x = button_rect.x + 10
            text_y = button_rect.y + (button_height - text_surface.get_height()) // 2
            self.screen.blit(text_surface, (text_x, text_y))
    
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
            self.screen.fill(self.BLACK)
        
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
                    # Draw inner white border
                    pygame.draw.rect(self.screen, self.WHITE, 
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
        """Display options and wait for user selection via keyboard."""
        self.selected_choice = None
        
        # Render scene
        self._render_scene(character, expression, bg)
        
        # Draw prompt
        prompt_text = f"Enter choice ({', '.join(options)}): "
        text_surface = self.font_medium.render(prompt_text, True, self.WHITE)
        self.screen.blit(text_surface, (20, 20))
        
        pygame.display.flip()
        
        # Wait for keyboard input
        input_text = ""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if input_text.strip() in options:
                            return input_text.strip()
                        else:
                            input_text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode
            
            # Redraw
            self._render_scene(character, expression, bg)
            prompt_surface = self.font_medium.render(prompt_text + input_text, True, self.WHITE)
            self.screen.blit(prompt_surface, (20, 20))
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
        
        # Format option texts (apply formatting)
        formatted_options = []
        for option_num, difficulty_tag, option_text in option_texts:
            formatted_text = TerminalInteraction.format_colonel_text(option_text)
            formatted_text = TerminalInteraction.format_hatred_text(formatted_text)
            formatted_text = TerminalInteraction.format_coding_text(formatted_text)
            formatted_text = TerminalInteraction.format_money_text(formatted_text)
            formatted_options.append((option_num, difficulty_tag, formatted_text))
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        mouse_pos = event.pos
                        for button_rect, option_num, _ in self.buttons:
                            if button_rect.collidepoint(mouse_pos):
                                return option_num
                elif event.type == pygame.KEYDOWN:
                    # Allow keyboard selection too
                    for option_num, _, _ in formatted_options:
                        if event.unicode == option_num:
                            return option_num
            
            # Render scene
            self._render_scene(character, expression, bg)
            
            # Draw decision title (at top)
            title_surface = self.font_large.render("DECISION", True, self.YELLOW)
            self.screen.blit(title_surface, (20, 20))
            
            # Draw buttons (at bottom)
            self._draw_buttons(formatted_options)
            
            pygame.display.flip()
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
        outcome_surface.set_alpha(220)
        outcome_surface.fill(self.BLACK)
        self.screen.blit(outcome_surface, (0, box_y))
        
        pygame.draw.rect(self.screen, self.CYAN, (0, box_y, self.WINDOW_WIDTH, box_height), 2)
        
        # Draw title
        title_surface = self.font_large.render("OUTCOME", True, self.CYAN)
        self.screen.blit(title_surface, (20, box_y + 10))
        
        # Draw text
        text_surface = self.font_medium.render(formatted_text, True, self.WHITE)
        self.screen.blit(text_surface, (20, box_y + 50))
        
        # Draw "Press Enter to continue" prompt
        prompt_text = "Press Enter to continue"
        prompt_surface = self.font_small.render(prompt_text, True, self.CYAN)
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
        bg: Optional[str] = None
    ) -> None:
        """Display text."""
        # Format text
        formatted_text = TerminalInteraction.format_colonel_text(text)
        formatted_text = TerminalInteraction.format_hatred_text(formatted_text)
        formatted_text = TerminalInteraction.format_coding_text(formatted_text)
        formatted_text = TerminalInteraction.format_money_text(formatted_text)
        
        # Render scene
        self._render_scene(character, expression, bg)
        
        # Draw text box
        self._draw_text_box(formatted_text)
        
        # Draw "Press Enter to continue" prompt
        prompt_text = "Press Enter to continue"
        prompt_surface = self.font_small.render(prompt_text, True, self.WHITE)
        prompt_x = self.WINDOW_WIDTH - prompt_surface.get_width() - 20
        prompt_y = self.WINDOW_HEIGHT - 30
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
