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
try:
    BACKGROUND_IMAGE = pygame.image.load(os.path.join(os.path.dirname(__file__), "pg-background.jpg"))
except pygame.error:
    raise FileNotFoundError("Background image 'pg-background.jpg' not found. Please ensure the file is in the same directory as the script.")
BACKGROUND_IMAGE = pygame.transform.scale(BACKGROUND_IMAGE, (SCREEN_WIDTH, SCREEN_HEIGHT))
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Font settings
FONT_PATH = os.path.join(os.path.dirname(__file__), "Minercraftory.ttf")
if not os.path.exists(FONT_PATH):
    raise FileNotFoundError(f"Font file not found at {FONT_PATH}. Please ensure the file is in the same directory as the script.")
FONT = pygame.font.Font(FONT_PATH, 24)  # Pixelated font style

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

# Initialize players
player1 = Player(100, SCREEN_HEIGHT // 2, RED)
player2 = Player(SCREEN_WIDTH - 150, SCREEN_HEIGHT // 2, BLUE)

# Initialize swords
sword1 = Sword(player1, RED)
sword2 = Sword(player2, BLUE)

# Groups
all_sprites = pygame.sprite.Group(player1, player2, sword1, sword2)

# Key mappings
player1_keys = [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]
player2_keys = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Input handling
    keys = pygame.key.get_pressed()
    player1.update(keys, *player1_keys)
    player2.update(keys, *player2_keys)

    # Sword attacks
    if keys[pygame.K_SPACE]:  # Player 1 attack key
        sword1.attacking = True
    else:
        sword1.attacking = False

    if keys[pygame.K_RETURN]:  # Player 2 attack key
        sword2.attacking = True
    else:
        sword2.attacking = False

    # Update swords
    sword1.update()
    sword2.update()

    # Check for collisions and apply damage
    if sword1.attacking and pygame.sprite.collide_rect(sword1, player2):
        player2.health = max(player2.health - SWORD_DAMAGE, 0)
    if sword2.attacking and pygame.sprite.collide_rect(sword2, player1):
        player1.health = max(player1.health - SWORD_DAMAGE, 0)

    # Check for game over
    if player1.health <= 0:
        print("Player 2 wins!")
        running = False
    elif player2.health <= 0:
        print("Player 1 wins!")
        running = False

    # Drawing
    screen.fill(WHITE)
    screen.blit(BACKGROUND_IMAGE, (0, 0))
    all_sprites.draw(screen)

    # Display health bars
    pygame.draw.rect(screen, RED, (50, 35, player1.health * 2, 30))
    pygame.draw.rect(screen, BLUE, (SCREEN_WIDTH - 250, 35, player2.health * 2, 30))

    # Display health values above health bars
    player1_health_text = FONT.render(f"{player1.health}", True, BLACK)
    player2_health_text = FONT.render(f"{player2.health}", True, BLACK)
    screen.blit(player1_health_text, (50 + player1.health, 30))
    screen.blit(player2_health_text, (SCREEN_WIDTH - 250 + player2.health, 30))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
