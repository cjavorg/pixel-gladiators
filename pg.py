import pygame
import sys
import os

# Initialize pygame
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

# Load background
try:
    BACKGROUND_IMAGE = pygame.image.load(os.path.join(os.path.dirname(__file__), "pg-background.jpg"))
    BACKGROUND_IMAGE = pygame.transform.scale(BACKGROUND_IMAGE, (SCREEN_WIDTH, SCREEN_HEIGHT))
except pygame.error:
    raise FileNotFoundError("Background image 'pg-background.jpg' not found. Please ensure the file is in the same directory as the script.")

# Font settings
FONT_PATH = os.path.join(os.path.dirname(__file__), "Minercraftory.ttf")
if not os.path.exists(FONT_PATH):
    raise FileNotFoundError(f"Font file not found at {FONT_PATH}. Please ensure the file is in the same directory as the script.")
FONT = pygame.font.Font(FONT_PATH, 24)
TITLE_FONT = pygame.font.Font(FONT_PATH, 64)

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
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.is_hovered = False

    def draw(self, surface):
        color = (min(self.color[0] + 30, 255),
                min(self.color[1] + 30, 255),
                min(self.color[2] + 30, 255)) if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        text_surface = FONT.render(self.text, True, BLACK)
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
        self.start_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2, 200, 50, "Start Game", (100, 200, 100))
        self.menu_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 100, 200, 50, "Back to Menu", (100, 200, 100))
        self.winner = None
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

    def run_menu(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if self.start_button.handle_event(event):
                self.state = "PLAYING"

        screen.blit(BACKGROUND_IMAGE, (0, 0))

        # Draw title
        title_text = TITLE_FONT.render("Pixel Gladiators", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
        screen.blit(title_text, title_rect)

        self.start_button.draw(screen)
        return True

    def run_game_over(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if self.menu_button.handle_event(event):
                self.state = "MENU"
                self.setup_game_objects()  # Reset game for next round

        screen.blit(BACKGROUND_IMAGE, (0, 0))

        # Draw winner text
        winner_text = TITLE_FONT.render(f"Player {self.winner} Wins!", True, WHITE)
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
        screen.blit(BACKGROUND_IMAGE, (0, 0))
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
