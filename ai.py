import pygame
import math
import random
from weapons import ARMOR_STATS, WEAPON_STATS
from bullets import Bullet

class AI:
    def __init__(self, x, y, level, weapon_type="ar"):
        self.x = x
        self.y = y
        self.level = level
        self.weapon_type = weapon_type
        self.size = 15
        self.angle = 180 # Start facing left
        
        # Base stats scaling with level
        # Level 1-10: HP and Speed scale slightly
        self.armor_type = "none"
        if level > 3: self.armor_type = "light"
        if level > 6: self.armor_type = "medium"
        if level > 9: self.armor_type = "heavy"
        
        self.hp_max = ARMOR_STATS[self.armor_type]["hp"] + (level // 5)
        self.hp = float(self.hp_max)
        self.base_speed = ARMOR_STATS[self.armor_type]["speed"] + (level * 0.1)
        self.color = (255, 50, 50) # AI is red
        
        # Weapon stats
        self.stats = WEAPON_STATS[weapon_type].copy()
        # Scale AI weapon stats (AI has slightly slower fire rate than player usually, but increases with level)
        self.stats["fire_rate"] *= max(0.5, 1.5 - (level * 0.1))
        self.ammo = self.stats["ammo"]
        self.reloading = False
        self.reload_timer = 0
        self.fire_timer = 0
        
        # AI State
        self.target_pos = (x, y)
        self.move_timer = 0
        self.state = "idle" # idle, move, cover, rush
        self.last_shot_time = 0
        self.accuracy_offset = max(0, 20 - level * 2) # Decreases as level increases

    def update(self, dt, player, obstacles, arena):
        # AI logic based on level
        self.update_behavior(dt, player, obstacles, arena)
        
        # Speed with weapon penalty
        current_speed = self.base_speed * self.stats["speed_penalty"]
        
        # Movement towards target_pos
        dx = self.target_pos[0] - self.x
        dy = self.target_pos[1] - self.y
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist > 5:
            vx = (dx / dist) * current_speed
            vy = (dy / dist) * current_speed
            
            # Simple collision detection
            new_rect = pygame.Rect(self.x + vx - self.size, self.y - self.size, self.size * 2, self.size * 2)
            can_move_x = True
            for wall in obstacles:
                if new_rect.colliderect(wall):
                    can_move_x = False
                    break
            if can_move_x:
                self.x += vx
                
            new_rect = pygame.Rect(self.x - self.size, self.y + vy - self.size, self.size * 2, self.size * 2)
            can_move_y = True
            for wall in obstacles:
                if new_rect.colliderect(wall):
                    can_move_y = False
                    break
            if can_move_y:
                self.y += vy
        
        # Aiming logic
        self.update_aim(player)
        
        # Timers
        if self.fire_timer > 0:
            self.fire_timer -= dt
        if self.reloading:
            self.reload_timer -= dt
            if self.reload_timer <= 0:
                self.reloading = False
                self.ammo = self.stats["ammo"]

    def update_aim(self, player):
        # Calculate base angle to player
        dx = player.x - self.x
        dy = player.y - self.y
        base_angle = math.degrees(math.atan2(dy, dx))
        
        # Level 4-6: Predictive aiming (simple)
        if self.level >= 4:
            # Predict where player will be based on their current velocity
            prediction_factor = 0.5 # How much to predict
            dist = math.sqrt(dx**2 + dy**2)
            time_to_reach = dist / 15 # Bullet speed approx 15
            
            target_x = player.x + player.vx * time_to_reach * prediction_factor
            target_y = player.y + player.vy * time_to_reach * prediction_factor
            base_angle = math.degrees(math.atan2(target_y - self.y, target_x - self.x))
            
        # Level 7-10: Mind games / Habit tracking
        if self.level >= 7:
            # Check player tendencies
            if player.stats_tracker["left_moves"] > player.stats_tracker["right_moves"] * 1.5:
                base_angle -= 5 # Pre-aim left (from AI perspective)
            elif player.stats_tracker["right_moves"] > player.stats_tracker["left_moves"] * 1.5:
                base_angle += 5 # Pre-aim right
        
        # Level 10+: Predictive aiming (more aggressive)
        if self.level >= 10:
            # Even better prediction
            pass

        # Apply accuracy offset (jitter)
        if self.accuracy_offset > 0:
            base_angle += random.uniform(-self.accuracy_offset, self.accuracy_offset)
            
        self.angle = base_angle

    def update_behavior(self, dt, player, obstacles, arena):
        self.move_timer -= dt
        
        # Level 1: Moves randomly
        if self.level == 1:
            if self.move_timer <= 0:
                self.target_pos = (random.randint(arena.width//2, arena.width-50), 
                                   random.randint(50, arena.height-50))
                self.move_timer = 2000
                
        # Level 2-3: Moves toward player intelligently, uses cover
        elif self.level <= 3:
            if self.move_timer <= 0:
                # Try to find a position with line of sight but near a wall
                if arena.is_visible((self.x, self.y), (player.x, player.y)):
                    # Strafe
                    self.target_pos = (self.x, self.y + random.choice([-100, 100]))
                else:
                    # Move to see player
                    self.target_pos = (player.x + 200, player.y + random.randint(-50, 50))
                self.move_timer = 1500
                
        # Level 4-6: Predicts movement slightly, strafes during fights
        elif self.level <= 6:
            if self.move_timer <= 0:
                # Active strafing
                self.target_pos = (self.x + random.randint(-50, 50), 
                                   player.y + random.randint(-100, 100))
                self.move_timer = 800
                
        # Level 7+: Advanced tactics
        else:
            if self.move_timer <= 0:
                # Check if player is rushing
                if player.stats_tracker["rush_count"] > 100: # Simple rush detection
                    # Back up
                    self.target_pos = (arena.width - 100, self.y + random.randint(-100, 100))
                else:
                    # Flank or take cover
                    self.target_pos = (random.randint(arena.width//2 + 100, arena.width-100), 
                                       random.randint(100, arena.height-100))
                self.move_timer = 1000

    def fire(self, player, arena):
        # AI fires if player is visible and fire_timer is 0
        if self.reloading or self.fire_timer > 0:
            return None
            
        if self.ammo <= 0:
            self.start_reload()
            return None
            
        # Check line of sight
        if not arena.is_visible((self.x, self.y), (player.x, player.y)):
            return None
            
        # Add some delay for low levels
        if self.level < 3 and random.random() > 0.3:
            return None
            
        self.ammo -= 1
        self.fire_timer = self.stats["fire_rate"]
        
        bullets = []
        for _ in range(self.stats["pellets"]):
            spread_angle = self.angle + random.uniform(-self.stats["spread"], self.stats["spread"])
            bullets.append(Bullet(self.x, self.y, spread_angle, self.stats["damage"], self.stats["range"], "ai", color=(255, 100, 100)))
            
        if self.ammo <= 0:
            self.start_reload()
            
        return bullets

    def start_reload(self):
        if not self.reloading:
            self.reloading = True
            self.reload_timer = self.stats["reload_time"]

    def draw(self, screen):
        # Draw AI circle
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
        # Draw aim direction
        aim_x = self.x + math.cos(math.radians(self.angle)) * 25
        aim_y = self.y + math.sin(math.radians(self.angle)) * 25
        pygame.draw.line(screen, (255, 100, 100), (int(self.x), int(self.y)), (int(aim_x), int(aim_y)), 2)
        
        # Health bar
        bar_width = 40
        pygame.draw.rect(screen, (100, 0, 0), (self.x - bar_width//2, self.y - self.size - 10, bar_width, 5))
        pygame.draw.rect(screen, (255, 0, 0), (self.x - bar_width//2, self.y - self.size - 10, int(bar_width * (self.hp / self.hp_max)), 5))
        
        # Level text
        # (Font handling in main loop)
