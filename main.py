import pygame
import random

from pygame import mixer

pygame.init()
mixer.init()

# Game window
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Direction Roulette")
pygame.display.set_icon(pygame.image.load("assets/images/icon_direction_roulette.png"))
enemies = pygame.sprite.Group()

# BGM
mixer.music.load("assets/sfx/music_background.wav")
mixer.music.play(-1)

lives_remaining = 1
score = 0
is_game_over = False


# Create player object
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets/images/player.png")
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.speed = 5  # Default player speed
        self.direction = None

    # Change the player's direction based on random selection
    # With border detection
    def update(self):
        if self.direction == "up" and self.rect.top > 5:
            self.rect.y -= self.speed
        elif self.direction == "down" and self.rect.bottom < SCREEN_HEIGHT - 5:
            self.rect.y += self.speed
        elif self.direction == "left" and self.rect.left > 5:
            self.rect.x -= self.speed
        elif self.direction == "right" and self.rect.right < SCREEN_WIDTH - 5:
            self.rect.x += self.speed

    # Select random movement to go to
    def change_direction(self):
        directions = ["up", "down", "left", "right"]
        if self.direction:
            directions.remove(self.direction)
        self.direction = random.choice(directions)


# Define the Enemy class
chance_to_spawn_new_enemy = 20


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets/images/bomb.png")
        self.rect = self.image.get_rect(center=(random.randint(0, SCREEN_WIDTH), 0))
        self.speed = 7
        self.direction = random.choice(["downwards", "upwards", "to_left", "to_right"])
        self.next_spawn_position_y = random.randint(0, SCREEN_HEIGHT)
        self.next_spawn_position_x = random.randint(0, SCREEN_WIDTH)
        self.new_enemy_chance_threshold = 1

    def update(self):
        global score, chance_to_spawn_new_enemy

        # Make the bomb go the proper way depending on its spawn location
        # going downwards, must spawn from (randint, 0)
        # vice versa
        if self.rect.top > SCREEN_HEIGHT and self.direction == "downwards" \
                or self.rect.bottom > 0 and self.direction == "upwards" \
                or self.rect.left > SCREEN_WIDTH and self.direction == "to_right" \
                or self.rect.right < 0 and self.direction == "to_left":

            self.direction = random.choice(["downwards", "upwards", "to_left", "to_right"])

            self.next_spawn_position_y = random.randint(25, SCREEN_HEIGHT - 25)
            self.next_spawn_position_x = random.randint(25, SCREEN_WIDTH - 25)

            if self.direction == "downwards":
                self.rect = self.image.get_rect(center=(self.next_spawn_position_x, 0))
            elif self.direction == "upwards":
                self.rect = self.image.get_rect(center=(self.next_spawn_position_x, SCREEN_HEIGHT))
            elif self.direction == "to_right":
                self.rect = self.image.get_rect(center=(0, self.next_spawn_position_y))
            elif self.direction == "to_left":
                self.rect = self.image.get_rect(center=(SCREEN_WIDTH, self.next_spawn_position_y))

            score += 10
            self.speed += 0.01
            sound_passed = mixer.Sound("assets/sfx/enemy_passed.wav")
            sound_passed.play()

            if random.randint(0, chance_to_spawn_new_enemy) == self.new_enemy_chance_threshold:
                print("new enemy")
                enemies.add(Enemy())
                chance_to_spawn_new_enemy *= 4

        if self.direction == "downwards":
            self.rect.x = self.next_spawn_position_x
            self.rect.y += self.speed
        elif self.direction == "upwards":
            self.rect.x = self.next_spawn_position_x
            self.rect.y -= self.speed
        elif self.direction == "to_right":
            self.rect.y = self.next_spawn_position_y
            self.rect.x += self.speed
        elif self.direction == "to_left":
            self.rect.y = self.next_spawn_position_y
            self.rect.x -= self.speed

            # Game loop


def play():
    global score, lives_remaining, is_game_over, enemies

    # Create the Player
    player = Player()

    # Create the Enemy sprite group
    enemies.add(Enemy())

    # Set up the game clock
    clock = pygame.time.Clock()

    game_over = False
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                player.change_direction()
                player.speed += 0.02  # Speed up player by an increment every click
                score += 2

        # Update player and enemy on frame
        player.update()
        enemies.update()

        # Check if player has hit an enemy
        # End game if player has collided
        # TODO: Add game over screen, add more lives

        collision_occurred = False
        enemy_amt = len(enemies)
        if pygame.sprite.spritecollide(player, enemies, False) and not collision_occurred:
            collision_occurred = True

            player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            player.direction = None
            player.speed = 5
            lives_remaining -= 1
            mixer.Sound("assets/sfx/life_lost.wav").play()
            enemies = pygame.sprite.Group()

            for _ in range(enemy_amt): enemies.add(Enemy())


            if lives_remaining <= 0:
                running = False
                game_over = True

        # Draw everything

        SCREEN.blit(pygame.image.load("assets/images/image_background.png").convert(), (0, 0))
        SCREEN.blit(player.image, player.rect)  # Player
        enemies.draw(SCREEN)  # Draw enemy

        font = pygame.font.Font('arial.ttf', 32)
        score_text = font.render(f'Score: {score}       Lives: {lives_remaining}', True, (0, 0, 0))
        SCREEN.blit(score_text, ((SCREEN_WIDTH//2)-150, 25))
        pygame.display.flip()

        # Set at 60 fps
        clock.tick(60)

    if game_over:
        game_over_screen(score)


def game_over_screen(score):
    global is_game_over

    is_game_over = True

    button_width = 200
    button_height = 50

    play_again_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + 80, button_width, button_height)
    main_menu_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + 140, button_width, button_height)

    while is_game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if play_again_button_rect.collidepoint(mouse_pos):
                    play_again()
                elif main_menu_button_rect.collidepoint(mouse_pos):
                    main_menu()

        SCREEN.fill((0, 0, 0))

        game_over_text = pygame.font.Font(None, 80).render("Game Over!", True, (255, 255, 255))
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        SCREEN.blit(game_over_text, game_over_rect)

        score_text = pygame.font.Font(None, 40).render(f"Score: {score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        SCREEN.blit(score_text, score_rect)

        play_again_button = pygame.font.Font(None, 30).render("Play Again", True, (255, 255, 255))
        play_again_button_rect.centerx = SCREEN_WIDTH // 2
        SCREEN.blit(play_again_button, play_again_button_rect)

        main_menu_button = pygame.font.Font(None, 30).render("Main Menu", True, (255, 255, 255))
        main_menu_button_rect.centerx = SCREEN_WIDTH // 2
        SCREEN.blit(main_menu_button, main_menu_button_rect)

        pygame.display.flip()






def play_again():
    global score, lives_remaining, is_game_over, enemies

    score = 0
    lives_remaining = 0
    is_game_over = False
    enemies = pygame.sprite.Group()

    play()

    # Create a new enemy
    enemies.add(Enemy())


def main_menu():
    global is_game_over

    is_game_over = False
    SCREEN.fill((0, 0, 0))

    game_title_text = pygame.font.Font(None, 80).render("Direction Roulette", True, (255, 255, 255))
    game_title_rect = game_title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
    SCREEN.blit(game_title_text, game_title_rect)

    play_button = pygame.font.Font(None, 30).render("Play", True, (255, 255, 255))
    play_button_rect = play_button.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
    SCREEN.blit(play_button, play_button_rect)

    pygame.display.flip()

    while not is_game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if play_button_rect.collidepoint(mouse_pos):
                    play_again()
                    main_menu()


main_menu()
