import time

import pygame
import random

from pygame import mixer

pygame.init()
mixer.init()
# Game window
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Direction Roulette")

score = 0
lives_remaining = 3
enemies = pygame.sprite.Group()

# BGM
mixer.music.load("assets/bgm.wav")
mixer.music.play(-1)

# Create player object
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets/player.png")
        self.rect = self.image.get_rect(center=(screen_width // 2, screen_height // 2))
        self.speed = 5  # Default player speed
        self.direction = None

    # Change the player's direction based on random selection
    # With border detection
    def update(self):
        if self.direction == "up" and self.rect.top > 5:
            self.rect.y -= self.speed
        elif self.direction == "down" and self.rect.bottom < screen_height - 5:
            self.rect.y += self.speed
        elif self.direction == "left" and self.rect.left > 5:
            self.rect.x -= self.speed
        elif self.direction == "right" and self.rect.right < screen_width - 5:
            self.rect.x += self.speed

    # Select random movement to go to
    def change_direction(self):
        directions = ["up", "down", "left", "right"]
        if self.direction:
            directions.remove(self.direction)
        self.direction = random.choice(directions)


# Define the Enemy class
chance_to_spawn_new_enemy = 10


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets/bombthing.png")
        self.rect = self.image.get_rect(center=(random.randint(0, screen_width), 0))
        self.speed = 5
        self.direction = random.choice(["downwards", "upwards", "to_left", "to_right"])
        self.next_spawn_position_y = 0
        self.next_spawn_position_x = random.randint(0, screen_width)
        self.new_enemy_chance_threshold = 1

    def update(self):
        global score, chance_to_spawn_new_enemy

        # Make the bomb go the proper way depending on its spawn location
        # going downwards, must spawn from (randint, 0)
        # vice versa
        if self.rect.top > screen_height and self.direction == "downwards" \
                or self.rect.bottom > 0 and self.direction == "upwards" \
                or self.rect.left > screen_width and self.direction == "to_right" \
                or self.rect.right < 0 and self.direction == "to_left":

            self.direction = random.choice(["downwards", "upwards", "to_left", "to_right"])

            # select a random x and y position to spawn from for the next direction.
            self.next_spawn_position_y = random.randint(0, screen_height)
            self.next_spawn_position_x = random.randint(0, screen_width)

            if self.direction == "downwards":
                self.rect = self.image.get_rect(center=(self.next_spawn_position_x, 0))
            elif self.direction == "upwards":
                self.rect = self.image.get_rect(center=(self.next_spawn_position_x, screen_height))
            elif self.direction == "to_right":
                self.rect = self.image.get_rect(center=(0, self.next_spawn_position_y))
            elif self.direction == "to_left":
                self.rect = self.image.get_rect(center=(screen_width, self.next_spawn_position_y))

            score += 10
            self.speed += 0.01
            sound_passed = mixer.Sound("assets/enemy_passed.wav")
            sound_passed.play()

            if random.randint(0, chance_to_spawn_new_enemy) == self.new_enemy_chance_threshold:
                print("new enemy")
                enemies.add(Enemy())
                chance_to_spawn_new_enemy *= 5

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


class Powerup(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect(center=(random.randint(5, screen_width), random.randint(5, screen_height)))


# Game loop
def play():
    global score, lives_remaining

    # Create the Player
    player = Player()

    # Create the Enemy sprite group
    enemies.add(Enemy())

    # Set up the game clock
    clock = pygame.time.Clock()

    running = True
    while running:
        #powerup_threshold = 1

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

        # Can't fix lives counter
        collision_occurred = False
        if pygame.sprite.spritecollide(player, enemies, False) and not collision_occurred:
            lives_remaining -= 1
            collision_occurred = True

            if lives_remaining == 0:
                #running = False
                game_over()


        # Draw everything
        # ---------------
        # Background
        screen.fill((35, 31, 32))

        # Player
        screen.blit(player.image, player.rect)

        # Obstacles
        enemies.draw(screen)

        # Score text
        font = pygame.font.Font('arial.ttf', 32)
        score_text = font.render(f'Score: {score}\tLives: {lives_remaining}', True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        pygame.display.flip()

        # Wait for next frame
        clock.tick(60)

def game_over():
    screen.fill((200, 50, 50))
    pygame.display.flip()

play()