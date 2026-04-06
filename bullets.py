import pygame
import math

class Bullet:
    def __init__(self, x, y, angle, damage, range_limit, owner_type, speed=15, size=4, color=(255, 255, 0)):
        self.x = x
        self.y = y
        self.angle = angle
        self.damage = damage
        self.range_limit = range_limit
        self.owner_type = owner_type # 'player' or 'ai'
        self.speed = speed
        self.size = size
        self.color = color
        self.distance_traveled = 0
        self.alive = True

    def update(self, obstacles):
        # Move bullet
        dx = math.cos(math.radians(self.angle)) * self.speed
        dy = math.sin(math.radians(self.angle)) * self.speed
        
        self.x += dx
        self.y += dy
        self.distance_traveled += math.sqrt(dx**2 + dy**2)
        
        # Check range
        if self.distance_traveled > self.range_limit:
            self.alive = False
            
        # Check collisions with obstacles (walls)
        bullet_rect = pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)
        for obstacle in obstacles:
            if bullet_rect.colliderect(obstacle):
                self.alive = False
                return True # Hit a wall
        return False

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
        # Trail
        trail_start = (int(self.x - math.cos(math.radians(self.angle)) * 10), 
                       int(self.y - math.sin(math.radians(self.angle)) * 10))
        pygame.draw.line(screen, (self.color[0], self.color[1], 0, 100), (int(self.x), int(self.y)), trail_start, 2)
