import pygame
import random
import sys

# 初始化 Pygame
pygame.init()

# 窗口设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
RED = (255, 50, 50)
YELLOW = (255, 255, 0)

# 创建游戏窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("简易飞机大战")
clock = pygame.time.Clock()

# 字体设置 - 加载Windows系统字体文件支持中文
import os

# 常见中文字体路径
font_paths = [
    "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
    "C:/Windows/Fonts/simhei.ttf",  # 黑体
    "C:/Windows/Fonts/simsun.ttc",  # 宋体
]

font = None
game_over_font = None

for font_path in font_paths:
    if os.path.exists(font_path):
        try:
            font = pygame.font.Font(font_path, 36)
            game_over_font = pygame.font.Font(font_path, 48)
            break
        except:
            continue

# 如果找不到中文字体，使用默认字体
if font is None:
    font = pygame.font.Font(None, 36)
    game_over_font = pygame.font.Font(None, 48)


class Player:
    """玩家飞机类"""
    def __init__(self):
        self.width = 50
        self.height = 50
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - self.height - 20
        self.speed = 5
        self.color = BLUE

    def move(self, keys):
        """根据键盘输入移动飞机，限制在窗口内"""
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
        if keys[pygame.K_UP]:
            self.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.y += self.speed

        # 边界限制
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height))

    def draw(self, surface):
        """绘制玩家飞机"""
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))

    def get_rect(self):
        """获取飞机矩形区域，用于碰撞检测"""
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Bullet:
    """子弹类"""
    def __init__(self, x, y):
        self.width = 6
        self.height = 15
        self.x = x - self.width // 2
        self.y = y
        self.speed = 8
        self.color = WHITE

    def update(self):
        """更新子弹位置（向上移动）"""
        self.y -= self.speed

    def draw(self, surface):
        """绘制子弹"""
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))

    def is_off_screen(self):
        """判断子弹是否超出窗口"""
        return self.y + self.height < 0

    def get_rect(self):
        """获取子弹矩形区域，用于碰撞检测"""
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Enemy:
    """敌机类"""
    def __init__(self):
        self.width = 40
        self.height = 40
        self.x = random.randint(0, SCREEN_WIDTH - self.width)
        self.y = -self.height
        self.speed = random.randint(2, 4)
        self.color = RED

    def update(self):
        """更新敌机位置（向下移动）"""
        self.y += self.speed

    def draw(self, surface):
        """绘制敌机"""
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))

    def is_off_screen(self):
        """判断敌机是否超出窗口"""
        return self.y > SCREEN_HEIGHT

    def get_rect(self):
        """获取敌机矩形区域，用于碰撞检测"""
        return pygame.Rect(self.x, self.y, self.width, self.height)


def draw_text(surface, text, font, color, x, y, center=True):
    """绘制文字"""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)


def reset_game():
    """重置游戏状态"""
    player = Player()
    bullets = []
    enemies = []
    score = 0
    game_over = False
    last_shot_time = 0
    last_enemy_spawn_time = 0
    return player, bullets, enemies, score, game_over, last_shot_time, last_enemy_spawn_time


def main():
    """游戏主函数"""
    # 初始化游戏状态
    player, bullets, enemies, score, game_over, last_shot_time, last_enemy_spawn_time = reset_game()

    # 射击间隔（秒）
    shot_interval = 0.3
    # 敌机生成间隔（秒）
    enemy_spawn_interval = 1.0

    running = True
    while running:
        current_time = pygame.time.get_ticks() / 1000.0  # 转换为秒

        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                # 游戏结束时按 R 键重启
                if game_over and event.key == pygame.K_r:
                    player, bullets, enemies, score, game_over, last_shot_time, last_enemy_spawn_time = reset_game()

        if not game_over:
            # 获取键盘状态
            keys = pygame.key.get_pressed()

            # 玩家移动
            player.move(keys)

            # 发射子弹（空格键，有间隔限制）
            if keys[pygame.K_SPACE]:
                if current_time - last_shot_time >= shot_interval:
                    # 在飞机顶部中央发射子弹
                    bullet_x = player.x + player.width // 2
                    bullet_y = player.y
                    bullets.append(Bullet(bullet_x, bullet_y))
                    last_shot_time = current_time

            # 生成敌机
            if current_time - last_enemy_spawn_time >= enemy_spawn_interval:
                enemies.append(Enemy())
                last_enemy_spawn_time = current_time

            # 更新子弹位置
            for bullet in bullets[:]:
                bullet.update()
                if bullet.is_off_screen():
                    bullets.remove(bullet)

            # 更新敌机位置
            for enemy in enemies[:]:
                enemy.update()
                if enemy.is_off_screen():
                    enemies.remove(enemy)

            # 碰撞检测：子弹与敌机
            for bullet in bullets[:]:
                for enemy in enemies[:]:
                    if bullet.get_rect().colliderect(enemy.get_rect()):
                        # 子弹击中敌机，两者都销毁
                        if bullet in bullets:
                            bullets.remove(bullet)
                        if enemy in enemies:
                            enemies.remove(enemy)
                        score += 1
                        break

            # 碰撞检测：敌机与玩家
            for enemy in enemies:
                if player.get_rect().colliderect(enemy.get_rect()):
                    game_over = True
                    break

        # 绘制
        screen.fill(BLACK)

        # 绘制游戏元素
        if not game_over:
            player.draw(screen)
            for bullet in bullets:
                bullet.draw(screen)
            for enemy in enemies:
                enemy.draw(screen)

        # 显示得分
        draw_text(screen, f"得分: {score}", font, WHITE, 10, 10, center=False)

        # 游戏结束显示
        if game_over:
            draw_text(screen, "游戏结束", game_over_font, YELLOW, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
            draw_text(screen, f"最终得分: {score}", font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10)
            draw_text(screen, "按 R 键重新开始", font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)

        # 更新显示
        pygame.display.flip()

        # 控制帧率
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
