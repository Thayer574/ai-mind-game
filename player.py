import pygame
import math
import random
from weapons import ARMOR_STATS, WEAPON_STATS
from bullets import Bullet
from grenades import Grenade

class Player:
    def __init__(self, x, y, armor_type, primary_type, secondary_type):
        self.x = x
        self.y = y
        self.armor_type = armor_type
        self.primary_type = primary_type
        self.secondary_type = secondary_type
        self.current_weapon_slot = "primary"
        self.size = 10 # SCALED DOWN
        self.angle = 0
        
        # Load armor stats
        self.hp_max = float(ARMOR_STATS[armor_type]["hp"])
        self.hp = self.hp_max
        self.base_speed = ARMOR_STATS[armor_type]["speed"]
        self.color = ARMOR_STATS[armor_type]["color"]
        
        # TACTICAL REFINEMENT: Stamina & Sprint
        self.stamina_max = 100
        self.stamina = 100
        self.is_sprinting = False
        self.stamina_regen = 0.2
        self.stamina_drain = 0.5
        
        # Initialize weapon states
        self.weapons = {
            "primary": {
                "type": primary_type,
                "stats": WEAPON_STATS[primary_type].copy(),
                "ammo": WEAPON_STATS[primary_type]["ammo"],
                "reloading": False,
                "reload_timer": 0,
                "fire_timer": 0,
                "upgrades": []
            },
            "secondary": {
                "type": secondary_type,
                "stats": WEAPON_STATS[secondary_type].copy(),
                "ammo": WEAPON_STATS[secondary_type]["ammo"],
                "reloading": False,
                "reload_timer": 0,
                "fire_timer": 0,
                "upgrades": []
            }
        }
        
        # Grenades
        self.grenades = {"frag": 2, "flash": 1}
        self.grenade_timer = 0
        
        # Status effects
        self.blind_timer = 0
        self.stun_timer = 0 # Cannot shoot while stunned
        self.bleeding_stacks = 0
        self.bleed_timer = 0
        
        self.vx = 0
        self.vy = 0

    @property
    def current_weapon(self):
        return self.weapons[self.current_weapon_slot]

    def switch_weapon(self):
        if self.stun_timer > 0: return
        self.current_weapon_slot = "secondary" if self.current_weapon_slot == "primary" else "primary"

    def update(self, dt, keys, mouse_pos, obstacles, upgrades):
        # Status Effects
        if self.blind_timer > 0: self.blind_timer -= dt
        if self.stun_timer > 0: self.stun_timer -= dt
        
        # Bleeding logic
        if self.bleeding_stacks > 0:
            self.bleed_timer += dt
            if self.bleed_timer >= 1000:
                self.hp -= self.hp_max * 0.01 * self.bleeding_stacks
                self.bleed_timer = 0
            
        # Angle to mouse
        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        self.angle = math.degrees(math.atan2(dy, dx))
        
        # TACTICAL SPRINT & STAMINA
        self.is_sprinting = keys[pygame.K_LSHIFT] and self.stamina > 0
        if self.is_sprinting:
            self.stamina -= self.stamina_drain
            if self.stamina < 0:
                self.stamina = 0
                self.is_sprinting = False
        else:
            self.stamina = min(self.stamina_max, self.stamina + self.stamina_regen)
            
        # TACTICAL SPEED: Base * Weapon Penalty
        current_speed = self.base_speed * self.current_weapon["stats"]["speed_penalty"]
        if self.is_sprinting: current_speed *= 1.5 # Sprint boost
        if self.blind_timer > 0: current_speed *= 0.4
        if self.stun_timer > 0: current_speed *= 0.2 # Heavily slowed when stunned
            
        # Movement
        move_x, move_y = 0, 0
        if keys[pygame.K_w]: move_y -= 1
        if keys[pygame.K_s]: move_y += 1
        if keys[pygame.K_a]: move_x -= 1
        if keys[pygame.K_d]: move_x += 1
            
        if move_x != 0 and move_y != 0:
            length = math.sqrt(move_x**2 + move_y**2)
            move_x /= length
            move_y /= length
            
        self.vx = move_x * current_speed
        self.vy = move_y * current_speed
        
        # Collision
        new_rect_x = pygame.Rect(self.x + self.vx - self.size, self.y - self.size, self.size * 2, self.size * 2)
        if not any(new_rect_x.colliderect(w) for w in obstacles):
            self.x += self.vx
        new_rect_y = pygame.Rect(self.x - self.size, self.y + self.vy - self.size, self.size * 2, self.size * 2)
        if not any(new_rect_y.colliderect(w) for w in obstacles):
            self.y += self.vy
            
        # Update weapon timers
        for slot in ["primary", "secondary"]:
            w = self.weapons[slot]
            if w["fire_timer"] > 0: w["fire_timer"] -= dt
            if w["reloading"]:
                w["reload_timer"] -= dt
                if w["reload_timer"] <= 0:
                    w["reloading"] = False
                    w["ammo"] = w["stats"]["ammo"]
                    
        if self.grenade_timer > 0: self.grenade_timer -= dt

    def fire(self, upgrades):
        # CANNOT SHOOT IF SPRINTING OR STUNNED
        if self.blind_timer > 0 or self.is_sprinting or self.stun_timer > 0: return None 
        w = self.current_weapon
        
        if w["reloading"] or w["fire_timer"] > 0: return None
        if w["ammo"] <= 0:
            self.start_reload()
            return None
            
        w["ammo"] -= 1
        w["fire_timer"] = w["stats"]["fire_rate"]
        
        bullets = []
        shot_count = w["stats"]["pellets"]
            
        for _ in range(shot_count):
            spread_angle = self.angle + random.uniform(-w["stats"]["spread"], w["stats"]["spread"])
            bullets.append(Bullet(self.x, self.y, spread_angle, w["stats"]["damage"], w["stats"]["range"], "player", speed=w["stats"].get("bullet_speed", 15)))
            
        if w["ammo"] <= 0: self.start_reload()
        return bullets

    def take_damage(self, amount, upgrades):
        self.hp -= amount
        return amount

    def throw_grenade(self, g_type):
        if self.stun_timer > 0: return None
        if self.grenades[g_type] > 0 and self.grenade_timer <= 0:
            self.grenades[g_type] -= 1
            self.grenade_timer = 1000
            return Grenade(self.x, self.y, self.angle, g_type, "player")
        return None

    def start_reload(self):
        if self.stun_timer > 0: return
        w = self.current_weapon
        if not w["reloading"] and w["ammo"] < w["stats"]["ammo"]:
            w["reloading"] = True
            w["reload_timer"] = w["stats"]["reload_time"]

    def draw(self, screen):
        # Draw blind effect
        if self.blind_timer > 0:
            blind_surf = pygame.Surface((1280, 720))
            blind_surf.set_alpha(int(255 * (self.blind_timer / 3500)))
            blind_surf.fill((255, 255, 255))
            screen.blit(blind_surf, (0, 0))

        # Stun effect (white ring)
        if self.stun_timer > 0:
            pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.size + 6, 2)

        # Sprint effect (subtle glow)
        if self.is_sprinting:
            pygame.draw.circle(screen, (200, 255, 255), (int(self.x), int(self.y)), self.size + 3, 1)

        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
        aim_x = self.x + math.cos(math.radians(self.angle)) * 20
        aim_y = self.y + math.sin(math.radians(self.angle)) * 20
        pygame.draw.line(screen, (255, 255, 255), (int(self.x), int(self.y)), (int(aim_x), int(aim_y)), 2)
        
        # HP bar
        bar_width = 30
        pygame.draw.rect(screen, (50, 0, 0), (self.x - bar_width//2, self.y - self.size - 8, bar_width, 4))
        pygame.draw.rect(screen, (0, 255, 0), (self.x - bar_width//2, self.y - self.size - 8, int(bar_width * (max(0, self.hp) / self.hp_max)), 4))
