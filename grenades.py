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
        
        # TACTICAL UPGRADE: High-velocity throw
        self.speed = 18 
        self.friction = 0.94
        
        self.timer = self.stats["fuse"]
        self.alive = True
        self.exploded = False
        
        # TACTICAL REFINEMENT: Frag and Flash Radius
        self.radius = 120 # Larger overall radius
        self.lethal_radius = 45 # Insta-kill zone for frag
        
        self.vx = math.cos(math.radians(self.angle)) * self.speed
        self.vy = math.sin(math.radians(self.angle)) * self.speed

    def update(self, dt, obstacles):
        self.timer -= dt
        if self.timer <= 0:
            self.explode()
            return

        # Movement with friction
        self.vx *= self.friction
        self.vy *= self.friction
        
        # Collision with bounce
        new_x = self.x + self.vx
        new_y = self.y + self.vy
        
        rect_x = pygame.Rect(new_x - 4, self.y - 4, 8, 8)
        for wall in obstacles:
            if rect_x.colliderect(wall):
                self.vx *= -0.7
                break
        else:
            self.x = new_x
            
        rect_y = pygame.Rect(self.x - 4, new_y - 4, 8, 8)
        for wall in obstacles:
            if rect_y.colliderect(wall):
                self.vy *= -0.7
                break
        else:
            self.y = new_y

    def explode(self):
        self.exploded = True
        self.alive = False

    def check_hit(self, target, arena):
        # Line of sight check: Walls block all grenade effects
        if not arena.is_visible((self.x, self.y), (target.x, target.y)):
            return None
            
        dist = math.sqrt((target.x - self.x)**2 + (target.y - self.y)**2)
        
        if self.type == "frag":
            if dist < self.lethal_radius:
                return "lethal" # Instant kill
            elif dist < self.radius:
                # Falloff damage for the outer zone
                falloff = 1.0 - (dist / self.radius)
                return self.stats["damage"] * falloff
        elif self.type == "flash":
            if dist < self.radius:
                return "stun" # Stun effect
        return None

    def draw(self, screen):
        # Draw grenade body
        pygame.draw.circle(screen, self.stats["color"], (int(self.x), int(self.y)), 6)
        # Fuse blink
        if (self.timer // 100) % 2 == 0:
            pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), 3)
