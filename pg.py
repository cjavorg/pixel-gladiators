import pygame
import sys
import os

# Initialize pygame testing
pygame.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pixel Gladiators")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Load background images
try:
    GAME_BACKGROUND = pygame.image.load(os.path.join(os.path.dirname(__file__), "pg-background.jpg"))
    GAME_BACKGROUND = pygame.transform.scale(GAME_BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))

    LOBBY_BACKGROUND = pygame.image.load(os.path.join(os.path.dirname(__file__), "menu-page-bg.jpg"))
    LOBBY_BACKGROUND = pygame.transform.scale(LOBBY_BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))

    MENU_BACKGROUND = pygame.image.load(os.path.join(os.path.dirname(__file__), "lobby.jpg"))
    MENU_BACKGROUND = pygame.transform.scale(MENU_BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))

    MENU_OVERLAY = pygame.image.load(os.path.join(os.path.dirname(__file__), "menu-bg.png"))
    MENU_OVERLAY = pygame.transform.scale(MENU_OVERLAY, (SCREEN_WIDTH/1.5, SCREEN_HEIGHT))
except pygame.error as e:
    raise FileNotFoundError(f"Background image not found. Please ensure all image files are in the same directory as the script. Error: {e}")

# Font settings
FONT_PATH = os.path.join(os.path.dirname(__file__), "Minercraftory.ttf")
if not os.path.exists(FONT_PATH):
    raise FileNotFoundError(f"Font file not found at {FONT_PATH}. Please ensure the file is in the same directory as the script.")
FONT = pygame.font.Font(FONT_PATH, 24)
TITLE_FONT = pygame.font.Font(FONT_PATH, 64)
SUBTITLE_FONT = pygame.font.Font(FONT_PATH, 38)
BUTTON_FONT = pygame.font.Font(FONT_PATH, 20)  # Smaller font for button text

# Clock
clock = pygame.time.Clock()
FPS = 60

# Player settings
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
PLAYER_SPEED = 5
GRAVITY = 0.8
JUMP_SPEED = -15

# Sword settings
SWORD_WIDTH = 10
SWORD_HEIGHT = 40
SWORD_DAMAGE = 5  # Damage inflicted by a sword hit

# Add to the constants at the top
FULLSCREEN = False  # Initial fullscreen state

# Add to the constants section
DEFAULT_PLAYER1_NAME = "Player 1"
DEFAULT_PLAYER2_NAME = "Player 2"
CUSTOMIZE_FONT = pygame.font.Font(FONT_PATH, 48)  # Smaller font for customize screen title

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = PLAYER_SPEED
        self.health = 100
        self.velocity_y = 0
        self.jumping = False

    def update(self, keys, up, down, left, right):
        # Horizontal movement
        if keys[left] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[right] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

        # Jumping and gravity
        if keys[up] and not self.jumping:
            self.velocity_y = JUMP_SPEED
            self.jumping = True

        # Apply gravity
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

        # Check floor collision
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.velocity_y = 0
            self.jumping = False

# Sword class
class Sword(pygame.sprite.Sprite):
    def __init__(self, player, color):
        super().__init__()
        self.image = pygame.Surface((SWORD_WIDTH, SWORD_HEIGHT))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.player = player
        self.attacking = False

    def update(self):
        if self.attacking:
            self.rect.center = self.player.rect.center
        else:
            self.rect.topleft = (-100, -100)  # Move the sword off-screen when not attacking

