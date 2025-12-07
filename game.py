import pygame
import random

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
PLATFORM_BROWN = (139, 69, 19)
GOLD = (255, 215, 0)
RED = (255, 0, 0)
OVERLAY_COLOR = (0, 0, 0, 180) # Semi-transparent black

# --- Classes ---

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 40), pygame.SRCALPHA)
        
        # Robot Body (Gray)
        pygame.draw.rect(self.image, (192, 192, 192), (5, 15, 20, 25))
        # Head
        pygame.draw.rect(self.image, (169, 169, 169), (5, 0, 20, 15))
        # Eyes (Green)
        pygame.draw.rect(self.image, (0, 255, 0), (8, 5, 4, 4))
        pygame.draw.rect(self.image, (0, 255, 0), (18, 5, 4, 4))
        # Antenna
        pygame.draw.line(self.image, (100, 100, 100), (15, 0), (15, -5), 2)
        pygame.draw.circle(self.image, (255, 0, 0), (15, -5), 2)
        
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = SCREEN_HEIGHT - 100
        
        self.change_x = 0
        self.change_y = 0
        self.level = None
        
    def update(self):
        self.calc_grav()
        self.rect.x += self.change_x
        
        # Horizontal Collision
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                self.rect.left = block.rect.right
                
        self.rect.y += self.change_y
        
        # Vertical Collision
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
                self.change_y = 0
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom
                self.change_y = 0

    def calc_grav(self):
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += 0.35

    def jump(self):
        self.rect.y += 2
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 2
        
        if len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.change_y = -10

    def go_left(self):
        self.change_x = -5

    def go_right(self):
        self.change_x = 5

    def stop(self):
        self.change_x = 0

class Platform(pygame.sprite.Sprite):
    def __init__(self, width, height, x, y):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(PLATFORM_BROWN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, GOLD, (10, 10), 10)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, dist):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        # Eyes
        pygame.draw.rect(self.image, WHITE, (5, 5, 8, 8))
        pygame.draw.rect(self.image, WHITE, (17, 5, 8, 8))
        pygame.draw.rect(self.image, BLACK, (7, 7, 4, 4))
        pygame.draw.rect(self.image, BLACK, (19, 7, 4, 4))
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.start_x = x
        self.dist = dist
        self.direction = 1
        self.speed = 2

    def update(self):
        self.rect.x += self.speed * self.direction
        if abs(self.rect.x - self.start_x) > self.dist:
            self.direction *= -1

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        size = random.randint(3, 6)
        self.image = pygame.Surface((size, size))
        self.image.fill(GOLD)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.change_x = random.uniform(-3, 3)
        self.change_y = random.uniform(-3, 3)
        self.life = 20

    def update(self):
        self.rect.x += self.change_x
        self.rect.y += self.change_y
        self.life -= 1
        if self.life <= 0:
            self.kill()

class Level:
    def __init__(self, player):
        self.platform_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.coin_list = pygame.sprite.Group()
        self.player = player
        
        # Initial Generation
        self.current_x = 0
        self.generate_chunk(0)
        self.generate_chunk(SCREEN_WIDTH)

    def generate_chunk(self, start_x):
        # Floor
        floor_width = SCREEN_WIDTH
        floor = Platform(floor_width, 40, start_x, SCREEN_HEIGHT - 40)
        self.platform_list.add(floor)
        
        # Random Platforms
        num_platforms = random.randint(2, 4)
        for _ in range(num_platforms):
            w = random.randint(70, 150)
            h = 20
            x = start_x + random.randint(0, SCREEN_WIDTH - w)
            y = random.randint(150, 300)
            
            p = Platform(w, h, x, y)
            self.platform_list.add(p)
            
            # Chance for Coin
            if random.random() > 0.3:
                coin = Coin(x + w//2, y - 25)
                self.coin_list.add(coin)
                
            # Chance for Enemy
            if random.random() > 0.7:
                enemy = Enemy(x + 10, y - 30, w - 40)
                self.enemy_list.add(enemy)
                
        self.current_x = start_x + SCREEN_WIDTH

    def update(self):
        self.platform_list.update()
        self.enemy_list.update()
        self.coin_list.update()
        
        # Scroll World
        if self.player.rect.right >= 500:
            diff = self.player.rect.right - 500
            self.player.rect.right = 500
            self.shift_world(-diff)
            
        # Generate new chunks
        rightmost = -9999
        for p in self.platform_list:
            if p.rect.right > rightmost:
                rightmost = p.rect.right
                
        if rightmost < SCREEN_WIDTH + 200:
            self.generate_chunk(rightmost + random.randint(50, 150))

        # Cleanup
        for p in self.platform_list:
            if p.rect.right < 0: p.kill()
        for e in self.enemy_list:
            if e.rect.right < 0: e.kill()
        for c in self.coin_list:
            if c.rect.right < 0: c.kill()

    def shift_world(self, shift_x):
        for p in self.platform_list:
            p.rect.x += shift_x
        for e in self.enemy_list:
            e.rect.x += shift_x
            e.start_x += shift_x
        for c in self.coin_list:
            c.rect.x += shift_x

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Infinite Robot Runner")
    
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    game_over_font = pygame.font.Font(None, 72)
    
    # Game State Variables
    player = None
    level = None
    active_sprite_list = None
    particle_list = None
    score = 0
    game_over = False
    
    def reset_game():
        nonlocal player, level, active_sprite_list, particle_list, score, game_over
        player = Player()
        level = Level(player)
        player.level = level
        
        active_sprite_list = pygame.sprite.Group()
        active_sprite_list.add(player)
        
        particle_list = pygame.sprite.Group()
        score = 0
        game_over = False

    # Initial Start
    reset_game()
    
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        reset_game()
                else:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        player.go_left()
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        player.go_right()
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        player.jump()
                    
            if event.type == pygame.KEYUP:
                if not game_over:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        if player.change_x < 0: player.stop()
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        if player.change_x > 0: player.stop()
                    
        if not game_over:
            # Update
            active_sprite_list.update()
            level.update()
            particle_list.update()
            
            # Coin Collection
            coin_hit_list = pygame.sprite.spritecollide(player, level.coin_list, True)
            for coin in coin_hit_list:
                score += 100
                for _ in range(10):
                    p = Particle(coin.rect.centerx, coin.rect.centery)
                    particle_list.add(p)
                    
            # Enemy Collision
            if pygame.sprite.spritecollide(player, level.enemy_list, False):
                game_over = True
                
            # Fall off map
            if player.rect.y >= SCREEN_HEIGHT:
                game_over = True
            
        # Draw
        screen.fill(SKY_BLUE)
        level.platform_list.draw(screen)
        level.coin_list.draw(screen)
        level.enemy_list.draw(screen)
        active_sprite_list.draw(screen)
        particle_list.draw(screen)
        
        # Score
        text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(text, (10, 10))
        
        if game_over:
            # Draw Overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill(OVERLAY_COLOR)
            screen.blit(overlay, (0, 0))
            
            # Draw Text
            go_text = game_over_font.render("GAME OVER", True, RED)
            screen.blit(go_text, (SCREEN_WIDTH//2 - go_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
            
            restart_text = font.render("Press 'R' to Restart", True, WHITE)
            screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
        
        pygame.display.flip()
        clock.tick(FPS)
        
    pygame.quit()

if __name__ == "__main__":
    main()
