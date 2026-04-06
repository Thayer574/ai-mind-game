import pygame
import math
import random
from weapons import ARMOR_STATS, WEAPON_STATS
from bullets import Bullet
from grenades import Grenade

class AI:
    def __init__(self, x, y, level, sub_level=1, role=None):
        self.x = x
        self.y = y
        self.level = level
        self.sub_level = sub_level
        self.size = 10 
        self.angle = 180
        
        # SQUAD ROLE SPECIALIZATION
        if role is None:
            roles = ["scout", "assault", "heavy", "sniper"]
            self.role = random.choice(roles)
        else:
            self.role = role
            
        # Loadout based on Role and Level
        if self.role == "scout":
            self.armor_type = "none" if level < 5 else "light"
            self.weapon_type = "smg" if level < 3 else "auto_pistol" if random.random() > 0.5 else "smg"
        elif self.role == "assault":
            self.armor_type = "light" if level < 4 else "medium"
            self.weapon_type = "ar" if level < 6 else "shotgun" if random.random() > 0.5 else "ar"
        elif self.role == "heavy":
            self.armor_type = "medium" if level < 5 else "heavy"
            self.weapon_type = "lmg"
        elif self.role == "sniper":
            self.armor_type = "none" if level < 6 else "light"
            self.weapon_type = "dmr" if level < 4 else "sniper"
            
        # Load stats
        self.hp_max = float(ARMOR_STATS[self.armor_type]["hp"])
        # ELITE SCALING: Level 2 is significantly stronger than Level 1
        self.hp_max *= (1.0 + (level - 1) * 0.75) 
        self.hp = self.hp_max
        
        self.base_speed = ARMOR_STATS[self.armor_type]["speed"]
        self.color = (255, 60, 60)
        
        self.stats = WEAPON_STATS[self.weapon_type].copy()
        # AI fire rate improves with level
        self.stats["fire_rate"] *= max(0.5, 1.4 - (level * 0.25))
        self.ammo = self.stats["ammo"]
        self.reloading = False
        self.reload_timer = 0
        self.fire_timer = 0
        
        # Tactical Gear
        self.grenades = {"frag": 1 if level > 1 else 0, "flash": 1 if level > 2 else 0}
        self.grenade_timer = 0
        
        # Status effects
        self.blind_timer = 0
        self.stun_timer = 0 # Cannot shoot while stunned
        self.bleeding_stacks = 0
        self.bleed_timer = 0
        
        # NEURAL EVOLUTION: Learn from player and squad coordination
        self.target_pos = (x, y)
        self.move_timer = 0
        self.accuracy_offset = max(0, 15 - level * 4)
        self.state = "patrol" 
        self.vx = 0
        self.vy = 0
        
        # Tactical state
        self.is_holding_angle = False
        self.holding_timer = 0
        self.flank_dir = random.choice([-1, 1])

    def update(self, dt, player, obstacles, arena, squad_members):
        if self.bleeding_stacks > 0:
            self.bleed_timer += dt
            if self.bleed_timer >= 1000:
                self.hp -= self.hp_max * 0.01 * self.bleeding_stacks
                self.bleed_timer = 0
        if self.blind_timer > 0: self.blind_timer -= dt
        if self.stun_timer > 0: self.stun_timer -= dt
            
        self.update_tactics(dt, player, obstacles, arena, squad_members)
        
        current_speed = self.base_speed * self.stats["speed_penalty"]
        if self.blind_timer > 0: current_speed *= 0.3
        if self.stun_timer > 0: current_speed *= 0.2 # Heavily slowed when stunned
            
        dx = self.target_pos[0] - self.x
        dy = self.target_pos[1] - self.y
        dist = math.sqrt(dx**2 + dy**2)
        
        self.vx, self.vy = 0, 0
        if dist > 12:
            self.vx = (dx / dist) * current_speed
            self.vy = (dy / dist) * current_speed
            
            # Collision
            new_rect_x = pygame.Rect(self.x + self.vx - self.size, self.y - self.size, self.size * 2, self.size * 2)
            if not any(new_rect_x.colliderect(w) for w in obstacles):
                self.x += self.vx
            new_rect_y = pygame.Rect(self.x - self.size, self.y + self.vy - self.size, self.size * 2, self.size * 2)
            if not any(new_rect_y.colliderect(w) for w in obstacles):
                self.y += self.vy
        
        self.update_aim(player)
        
        if self.fire_timer > 0: self.fire_timer -= dt
        if self.reloading:
            self.reload_timer -= dt
            if self.reload_timer <= 0:
                self.reloading = False
                self.ammo = self.stats["ammo"]
        if self.grenade_timer > 0: self.grenade_timer -= dt

    def update_aim(self, player):
        dx = player.x - self.x
        dy = player.y - self.y
        base_angle = math.degrees(math.atan2(dy, dx))
        
        if self.level >= 2: 
            dist = math.sqrt(dx**2 + dy**2)
            bullet_speed = self.stats.get("bullet_speed", 15)
            time_to_reach = dist / bullet_speed
            # Level 2 AI has much better predictive aiming
            target_x = player.x + player.vx * time_to_reach * 0.98
            target_y = player.y + player.vy * time_to_reach * 0.98
            base_angle = math.degrees(math.atan2(target_y - self.y, target_x - self.x))
            
        if self.accuracy_offset > 0:
            base_angle += random.uniform(-self.accuracy_offset, self.accuracy_offset)
        self.angle = base_angle

    def update_tactics(self, dt, player, obstacles, arena, squad_members):
        visible = arena.is_visible((self.x, self.y), (player.x, player.y))
        dist_to_player = math.sqrt((player.x - self.x)**2 + (player.y - self.y)**2)
        
        self.move_timer -= dt
        if self.move_timer <= 0:
            # SQUAD TACTICS: Level 1 is individual, Level 2+ works as a team
            if self.level == 1:
                self.individual_tactics(player, obstacles, arena, dist_to_player, visible)
            else:
                self.squad_tactics(player, obstacles, arena, dist_to_player, visible, squad_members)
            
            # Clamp target pos
            self.target_pos = (max(40, min(arena.play_width-40, self.target_pos[0])),
                               max(40, min(arena.height-40, self.target_pos[1])))
            
            # Decision timer based on level
            self.move_timer = 1500 - min(1000, self.level * 200)

    def individual_tactics(self, player, obstacles, arena, dist, visible):
        # Dumb individual behavior: Just move to random nearby spots or towards player
        if self.hp < self.hp_max * 0.3:
            self.find_cover_away_from(player, obstacles, arena)
        elif not visible:
            self.target_pos = (player.x + random.randint(-150, 150), player.y + random.randint(-150, 150))
        else:
            # Move slightly to stay in range but not too close
            angle = math.atan2(self.y - player.y, self.x - player.x)
            target_dist = self.stats["range"] * 0.7
            self.target_pos = (player.x + math.cos(angle) * target_dist, player.y + math.sin(angle) * target_dist)

    def squad_tactics(self, player, obstacles, arena, dist, visible, squad_members):
        # ADVANCED SQUAD TACTICS: Work together based on roles
        if self.hp < self.hp_max * 0.2:
            self.find_cover_away_from(player, obstacles, arena)
            return

        # SQUAD ROLES IN ACTION
        if self.role == "sniper":
            # Snipers hold long angles and retreat if player gets close
            if dist < 400:
                self.find_cover_away_from(player, obstacles, arena)
            else:
                # Find a spot with line of sight but far away
                self.target_pos = (self.x + random.randint(-50, 50), self.y + random.randint(-50, 50))
        
        elif self.role == "heavy":
            # Heavies push slowly to suppress player
            angle_to_player = math.atan2(player.y - self.y, player.x - self.x)
            # Push to medium range
            self.target_pos = (player.x + math.cos(angle_to_player + math.pi) * 300,
                               player.y + math.sin(angle_to_player + math.pi) * 300)
            
        elif self.role == "scout":
            # Scouts flank wide while others push
            angle_to_player = math.atan2(player.y - self.y, player.x - self.x)
            flank_angle = angle_to_player + (math.pi/2 * self.flank_dir)
            self.target_pos = (player.x + math.cos(flank_angle) * 250, player.y + math.sin(flank_angle) * 250)
            
        elif self.role == "assault":
            # Assaults push together into player's room
            # COORDINATION: If others are pushing, assault pushes the doorway
            self.target_pos = (player.x + random.randint(-60, 60), player.y + random.randint(-60, 60))

    def find_cover_away_from(self, player, obstacles, arena):
        best_pos = (self.x, self.y)
        max_safety = -1
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(120, 300)
            tx = self.x + math.cos(angle) * dist
            ty = self.y + math.sin(angle) * dist
            if 40 < tx < arena.play_width - 40 and 40 < ty < arena.height - 40:
                if not arena.is_visible((tx, ty), (player.x, player.y)):
                    safety = math.sqrt((tx - player.x)**2 + (ty - player.y)**2)
                    if safety > max_safety:
                        max_safety = safety
                        best_pos = (tx, ty)
        self.target_pos = best_pos

    def fire(self, player, arena):
        # CANNOT SHOOT IF STUNNED
        if self.blind_timer > 0 or self.stun_timer > 0 or self.reloading or self.fire_timer > 0: return None
        if self.ammo <= 0:
            self.start_reload()
            return None
        if not arena.is_visible((self.x, self.y), (player.x, player.y)): return None
        
        dist = math.sqrt((player.x - self.x)**2 + (player.y - self.y)**2)
        if dist > self.stats["range"]: return None
        
        self.ammo -= 1
        self.fire_timer = self.stats["fire_rate"]
        
        bullets = []
        bullet_speed = self.stats.get("bullet_speed", 15)
        for _ in range(self.stats["pellets"]):
            spread_angle = self.angle + random.uniform(-self.stats["spread"], self.stats["spread"])
            bullets.append(Bullet(self.x, self.y, spread_angle, self.stats["damage"], self.stats["range"], "ai", color=(255, 100, 100), speed=bullet_speed))
        return bullets

    def check_grenade(self, player, arena):
        if self.blind_timer > 0 or self.stun_timer > 0 or self.grenade_timer > 0: return None
        dist = math.sqrt((player.x - self.x)**2 + (player.y - self.y)**2)
        
        # Tactical Grenade Throwing
        if 200 < dist < 800 and random.random() < 0.02:
            visible = arena.is_visible((self.x, self.y), (player.x, player.y))
            if not visible and self.grenades["frag"] > 0:
                self.grenades["frag"] -= 1
                self.grenade_timer = 4000
                return Grenade(self.x, self.y, self.angle, "frag", "ai")
            elif visible and self.grenades["flash"] > 0:
                self.grenades["flash"] -= 1
                self.grenade_timer = 5000
                return Grenade(self.x, self.y, self.angle, "flash", "ai")
        return None

    def start_reload(self):
        if not self.reloading:
            self.reloading = True
            self.reload_timer = self.stats["reload_time"]

    def draw(self, screen):
        # Draw stun effect (white glow)
        if self.stun_timer > 0:
            pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.size + 6, 2)
            
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
        aim_x = self.x + math.cos(math.radians(self.angle)) * 20
        aim_y = self.y + math.sin(math.radians(self.angle)) * 20
        pygame.draw.line(screen, (255, 100, 100), (int(self.x), int(self.y)), (int(aim_x), int(aim_y)), 2)
        
        bar_width = 30
        pygame.draw.rect(screen, (100, 0, 0), (self.x - bar_width//2, self.y - self.size - 8, bar_width, 4))
        pygame.draw.rect(screen, (255, 0, 0), (self.x - bar_width//2, self.y - self.size - 8, int(bar_width * (max(0, self.hp) / self.hp_max)), 4))
