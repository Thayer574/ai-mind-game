import pygame
import math
import random
from weapons import ARMOR_STATS, WEAPON_STATS
from bullets import Bullet

class Player:
    def __init__(self, x, y, armor_type, weapon_type, secondary_type="pistol"):
        self.x = x
        self.y = y
        self.armor_type = armor_type
        self.weapon_type = weapon_type
        self.secondary_type = secondary_type
        self.current_weapon = weapon_type
        self.size = 15
        self.angle = 0
        self.hp_max = ARMOR_STATS[armor_type]["hp"]
        self.hp = float(self.hp_max)
        self.base_speed = ARMOR_STATS[armor_type]["speed"]
        self.color = ARMOR_STATS[armor_type]["color"]
        
        # Load weapon stats
        self.stats = self.get_weapon_stats(self.current_weapon)
        self.ammo = self.stats["ammo"]
        self.reloading = False
        self.reload_timer = 0
        self.fire_timer = 0
        
        # Tracking for AI learning
        self.stats_tracker = {
            "left_moves": 0,
            "right_moves": 0,
            "shots_fired": 0,
            "rush_count": 0
        }
        
        # For movement prediction (velocity)
        self.vx = 0
        self.vy = 0

    def get_weapon_stats(self, weapon_type):
        return WEAPON_STATS[weapon_type].copy()

    def update(self, dt, keys, mouse_pos, obstacles):
        # Calculate angle to mouse
        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        self.angle = math.degrees(math.atan2(dy, dx))
        
        # Speed with weapon penalty
        current_speed = self.base_speed * self.stats["speed_penalty"]
        
        # Movement
        move_x = 0
        move_y = 0
        if keys[pygame.K_w]: move_y -= 1
        if keys[pygame.K_s]: move_y += 1
        if keys[pygame.K_a]: 
            move_x -= 1
            self.stats_tracker["left_moves"] += 1
        if keys[pygame.K_d]: 
            move_x += 1
            self.stats_tracker["right_moves"] += 1
            
        # Normalize diagonal movement
        if move_x != 0 and move_y != 0:
            length = math.sqrt(move_x**2 + move_y**2)
            move_x /= length
            move_y /= length
            
        # Rush count tracking (if moving towards right/AI side)
        if move_x > 0:
            self.stats_tracker["rush_count"] += 1
            
        # Collision detection (simple)
        self.vx = move_x * current_speed
        self.vy = move_y * current_speed
        
        # Try moving X
        new_rect = pygame.Rect(self.x + self.vx - self.size, self.y - self.size, self.size * 2, self.size * 2)
        can_move_x = True
        for wall in obstacles:
            if new_rect.colliderect(wall):
                can_move_x = False
                break
        if can_move_x:
            self.x += self.vx
            
        # Try moving Y
        new_rect = pygame.Rect(self.x - self.size, self.y + self.vy - self.size, self.size * 2, self.size * 2)
        can_move_y = True
        for wall in obstacles:
            if new_rect.colliderect(wall):
                can_move_y = False
                break
        if can_move_y:
            self.y += self.vy
            
        # Timers
        if self.fire_timer > 0:
            self.fire_timer -= dt
        if self.reloading:
            self.reload_timer -= dt
            if self.reload_timer <= 0:
                self.reloading = False
                self.ammo = self.stats["ammo"]

    def fire(self):
        if self.reloading or self.fire_timer > 0:
            return None
        
        if self.ammo <= 0:
            self.start_reload()
            return None
            
        self.ammo -= 1
        self.fire_timer = self.stats["fire_rate"]
        self.stats_tracker["shots_fired"] += 1
        
        bullets = []
        for _ in range(self.stats["pellets"]):
            # Add spread
            spread_angle = self.angle + random.uniform(-self.stats["spread"], self.stats["spread"])
            bullets.append(Bullet(self.x, self.y, spread_angle, self.stats["damage"], self.stats["range"], "player"))
            
        if self.ammo <= 0:
            self.start_reload()
            
        return bullets

    def start_reload(self):
        if not self.reloading and self.ammo < self.stats["ammo"]:
            self.reloading = True
            self.reload_timer = self.stats["reload_time"]

    def draw(self, screen):
        # Draw player circle
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
        # Draw aim direction line
        aim_x = self.x + math.cos(math.radians(self.angle)) * 25
        aim_y = self.y + math.sin(math.radians(self.angle)) * 25
        pygame.draw.line(screen, (255, 255, 255), (int(self.x), int(self.y)), (int(aim_x), int(aim_y)), 2)
        
        # Health bar (simple)
        bar_width = 40
        pygame.draw.rect(screen, (255, 0, 0), (self.x - bar_width//2, self.y - self.size - 10, bar_width, 5))
        pygame.draw.rect(screen, (0, 255, 0), (self.x - bar_width//2, self.y - self.size - 10, int(bar_width * (self.hp / self.hp_max)), 5))
        
        # Ammo display
        if self.reloading:
            text = "RELOADING..."
        else:
            text = f"{self.ammo}/{self.stats['ammo']}"
        # (Font handling will be in main loop)
        return text