class Button:
    def __init__(self, x, y, width, height, text, color, small_text=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.is_hovered = False
        self.small_text = small_text

    def draw(self, surface):
        color = (min(self.color[0] + 30, 255),
                min(self.color[1] + 30, 255),
                min(self.color[2] + 30, 255)) if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        # Use smaller font if small_text is True
        font = BUTTON_FONT if self.small_text else FONT
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class Game:
    def __init__(self):
        self.state = "MENU"
        # Store original screen dimensions
        self.original_width = SCREEN_WIDTH
        self.original_height = SCREEN_HEIGHT
        self.is_fullscreen = FULLSCREEN

        # Add fullscreen button
        self.fullscreen_button = Button(SCREEN_WIDTH - 220, 20, 200, 50, "Fullscreen", (100, 100, 200))

        # Main menu buttons
        self.start_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2, 200, 50, "Start Game", (100, 200, 100))
        # Game over button - added small_text=True
        self.menu_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 100, 200, 50, "Back to Lobby", (100, 200, 100), small_text=True)
        # Prep screen buttons
        self.play_button = Button(SCREEN_WIDTH - 220, SCREEN_HEIGHT - 80, 200, 50, "Play!", (100, 200, 100))
        # Move controls button to the left side within the overlay
        self.controls_button = Button(50, 150, 200, 50, "Controls", (100, 100, 200))
        self.show_controls = False
        self.winner = None

        # Add customization screen buttons
        self.start_fight_button = Button(SCREEN_WIDTH - 220, SCREEN_HEIGHT - 80, 200, 50, "Start Fight!", (100, 200, 100))
        self.player1_name_button = Button(100, 200, 200, 50, DEFAULT_PLAYER1_NAME, (200, 100, 100))
        self.player2_name_button = Button(SCREEN_WIDTH - 300, 200, 200, 50, DEFAULT_PLAYER2_NAME, (100, 100, 200))

        # Player names
        self.player1_name = DEFAULT_PLAYER1_NAME
        self.player2_name = DEFAULT_PLAYER2_NAME

        # Text input state
        self.active_input = None
        self.input_text = ""

        self.setup_game_objects()

    def setup_game_objects(self):
        # Initialize players
        self.player1 = Player(100, SCREEN_HEIGHT // 2, RED)
        self.player2 = Player(SCREEN_WIDTH - 150, SCREEN_HEIGHT // 2, BLUE)

        # Initialize swords
        self.sword1 = Sword(self.player1, RED)
        self.sword2 = Sword(self.player2, BLUE)

        # Groups
        self.all_sprites = pygame.sprite.Group(self.player1, self.player2, self.sword1, self.sword2)

    def toggle_fullscreen(self):
        global screen, SCREEN_WIDTH, SCREEN_HEIGHT
        self.is_fullscreen = not self.is_fullscreen

        if self.is_fullscreen:
            # Get the current display info
            display_info = pygame.display.Info()
            SCREEN_WIDTH = display_info.current_w
            SCREEN_HEIGHT = display_info.current_h
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
            self.fullscreen_button.text = "Unfullscreen"  # Change button text
        else:
            SCREEN_WIDTH = self.original_width
            SCREEN_HEIGHT = self.original_height
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.fullscreen_button.text = "Fullscreen"  # Change button text back

        # Update button positions for new screen size
        self.update_button_positions()

        # Rescale background images
        self.scale_backgrounds()

    def scale_backgrounds(self):
        global GAME_BACKGROUND, LOBBY_BACKGROUND, MENU_BACKGROUND, MENU_OVERLAY

        GAME_BACKGROUND = pygame.transform.scale(GAME_BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))
        LOBBY_BACKGROUND = pygame.transform.scale(LOBBY_BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))
        MENU_BACKGROUND = pygame.transform.scale(MENU_BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))
        MENU_OVERLAY = pygame.transform.scale(MENU_OVERLAY, (SCREEN_WIDTH/1.5, SCREEN_HEIGHT))

    def update_button_positions(self):
        # Update button positions based on new screen size
        self.fullscreen_button.rect.topleft = (SCREEN_WIDTH - 220, 20)
        self.start_button.rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
        self.menu_button.rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100)
        self.play_button.rect.bottomright = (SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20)
        self.controls_button.rect.topleft = (50, 150)
        self.start_fight_button.rect.bottomright = (SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20)
        self.player1_name_button.rect.topleft = (100, 200)
        self.player2_name_button.rect.topleft = (SCREEN_WIDTH - 300, 200)

    def run_menu(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if self.start_button.handle_event(event):
                self.state = "PREP"
            if self.fullscreen_button.handle_event(event):
                self.toggle_fullscreen()

        # Draw menu background with overlay
        screen.blit(MENU_BACKGROUND, (0, 0))

        # Draw title
        title_text = TITLE_FONT.render("Pixel Gladiators", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
        screen.blit(title_text, title_rect)

        self.start_button.draw(screen)
        self.fullscreen_button.draw(screen)
        return True

    def run_prep_screen(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if self.play_button.handle_event(event):
                self.state = "CUSTOMIZE"  # Changed from "PLAYING" to "CUSTOMIZE"
            if self.controls_button.handle_event(event):
                self.show_controls = not self.show_controls
            if self.fullscreen_button.handle_event(event):
                self.toggle_fullscreen()

        # Draw lobby background
        screen.blit(LOBBY_BACKGROUND, (0, 0))
        screen.blit(MENU_OVERLAY, (0, 0))

        # Draw title in the menu overlay
        title_text = SUBTITLE_FONT.render("Pixel Gladiators", True, WHITE)
        # Position the title at 1/4 of screen width (center of left half) and near the top
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//3.5, 80))
        screen.blit(title_text, title_rect)

        if self.show_controls:
            # Increase menu width to accommodate longer text
            menu_width = 300  # Increased from 300
            menu_height = 400
            menu_x = SCREEN_WIDTH - menu_width - 20
            menu_y = (SCREEN_HEIGHT - menu_height) // 2

            # Draw semi-transparent menu background
            menu_surface = pygame.Surface((menu_width, menu_height))
            menu_surface.fill((50, 50, 50))
            menu_surface.set_alpha(200)
            screen.blit(menu_surface, (menu_x, menu_y))

            # Draw menu border
            pygame.draw.rect(screen, WHITE, (menu_x, menu_y, menu_width, menu_height), 2)

            # Draw "Controls" header
            controls_text = FONT.render("Controls", True, WHITE)
            controls_rect = controls_text.get_rect(center=(menu_x + menu_width // 2.5, menu_y + 30))
            screen.blit(controls_text, controls_rect)

            # Draw instructions in the menu with better spacing
            instructions = [
                ("Player 1", ""),
                ("WASD", "Movement"),
                ("SPACE", "Attack"),
                ("", ""),
                ("Player 2", ""),
                ("Arrow Keys", "Movement"),
                ("ENTER", "Attack")
            ]

            y_offset = menu_y + 80
            for control, action in instructions:
                if control:  # If it's not just a spacer
                    if control in ["Player 1:", "Player 2:"]:
                        # Draw player headers in a different style
                        text = FONT.render(control, True, (200, 200, 100))
                        screen.blit(text, (menu_x + 20, y_offset))
                    else:
                        # Draw control key with adjusted spacing
                        control_text = FONT.render(control, True, WHITE)
                        screen.blit(control_text, (menu_x + 30, y_offset))

                        # Draw action description with more space
                        action_text = FONT.render(action, True, WHITE)
                        # Adjust position to prevent overlap
                        action_x = menu_x + menu_width - 160  # Moved further left and adjusted for wider menu
                        screen.blit(action_text, (action_x, y_offset))

                y_offset += 50  # Increased vertical spacing further

        self.controls_button.draw(screen)
        self.fullscreen_button.draw(screen)
        self.play_button.draw(screen)
        return True

    def run_customize_screen(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and self.active_input:
                if event.key == pygame.K_RETURN:
                    # Save the name and exit input mode
                    if self.active_input == 1:
                        self.player1_name = self.input_text if self.input_text else DEFAULT_PLAYER1_NAME
                    else:
                        self.player2_name = self.input_text if self.input_text else DEFAULT_PLAYER2_NAME
                    self.active_input = None
                    self.input_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                elif event.key == pygame.K_ESCAPE:  # Add escape to cancel editing
                    self.active_input = None
                    self.input_text = ""
                else:
                    # Limit name length to 12 characters
                    if len(self.input_text) < 12:
                        self.input_text += event.unicode
            # Handle mouse clicks outside input boxes to deselect
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                input1_rect = pygame.Rect(100, 260, 200, 40)
                input2_rect = pygame.Rect(SCREEN_WIDTH - 300, 260, 200, 40)
                if not input1_rect.collidepoint(mouse_pos) and not input2_rect.collidepoint(mouse_pos):
                    if self.active_input == 1:
                        self.player1_name = self.input_text if self.input_text else self.player1_name
                    elif self.active_input == 2:
                        self.player2_name = self.input_text if self.input_text else self.player2_name
                    self.active_input = None
                    self.input_text = ""

            if self.start_fight_button.handle_event(event):
                self.state = "PLAYING"
            elif self.fullscreen_button.handle_event(event):
                self.toggle_fullscreen()

        # Draw background
        screen.blit(LOBBY_BACKGROUND, (0, 0))

        # Draw title with smaller font
        title_text = CUSTOMIZE_FONT.render("Customize Characters", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 80))
        screen.blit(title_text, title_rect)

        # Draw player sections
        self.draw_player_section(1)
        self.draw_player_section(2)

        # Draw name input boxes with text input styling
        self.draw_name_input(1)
        self.draw_name_input(2)

        # Draw buttons
        self.start_fight_button.draw(screen)
        self.fullscreen_button.draw(screen)

        return True

    def draw_name_input(self, player_num):
        x = 100 if player_num == 1 else SCREEN_WIDTH - 300
        y = 260
        width = 200
        height = 40

        # Create input box rect
        input_rect = pygame.Rect(x, y, width, height)

        # Handle mouse clicks on the input box
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]  # Left mouse button
        if mouse_clicked and input_rect.collidepoint(mouse_pos):
            self.active_input = player_num
            self.input_text = self.player1_name if player_num == 1 else self.player2_name

        # Draw input box background
        box_color = (100, 100, 100) if self.active_input == player_num else (70, 70, 70)
        pygame.draw.rect(screen, box_color, input_rect)
        pygame.draw.rect(screen, WHITE, input_rect, 2)  # Border

        # Draw current name or active input text
        if self.active_input == player_num:
            text = self.input_text + "_"  # Add cursor
        else:
            text = self.player1_name if player_num == 1 else self.player2_name

        text_surface = FONT.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=input_rect.center)
        screen.blit(text_surface, text_rect)

        # Draw "Click to edit" hint if not active
        if not self.active_input:
            hint_text = BUTTON_FONT.render("Click to edit", True, (150, 150, 150))
            hint_rect = hint_text.get_rect(center=(x + width//2, y + height + 20))
            screen.blit(hint_text, hint_rect)

    def draw_player_section(self, player_num):
        x = 100 if player_num == 1 else SCREEN_WIDTH - 300
        y = 150

        # Draw section title
        section_text = SUBTITLE_FONT.render(f"Player {player_num}", True, WHITE)
        section_rect = section_text.get_rect(topleft=(x, y))
        screen.blit(section_text, section_rect)

        # Draw placeholder for future skin selection
        skin_text = FONT.render("Skin Selection", True, WHITE)
        screen.blit(skin_text, (x, y + 200))  # Moved down to accommodate name input

        # Draw skin preview box
        preview_rect = pygame.Rect(x, y + 250, 150, 150)  # Moved down to accommodate name input
        pygame.draw.rect(screen, WHITE, preview_rect, 2)
        coming_soon = FONT.render("Coming Soon!", True, WHITE)
        coming_soon_rect = coming_soon.get_rect(center=preview_rect.center)
        screen.blit(coming_soon, coming_soon_rect)

    def run_game_over(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if self.menu_button.handle_event(event):
                self.state = "PREP"
                self.setup_game_objects()  # Reset game for next round

        screen.blit(LOBBY_BACKGROUND, (0, 0))

        # Draw winner text using custom name
        winner_name = self.player1_name if self.winner == 1 else self.player2_name
        winner_text = TITLE_FONT.render(f"{winner_name} Wins!", True, WHITE)
        winner_rect = winner_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
        screen.blit(winner_text, winner_rect)

        self.menu_button.draw(screen)
        return True

    def run_game(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

        keys = pygame.key.get_pressed()
        self.player1.update(keys, *player1_keys)
        self.player2.update(keys, *player2_keys)

        # Sword attacks
        if keys[pygame.K_SPACE]:
            self.sword1.attacking = True
        else:
            self.sword1.attacking = False

        if keys[pygame.K_RETURN]:
            self.sword2.attacking = True
        else:
            self.sword2.attacking = False

        # Update swords
        self.sword1.update()
        self.sword2.update()

        # Check for collisions and apply damage
        if self.sword1.attacking and pygame.sprite.collide_rect(self.sword1, self.player2):
            self.player2.health = max(self.player2.health - SWORD_DAMAGE, 0)
        if self.sword2.attacking and pygame.sprite.collide_rect(self.sword2, self.player1):
            self.player1.health = max(self.player1.health - SWORD_DAMAGE, 0)

        # Check for game over
        if self.player1.health <= 0:
            self.winner = 2
            self.state = "GAME_OVER"
        elif self.player2.health <= 0:
            self.winner = 1
            self.state = "GAME_OVER"

        # Drawing
        screen.blit(GAME_BACKGROUND, (0, 0))
        self.all_sprites.draw(screen)

        # Display health bars
        pygame.draw.rect(screen, RED, (50, 35, self.player1.health * 2, 30))
        pygame.draw.rect(screen, BLUE, (SCREEN_WIDTH - 250, 35, self.player2.health * 2, 30))

        # Display health values
        player1_health_text = FONT.render(f"{self.player1.health}", True, BLACK)
        player2_health_text = FONT.render(f"{self.player2.health}", True, BLACK)
        screen.blit(player1_health_text, (50 + self.player1.health, 30))
        screen.blit(player2_health_text, (SCREEN_WIDTH - 250 + self.player2.health, 30))

        return True

# Key mappings
player1_keys = [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]
player2_keys = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]

def main():
    clock = pygame.time.Clock()
    game = Game()

    running = True
    while running:
        if game.state == "MENU":
            running = game.run_menu()
        elif game.state == "PREP":
            running = game.run_prep_screen()
        elif game.state == "CUSTOMIZE":
            running = game.run_customize_screen()
        elif game.state == "PLAYING":
            running = game.run_game()
        elif game.state == "GAME_OVER":
            running = game.run_game_over()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
