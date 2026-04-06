import pygame
import random
import math
from arena import Arena
from player import Player
from ai import AI
from ui import UI
from upgrades import UpgradeManager
from weapons import WEAPON_STATS

# Constants
FPS = 60
SIDEBAR_WIDTH = 300

class Game:
    def __init__(self):
        pygame.init()
        self.width, self.height = 1280, 720
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("MIND GAMES: ADVANCED SQUAD TACTICS")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.ui = UI(self.screen, self.width, self.height, SIDEBAR_WIDTH)
        self.upgrade_manager = UpgradeManager()
        
        self.state = "main_menu"
        self.level = 1
        self.sub_level = 1 # 1-4 AI squad size
        self.score = 0
        self.player = None
        self.ais = []
        self.arena = Arena(self.width, self.height, SIDEBAR_WIDTH)
        self.bullets = []
        self.grenades = []
        
        self.selected_armor = "medium"
        self.selected_weapon = "ar"
        self.selected_secondary = "pistol"
        
        self.screen_shake = 0
        self.hit_markers = []

    def start_new_game(self):
        self.level = 1
        self.sub_level = 1
        self.score = 0
        self.upgrade_manager.currency = 0
        self.state = "loadout"

    def enter_arena(self):
        self.arena.setup_arena()
        # Safe corner spawn
        spawn_x, spawn_y = 60, 60
        self.player = Player(spawn_x, spawn_y, self.selected_armor, self.selected_weapon, self.selected_secondary)
        self.player.size = 10 
        self.spawn_ais()
        self.bullets = []
        self.grenades = []
        self.state = "playing"

    def spawn_ais(self):
        self.ais = []
        # Spawn in bottom-right corner area
        base_x = self.arena.play_width - 80
        base_y = self.height - 80
        roles = ["scout", "assault", "heavy", "sniper"]
        
        for i in range(self.sub_level):
            offset_x = (i % 2) * 60
            offset_y = (i // 2) * 60
            role = roles[i % len(roles)]
            self.ais.append(AI(base_x - offset_x, base_y - offset_y, self.level, i+1, role=role))

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: self.running = False
                if self.state == "playing":
                    if event.key == pygame.K_SPACE: self.player.switch_weapon()
                    elif event.key == pygame.K_r: self.player.start_reload()
                    elif event.key == pygame.K_1: 
                        g = self.player.throw_grenade("frag")
                        if g: self.grenades.append(g)
                    elif event.key == pygame.K_2:
                        g = self.player.throw_grenade("flash")
                        if g: self.grenades.append(g)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == "main_menu":
                    play_btn, lb_btn, quit_btn = self.ui.draw_main_menu(mouse_pos)
                    if play_btn.collidepoint(mouse_pos): self.start_new_game()
                    elif lb_btn.collidepoint(mouse_pos): self.state = "leaderboard"
                    elif quit_btn.collidepoint(mouse_pos): self.running = False
                elif self.state == "loadout":
                    armor_btns, weapon_btns, sec_btns, start_btn = self.ui.draw_loadout_screen(mouse_pos, self.selected_armor, self.selected_weapon, self.selected_secondary)
                    for btn, armor in armor_btns:
                        if btn.collidepoint(mouse_pos): self.selected_armor = armor
                    for btn, weapon in weapon_btns:
                        if btn.collidepoint(mouse_pos): self.selected_weapon = weapon
                    for btn, sec in sec_btns:
                        if btn.collidepoint(mouse_pos): self.selected_secondary = sec
                    if start_btn.collidepoint(mouse_pos): self.enter_arena()
                elif self.state == "game_over":
                    menu_btn = self.ui.draw_game_over(mouse_pos, self.level, self.score)
                    if menu_btn.collidepoint(mouse_pos): self.state = "main_menu"
                elif self.state == "leaderboard":
                    back_btn = self.ui.draw_leaderboard(mouse_pos)
                    if back_btn.collidepoint(mouse_pos): self.state = "main_menu"

    def advance_progression(self):
        if self.sub_level < 4:
            self.sub_level += 1
        else:
            self.sub_level = 1
            self.level += 1
            
        self.bullets = []
        self.grenades = []
        self.arena.setup_arena()
        self.player.x, self.player.y = 60, 60
        self.spawn_ais()
        
        # FULL RESET
        self.player.hp = self.player.hp_max
        self.player.stamina = self.player.stamina_max
        for slot in ["primary", "secondary"]:
            w = self.player.weapons[slot]
            w["ammo"] = w["stats"]["ammo"]
            w["reloading"] = False
        self.player.grenades = {"frag": 2, "flash": 1}
        self.state = "playing"

    def update(self):
        dt = self.clock.tick(FPS)
        if self.state == "playing":
            keys = pygame.key.get_pressed()
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            
            should_fire = False
            w = self.player.current_weapon
            if w["stats"]["is_auto"]:
                if mouse_pressed[0]: should_fire = True
            else:
                if mouse_pressed[0] and w["fire_timer"] <= 0: should_fire = True

            if should_fire:
                new_bullets = self.player.fire(self.upgrade_manager)
                if new_bullets: self.bullets.extend(new_bullets)
            
            self.player.update(dt, keys, mouse_pos, self.arena.obstacles, self.upgrade_manager)
            
            for ai in self.ais:
                # Pass other squad members for coordination
                ai.update(dt, self.player, self.arena.obstacles, self.arena, [a for a in self.ais if a != ai])
                ai_bullets = ai.fire(self.player, self.arena)
                if ai_bullets: self.bullets.extend(ai_bullets)
                ai_grenade = ai.check_grenade(self.player, self.arena)
                if ai_grenade: self.grenades.append(ai_grenade)
            
            for g in self.grenades[:]:
                g.update(dt, self.arena.obstacles)
                if g.exploded:
                    targets = [self.player] + self.ais
                    for target in targets:
                        # Check hit with LOS and fragmentation damage
                        result = g.check_hit(target, self.arena)
                        if result:
                            if g.type == "frag":
                                # result is damage value
                                if target == self.player:
                                    self.player.take_damage(result, self.upgrade_manager)
                                    self.screen_shake = 25
                                else:
                                    target.hp -= result
                            elif g.type == "flash":
                                # result is True
                                target.blind_timer = g.stats["blind_duration"]
                    self.grenades.remove(g)
                    if self.player.hp <= 0: self.game_over()
                    self.ais = [ai for ai in self.ais if ai.hp > 0]
                    if not self.ais: self.victory()
            
            for b in self.bullets[:]:
                b.update(self.arena.obstacles, ricochet=False)
                if not b.alive:
                    if b in self.bullets: self.bullets.remove(b)
                    continue
                
                bullet_rect = pygame.Rect(b.x - b.size, b.y - b.size, b.size*2, b.size*2)
                if b.owner_type == "player":
                    for ai in self.ais[:]:
                        ai_rect = pygame.Rect(ai.x - ai.size, ai.y - ai.size, ai.size*2, ai.size*2)
                        if bullet_rect.colliderect(ai_rect):
                            ai.hp -= b.damage
                            b.alive = False
                            if b in self.bullets: self.bullets.remove(b)
                            self.hit_markers.append({"x": b.x, "y": b.y, "timer": 10})
                            if ai.hp <= 0:
                                self.ais.remove(ai)
                                if not self.ais: self.victory()
                            break
                else:
                    player_rect = pygame.Rect(self.player.x - self.player.size, self.player.y - self.player.size, self.player.size*2, self.player.size*2)
                    if bullet_rect.colliderect(player_rect):
                        self.player.take_damage(b.damage, self.upgrade_manager)
                        self.screen_shake = 12
                        b.alive = False
                        if b in self.bullets: self.bullets.remove(b)
                        if self.player.hp <= 0: self.game_over()
            
            if self.screen_shake > 0: self.screen_shake *= 0.85
            if self.screen_shake < 0.5: self.screen_shake = 0
            for hm in self.hit_markers[:]:
                hm["timer"] -= 1
                if hm["timer"] <= 0: self.hit_markers.remove(hm)

    def victory(self):
        self.score += self.level * 100 * self.sub_level
        self.advance_progression()

    def game_over(self):
        self.ui.save_score(self.level, self.score)
        self.state = "game_over"

    def draw(self):
        self.screen.fill(self.ui.colors["bg"])
        mouse_pos = pygame.mouse.get_pos()
        
        if self.state == "playing":
            shake_surface = pygame.Surface((self.width - SIDEBAR_WIDTH, self.height))
            self.arena.draw(shake_surface)
            self.player.draw(shake_surface)
            for ai in self.ais: ai.draw(shake_surface)
            for b in self.bullets: b.draw(shake_surface)
            for g in self.grenades: g.draw(shake_surface)
            for hm in self.hit_markers:
                pygame.draw.line(shake_surface, (255, 255, 255), (hm["x"]-6, hm["y"]-6), (hm["x"]+6, hm["y"]+6), 2)
                pygame.draw.line(shake_surface, (255, 255, 255), (hm["x"]+6, hm["y"]-6), (hm["x"]-6, hm["y"]+6), 2)
            
            offset_x = random.randint(-int(self.screen_shake), int(self.screen_shake))
            offset_y = random.randint(-int(self.screen_shake), int(self.screen_shake))
            self.screen.blit(shake_surface, (offset_x, offset_y))
            
            self.ui.draw_sidebar(self.level, self.score, self.upgrade_manager.currency, self.player, self.ais, self.sub_level)
            
        elif self.state == "main_menu": self.ui.draw_main_menu(mouse_pos)
        elif self.state == "loadout": self.ui.draw_loadout_screen(mouse_pos, self.selected_armor, self.selected_weapon, self.selected_secondary)
        elif self.state == "game_over": self.ui.draw_game_over(mouse_pos, self.level, self.score)
        elif self.state == "leaderboard": self.ui.draw_leaderboard(mouse_pos)
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
