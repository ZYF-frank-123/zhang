import pygame
import random
import sys
import os

try:
    pygame.init()
    pygame.font.init()
except Exception as e:
    print(f"Pygame 初始化失败: {e}")
    print("请确保已安装 pygame: pip install pygame")
    sys.exit(1)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
RED = (255, 50, 50)
YELLOW = (255, 255, 0)

PLAYER_WIDTH = 50
PLAYER_HEIGHT = 40
PLAYER_SPEED = 5

BULLET_WIDTH = 6
BULLET_HEIGHT = 15
BULLET_SPEED = 8
BULLET_COOLDOWN = 300

ENEMY_WIDTH = 40
ENEMY_HEIGHT = 30
ENEMY_SPEED = 3
ENEMY_SPAWN_INTERVAL = 1000

try:
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Simple Plane Battle")
except Exception as e:
    print(f"创建窗口失败: {e}")
    sys.exit(1)

clock = pygame.time.Clock()

def get_font(size):
    font_paths = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return pygame.font.Font(path, size)
            except:
                continue
    return pygame.font.Font(None, size)

font = get_font(28)
large_font = get_font(48)

class Player:
    def __init__(self):
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - self.height - 20
        self.speed = PLAYER_SPEED
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < SCREEN_HEIGHT - self.height:
            self.y += self.speed
        self.rect.x = self.x
        self.rect.y = self.y
    
    def draw(self, surface):
        pygame.draw.rect(surface, BLUE, self.rect)
        pygame.draw.polygon(surface, BLUE, [
            (self.x + self.width // 2, self.y),
            (self.x + self.width // 4, self.y + 10),
            (self.x + self.width * 3 // 4, self.y + 10)
        ])

class Bullet:
    def __init__(self, x, y):
        self.width = BULLET_WIDTH
        self.height = BULLET_HEIGHT
        self.x = x
        self.y = y
        self.speed = BULLET_SPEED
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def update(self):
        self.y -= self.speed
        self.rect.y = self.y
    
    def is_off_screen(self):
        return self.y + self.height < 0
    
    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)

class Enemy:
    def __init__(self):
        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT
        self.x = random.randint(0, SCREEN_WIDTH - self.width)
        self.y = -self.height
        self.speed = ENEMY_SPEED
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def update(self):
        self.y += self.speed
        self.rect.y = self.y
    
    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT
    
    def draw(self, surface):
        pygame.draw.rect(surface, RED, self.rect)
        pygame.draw.polygon(surface, RED, [
            (self.x + self.width // 2, self.y + self.height),
            (self.x + self.width // 4, self.y + self.height - 10),
            (self.x + self.width * 3 // 4, self.y + self.height - 10)
        ])

def check_collision(rect1, rect2):
    return rect1.colliderect(rect2)

def draw_text(surface, text, font, color, x, y, center=False):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

def reset_game():
    return Player(), [], [], 0, False, pygame.time.get_ticks(), pygame.time.get_ticks()

def main():
    print("游戏启动中...")
    print("控制说明:")
    print("  方向键 - 移动飞机")
    print("  空格键 - 发射子弹")
    print("  R键 - 重新开始(游戏结束后)")
    print("  ESC键 - 退出游戏")
    
    player, bullets, enemies, score, game_over, last_bullet_time, last_enemy_time = reset_game()
    running = True
    
    while running:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if game_over and event.key == pygame.K_r:
                    player, bullets, enemies, score, game_over, last_bullet_time, last_enemy_time = reset_game()
        
        if not game_over:
            keys = pygame.key.get_pressed()
            player.move(keys)
            
            if keys[pygame.K_SPACE] and current_time - last_bullet_time >= BULLET_COOLDOWN:
                bullet_x = player.x + player.width // 2 - BULLET_WIDTH // 2
                bullet_y = player.y
                bullets.append(Bullet(bullet_x, bullet_y))
                last_bullet_time = current_time
            
            if current_time - last_enemy_time >= ENEMY_SPAWN_INTERVAL:
                enemies.append(Enemy())
                last_enemy_time = current_time
            
            for bullet in bullets[:]:
                bullet.update()
                if bullet.is_off_screen():
                    bullets.remove(bullet)
            
            for enemy in enemies[:]:
                enemy.update()
                if enemy.is_off_screen():
                    enemies.remove(enemy)
            
            for bullet in bullets[:]:
                for enemy in enemies[:]:
                    if check_collision(bullet.rect, enemy.rect):
                        if bullet in bullets:
                            bullets.remove(bullet)
                        if enemy in enemies:
                            enemies.remove(enemy)
                        score += 1
                        break
            
            for enemy in enemies:
                if check_collision(player.rect, enemy.rect):
                    game_over = True
                    break
        
        screen.fill(BLACK)
        
        player.draw(screen)
        
        for bullet in bullets:
            bullet.draw(screen)
        
        for enemy in enemies:
            enemy.draw(screen)
        
        draw_text(screen, f"得分: {score}", font, YELLOW, 10, 10)
        
        if game_over:
            draw_text(screen, "游戏结束", large_font, RED, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, center=True)
            draw_text(screen, f"最终得分: {score}", font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20, center=True)
            draw_text(screen, "按 R 键重新开始", font, YELLOW, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60, center=True)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()