import pygame
import math
import random
from weapons import GRENADE_STATS

class Grenade:
    def __init__(self, x, y, angle, g_type, owner_type):
        self.x = x
        self.y = y
        self.angle = angle
        self.type = g_type # 'frag' or 'flash'
        self.owner_type = owner_type
        self.stats = GRENADE_STATS[g_type].copy()
        
        # TACTICAL UPGRADE: Faster throw for longer distance
        self.speed = 16 
        self.friction = 0.95
        
        self.timer = self.stats["fuse"]
        self.alive = True
        self.exploded = False
        
        # Effective radius
        self.radius = self.stats["radius"] # 50px as requested previously
        
        self.vx = math.cos(math.radians(self.angle)) * self.speed
        self.vy = math.sin(math.radians(self.angle)) * self.speed
        
        # Track if it has already hit targets to prevent multiple damage instances
        self.targets_hit = set()

    def update(self, dt, obstacles):
        self.timer -= dt
        if self.timer <= 0:
            self.explode()
            return

        # Movement with friction
        self.vx *= self.friction
        self.vy *= self.friction
        
        # Advanced Bounce Physics
        new_x = self.x + self.vx
        new_y = self.y + self.vy
        
        # Check collision with bounce logic
        rect_x = pygame.Rect(new_x - 4, self.y - 4, 8, 8)
        for wall in obstacles:
            if rect_x.colliderect(wall):
                self.vx *= -0.7 # Bounce and lose energy
                break
        else:
            self.x = new_x
            
        rect_y = pygame.Rect(self.x - 4, new_y - 4, 8, 8)
        for wall in obstacles:
            if rect_y.colliderect(wall):
                self.vy *= -0.7 # Bounce and lose energy
                break
        else:
            self.y = new_y

    def explode(self):
        self.exploded = True
        self.alive = False

    def check_hit(self, target, arena):
        # TACTICAL UPGRADE: Line of sight check for grenades
        # If target is behind a wall, they take no damage/blind
        if not arena.is_visible((self.x, self.y), (target.x, target.y)):
            return False
            
        dist = math.sqrt((target.x - self.x)**2 + (target.y - self.y)**2)
        if dist < self.radius:
            if self.type == "frag":
                # FRAGMENTATION DAMAGE: More damage if close, less if far
                damage_factor = 1.0 - (dist / self.radius)
                damage = self.stats["damage"] * damage_factor
                return damage
            elif self.type == "flash":
                # FLASH BLIND: If visible and within radius, blind for 2-3 seconds
                # (handled in main.py but return True here)
                return True
        return False

    def draw(self, screen):
        # Draw grenade body
        pygame.draw.circle(screen, self.stats["color"], (int(self.x), int(self.y)), 6)
        # Glow based on timer
        glow_alpha = int(255 * (1 - self.timer / self.stats["fuse"]))
        glow_surf = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 0, 0, glow_alpha), (6, 6), 6)
        screen.blit(glow_surf, (int(self.x)-6, int(self.y)-6))
        
        # Fuse blink
        if (self.timer // 100) % 2 == 0:
            pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), 3)
