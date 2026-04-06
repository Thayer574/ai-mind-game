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
WIDTH, HEIGHT = 1000, 600
FPS = 60

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("AI Mind Games Arena")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.ui = UI(self.screen, WIDTH, HEIGHT)
        self.upgrade_manager = UpgradeManager()
        
        self.state = "main_menu" # main_menu, loadout, playing, victory, game_over, leaderboard
        
        # Game session data
        self.level = 1
        self.score = 0
        self.player = None
        self.ai = None
        self.arena = Arena(WIDTH, HEIGHT)
        self.bullets = []
        
        # Loadout selections
        self.selected_armor = "medium"
        self.selected_weapon = "ar"
        
        # UI interaction
        self.current_upgrades = []
        
        # Visual effects
        self.screen_shake = 0
        self.hit_markers = [] # (x, y, timer)

    def start_new_game(self):
        self.level = 1
        self.score = 0
        self.state = "loadout"

    def enter_arena(self):
        self.player = Player(100, HEIGHT//2, self.selected_armor, self.selected_weapon)
        self.spawn_ai()
        self.bullets = []
        self.state = "playing"

    def spawn_ai(self):
        ai_weapon = random.choice(["ar", "smg", "dmr"])
        if self.level > 5:
            ai_weapon = random.choice(["sniper", "lmg", "shotgun", "ar"])
        self.ai = AI(WIDTH - 100, HEIGHT//2, self.level, ai_weapon)

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == "main_menu":
                    play_btn, lb_btn, quit_btn = self.ui.draw_main_menu(mouse_pos)
                    if play_btn.collidepoint(mouse_pos):
                        self.start_new_game()
                    elif lb_btn.collidepoint(mouse_pos):
                        self.state = "leaderboard"
                    elif quit_btn.collidepoint(mouse_pos):
                        self.running = False
                elif self.state == "loadout":
                    armor_btns, weapon_btns, start_btn = self.ui.draw_loadout_screen(mouse_pos, self.selected_armor, self.selected_weapon)
                    for btn, armor in armor_btns:
                        if btn.collidepoint(mouse_pos):
                            self.selected_armor = armor
                    for btn, weapon in weapon_btns:
                        if btn.collidepoint(mouse_pos):
                            self.selected_weapon = weapon
                    if start_btn.collidepoint(mouse_pos):
                        self.enter_arena()
                elif self.state == "playing":
                    if event.button == 1:
                        new_bullets = self.player.fire()
                        if new_bullets:
                            self.bullets.extend(new_bullets)
                elif self.state == "victory":
                    upgrade_btns = self.ui.draw_upgrade_screen(mouse_pos, self.current_upgrades)
                    for rect, upgrade in upgrade_btns:
                        if rect.collidepoint(mouse_pos):
                            self.upgrade_manager.apply_upgrade(self.player, upgrade)
                            self.level += 1
                            self.spawn_ai()
                            self.bullets = []
                            self.player.hp = min(self.player.hp_max, self.player.hp + 1)
                            self.state = "playing"
                elif self.state == "game_over":
                    menu_btn = self.ui.draw_game_over(mouse_pos, self.level, self.score)
                    if menu_btn.collidepoint(mouse_pos):
                        self.state = "main_menu"
                elif self.state == "leaderboard":
                    back_btn = self.ui.draw_leaderboard(mouse_pos)
                    if back_btn.collidepoint(mouse_pos):
                        self.state = "main_menu"

    def update(self):
        dt = self.clock.tick(FPS)
        if self.state == "playing":
            keys = pygame.key.get_pressed()
            mouse_pos = pygame.mouse.get_pos()
            self.player.update(dt, keys, mouse_pos, self.arena.obstacles)
            self.ai.update(dt, self.player, self.arena.obstacles, self.arena)
            ai_bullets = self.ai.fire(self.player, self.arena)
            if ai_bullets:
                self.bullets.extend(ai_bullets)
            for b in self.bullets[:]:
                b.update(self.arena.obstacles)
                if not b.alive:
                    if b in self.bullets: self.bullets.remove(b)
                    continue
                bullet_rect = pygame.Rect(b.x - b.size, b.y - b.size, b.size*2, b.size*2)
                if b.owner_type == "player":
                    ai_rect = pygame.Rect(self.ai.x - self.ai.size, self.ai.y - self.ai.size, self.ai.size*2, self.ai.size*2)
                    if bullet_rect.colliderect(ai_rect):
                        self.ai.hp -= b.damage
                        b.alive = False
                        if b in self.bullets: self.bullets.remove(b)
                        self.player.hp = min(self.player.hp_max, self.player.hp + self.upgrade_manager.get_lifesteal())
                        self.hit_markers.append({"x": b.x, "y": b.y, "timer": 10})
                        if self.ai.hp <= 0:
                            self.victory()
                        continue
                else:
                    player_rect = pygame.Rect(self.player.x - self.player.size, self.player.y - self.player.size, self.player.size*2, self.player.size*2)
                    if bullet_rect.colliderect(player_rect):
                        if not self.upgrade_manager.check_dodge():
                            self.player.hp -= b.damage
                            self.screen_shake = 10
                        b.alive = False
                        if b in self.bullets: self.bullets.remove(b)
                        if self.player.hp <= 0:
                            self.game_over()
                        continue
            if self.screen_shake > 0:
                self.screen_shake -= 1
            for hm in self.hit_markers[:]:
                hm["timer"] -= 1
                if hm["timer"] <= 0:
                    self.hit_markers.remove(hm)

    def victory(self):
        self.score += self.level * 100
        self.current_upgrades = self.upgrade_manager.get_random_upgrades(3)
        self.state = "victory"

    def game_over(self):
        self.ui.save_score(self.level, self.score)
        self.state = "game_over"

    def draw(self):
        self.screen.fill((0, 0, 0))
        mouse_pos = pygame.mouse.get_pos()
        if self.state == "playing":
            shake_surface = pygame.Surface((WIDTH, HEIGHT))
            self.arena.draw(shake_surface)
            self.player.draw(shake_surface)
            self.ai.draw(shake_surface)
            for b in self.bullets:
                b.draw(shake_surface)
            for hm in self.hit_markers:
                pygame.draw.line(shake_surface, (255, 255, 255), (hm["x"]-5, hm["y"]-5), (hm["x"]+5, hm["y"]+5), 2)
                pygame.draw.line(shake_surface, (255, 255, 255), (hm["x"]+5, hm["y"]-5), (hm["x"]-5, hm["y"]+5), 2)
            
            offset_x = random.randint(-int(self.screen_shake), int(self.screen_shake))
            offset_y = random.randint(-int(self.screen_shake), int(self.screen_shake))
            self.screen.blit(shake_surface, (offset_x, offset_y))
            
            self.ui.draw_text(f"LEVEL: {self.level}", self.ui.font_small, (255, 255, 255), 20, 20)
            self.ui.draw_text(f"SCORE: {self.score}", self.ui.font_small, (255, 255, 255), 20, 50)
            ammo_text = f"AMMO: {self.player.ammo}/{self.player.stats['ammo']}"
            if self.player.reloading: ammo_text = "RELOADING..."
            self.ui.draw_text(ammo_text, self.ui.font_small, (255, 255, 0), 20, HEIGHT - 40)
        elif self.state == "main_menu":
            self.ui.draw_main_menu(mouse_pos)
        elif self.state == "loadout":
            self.ui.draw_loadout_screen(mouse_pos, self.selected_armor, self.selected_weapon)
        elif self.state == "victory":
            self.ui.draw_upgrade_screen(mouse_pos, self.current_upgrades)
        elif self.state == "game_over":
            self.ui.draw_game_over(mouse_pos, self.level, self.score)
        elif self.state == "leaderboard":
            self.ui.draw_leaderboard(mouse_pos)
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
