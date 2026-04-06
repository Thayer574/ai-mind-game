import pygame
import json
import os
from weapons import RARITY_COLORS

class UI:
    def __init__(self, screen, width, height, sidebar_width=300):
        self.screen = screen
        self.width = width
        self.height = height
        self.sidebar_width = sidebar_width
        self.play_width = width - sidebar_width
        
        self.font_title = pygame.font.SysFont("Verdana", 60, bold=True)
        self.font_header = pygame.font.SysFont("Verdana", 32, bold=True)
        self.font_main = pygame.font.SysFont("Verdana", 20)
        self.font_mono = pygame.font.SysFont("Courier", 18, bold=True)
        self.font_small = pygame.font.SysFont("Courier", 14)
        
        self.colors = {
            "bg": (10, 10, 15),
            "sidebar": (20, 20, 30),
            "accent": (0, 200, 255),
            "accent_hover": (0, 255, 255),
            "text": (230, 230, 230),
            "danger": (255, 60, 60),
            "success": (60, 255, 60),
            "warning": (255, 200, 0),
            "stamina": (0, 255, 200),
            "panel": (35, 35, 50),
            "border": (60, 60, 80)
        }
        
        self.leaderboard_file = "data/leaderboard.json"
        self.load_leaderboard()

    def load_leaderboard(self):
        if os.path.exists(self.leaderboard_file):
            try:
                with open(self.leaderboard_file, "r") as f:
                    self.leaderboard = json.load(f)
            except: self.leaderboard = []
        else: self.leaderboard = []

    def save_score(self, level, score):
        self.leaderboard.append({"level": level, "score": score})
        if not os.path.exists("data"): os.makedirs("data")
        with open(self.leaderboard_file, "w") as f:
            json.dump(self.leaderboard, f)

    def draw_text(self, text, font, color, x, y, center=False, shadow=True):
        if shadow:
            shadow_surf = font.render(text, True, (0, 0, 0))
            shadow_rect = shadow_surf.get_rect()
            if center: shadow_rect.center = (x+2, y+2)
            else: shadow_rect.topleft = (x+2, y+2)
            self.screen.blit(shadow_surf, shadow_rect)
            
        surface = font.render(text, True, color)
        rect = surface.get_rect()
        if center: rect.center = (x, y)
        else: rect.topleft = (x, y)
        self.screen.blit(surface, rect)
        return rect

    def draw_panel(self, x, y, w, h, title=""):
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, self.colors["panel"], rect, border_radius=5)
        pygame.draw.rect(self.screen, self.colors["border"], rect, 1, border_radius=5)
        if title:
            self.draw_text(title, self.font_small, self.colors["accent"], x + 10, y - 20)
        return rect

    def draw_button(self, text, x, y, w, h, hover=False, color=None):
        if color is None: color = self.colors["accent"]
        btn_rect = pygame.Rect(x - w//2, y - h//2, w, h)
        if hover:
            glow_rect = btn_rect.inflate(4, 4)
            pygame.draw.rect(self.screen, (*color, 50), glow_rect, border_radius=5)
            current_color = self.colors["accent_hover"]
        else: current_color = color
        pygame.draw.rect(self.screen, (20, 20, 30), btn_rect, border_radius=5)
        pygame.draw.rect(self.screen, current_color, btn_rect, 2, border_radius=5)
        self.draw_text(text, self.font_main, current_color, x, y, center=True)
        return btn_rect

    def draw_sidebar(self, level, score, currency, player, ais, sub_level):
        sidebar_rect = pygame.Rect(self.play_width, 0, self.sidebar_width, self.height)
        pygame.draw.rect(self.screen, self.colors["sidebar"], sidebar_rect)
        pygame.draw.line(self.screen, self.colors["border"], (self.play_width, 0), (self.play_width, self.height), 2)
        
        x_start = self.play_width + 15
        y_curr = 20
        
        # Mission Stats
        self.draw_text("MISSION DATA", self.font_mono, self.colors["accent"], x_start, y_curr)
        y_curr += 35
        self.draw_text(f"SECTOR: {level} (SQUAD: {sub_level})", self.font_main, self.colors["text"], x_start, y_curr)
        y_curr += 30
        self.draw_text(f"SCORE: {score}", self.font_main, self.colors["text"], x_start, y_curr)
        
        # Player Stats
        y_curr += 60
        self.draw_panel(x_start - 5, y_curr, self.sidebar_width - 25, 180, "PLAYER STATUS")
        y_curr += 15
        hp_pct = max(0, player.hp / player.hp_max)
        self.draw_text(f"HP: {int(player.hp)}/{int(player.hp_max)}", self.font_small, self.colors["text"], x_start + 5, y_curr)
        pygame.draw.rect(self.screen, (50, 0, 0), (x_start + 5, y_curr + 20, 260, 10))
        pygame.draw.rect(self.screen, self.colors["success"], (x_start + 5, y_curr + 20, int(260 * hp_pct), 10))
        
        # TACTICAL REFINEMENT: Stamina Bar
        y_curr += 45
        st_pct = max(0, player.stamina / player.stamina_max)
        self.draw_text(f"STAMINA (SHIFT): {int(player.stamina)}%", self.font_small, self.colors["text"], x_start + 5, y_curr)
        pygame.draw.rect(self.screen, (0, 50, 50), (x_start + 5, y_curr + 20, 260, 8))
        pygame.draw.rect(self.screen, self.colors["stamina"], (x_start + 5, y_curr + 20, int(260 * st_pct), 8))
        
        y_curr += 45
        w = player.current_weapon
        self.draw_text(f"WEAPON: {w['type'].upper()}", self.font_small, self.colors["accent"], x_start + 5, y_curr)
        y_curr += 25
        ammo_pct = max(0, w['ammo'] / w['stats']['ammo'])
        self.draw_text(f"AMMO: {w['ammo']}/{w['stats']['ammo']}", self.font_small, self.colors["warning"], x_start + 5, y_curr)
        pygame.draw.rect(self.screen, (40, 40, 50), (x_start + 5, y_curr + 20, 260, 10))
        pygame.draw.rect(self.screen, self.colors["warning"], (x_start + 5, y_curr + 20, int(260 * ammo_pct), 10))
        if w["reloading"]:
            self.draw_text("RELOADING...", self.font_small, self.colors["danger"], x_start + 140, y_curr)
            
        # AI Stats
        y_curr += 100
        self.draw_panel(x_start - 5, y_curr, self.sidebar_width - 25, 150, "INTEL: ENEMY TARGETS")
        y_curr += 15
        for i, ai in enumerate(ais):
            ai_hp_pct = max(0, ai.hp / ai.hp_max)
            label = f"AI-{i+1} [{ai.role.upper()}]"
            self.draw_text(label, self.font_small, self.colors["danger"], x_start + 5, y_curr)
            pygame.draw.rect(self.screen, (50, 0, 0), (x_start + 5, y_curr + 20, 260, 8))
            pygame.draw.rect(self.screen, self.colors["danger"], (x_start + 5, y_curr + 20, int(260 * ai_hp_pct), 8))
            y_curr += 40
            
        # Controls
        y_curr = self.height - 100
        self.draw_text(f"FRAG: {player.grenades['frag']} [1]", self.font_mono, self.colors["text"], x_start, y_curr)
        y_curr += 25
        self.draw_text(f"FLASH: {player.grenades['flash']} [2]", self.font_mono, self.colors["text"], x_start, y_curr)
        y_curr += 30
        self.draw_text("[SHIFT] SPRINT | [SPACE] SWITCH", self.font_small, (100, 100, 120), x_start, y_curr)

    def draw_main_menu(self, mouse_pos):
        self.screen.fill(self.colors["bg"])
        self.draw_text("MIND GAMES", self.font_title, self.colors["accent"], self.width//2, 200, center=True)
        self.draw_text("DEFINITIVE TACTICAL EDITION", self.font_header, self.colors["text"], self.width//2, 260, center=True)
        
        play_btn = self.draw_button("INITIATE COMBAT", self.width//2, 400, 300, 50, hover=pygame.Rect(self.width//2-150, 375, 300, 50).collidepoint(mouse_pos))
        lb_btn = self.draw_button("LEADERBOARD", self.width//2, 470, 300, 50, hover=pygame.Rect(self.width//2-150, 445, 300, 50).collidepoint(mouse_pos))
        quit_btn = self.draw_button("TERMINATE", self.width//2, 540, 300, 50, hover=pygame.Rect(self.width//2-150, 515, 300, 50).collidepoint(mouse_pos), color=self.colors["danger"])
        return play_btn, lb_btn, quit_btn

    def draw_loadout_screen(self, mouse_pos, selected_armor, selected_weapon, selected_secondary):
        self.screen.fill(self.colors["bg"])
        self.draw_text("LOADOUT SELECTION", self.font_header, self.colors["accent"], self.width//2, 60, center=True)
        
        self.draw_panel(100, 140, 800, 100, "CHASSIS")
        armors = ["none", "light", "medium", "heavy"]
        armor_btns = []
        for i, armor in enumerate(armors):
            is_selected = selected_armor == armor
            btn_color = self.colors["success"] if is_selected else self.colors["accent"]
            btn = self.draw_button(armor.upper(), 210 + i*195, 190, 170, 40, hover=pygame.Rect(125 + i*195, 170, 170, 40).collidepoint(mouse_pos), color=btn_color)
            armor_btns.append((btn, armor))
            
        self.draw_panel(100, 280, 800, 130, "PRIMARY")
        weapons = ["shotgun", "sniper", "dmr", "ar", "smg", "lmg"]
        weapon_btns = []
        for i, weapon in enumerate(weapons):
            is_selected = selected_weapon == weapon
            btn_color = self.colors["success"] if is_selected else self.colors["accent"]
            row, col = i // 3, i % 3
            btn = self.draw_button(weapon.upper(), 250 + col*250, 330 + row*50, 220, 40, hover=pygame.Rect(140 + col*250, 310 + row*50, 220, 40).collidepoint(mouse_pos), color=btn_color)
            weapon_btns.append((btn, weapon))
            
        self.draw_panel(100, 450, 800, 100, "SECONDARY")
        secondaries = ["pistol", "auto_pistol"]
        secondary_btns = []
        for i, sec in enumerate(secondaries):
            is_selected = selected_secondary == sec
            btn_color = self.colors["success"] if is_selected else self.colors["accent"]
            btn = self.draw_button(sec.replace("_", " ").upper(), 325 + i*350, 500, 300, 40, hover=pygame.Rect(175 + i*350, 480, 300, 40).collidepoint(mouse_pos), color=btn_color)
            secondary_btns.append((btn, sec))
            
        start_btn = self.draw_button("ENTER ARENA", self.width//2, 620, 300, 60, hover=pygame.Rect(self.width//2-150, 590, 300, 60).collidepoint(mouse_pos), color=self.colors["success"])
        return armor_btns, weapon_btns, secondary_btns, start_btn

    def draw_game_over(self, mouse_pos, level, score):
        self.screen.fill((40, 10, 10))
        self.draw_text("TERMINATED", self.font_title, self.colors["danger"], self.width//2, 250, center=True)
        self.draw_text(f"SECTOR REACHED: {level}", self.font_header, self.colors["text"], self.width//2, 330, center=True)
        self.draw_text(f"FINAL SCORE: {score}", self.font_header, self.colors["text"], self.width//2, 390, center=True)
        menu_btn = self.draw_button("MAIN MENU", self.width//2, 520, 250, 50, hover=pygame.Rect(self.width//2-125, 495, 250, 50).collidepoint(mouse_pos))
        return menu_btn

    def draw_leaderboard(self, mouse_pos):
        self.screen.fill(self.colors["bg"])
        self.draw_text("TOP OPERATORS", self.font_header, self.colors["accent"], self.width//2, 100, center=True)
        self.draw_text("RANK", self.font_mono, (150, 150, 150), 300, 200)
        self.draw_text("LEVEL", self.font_mono, (150, 150, 150), 500, 200)
        self.draw_text("SCORE", self.font_mono, (150, 150, 150), 700, 200)
        sorted_scores = sorted(self.leaderboard, key=lambda x: x['score'], reverse=True)[:10]
        for i, entry in enumerate(sorted_scores):
            self.draw_text(str(i+1), self.font_mono, self.colors["text"], 300, 250 + i*35)
            self.draw_text(str(entry['level']), self.font_mono, self.colors["text"], 500, 250 + i*35)
            self.draw_text(str(entry['score']), self.font_mono, self.colors["text"], 700, 250 + i*35)
        back_btn = self.draw_button("BACK", self.width//2, 650, 200, 50, hover=pygame.Rect(self.width//2-100, 625, 200, 50).collidepoint(mouse_pos))
        return back_btn
    
    def draw_upgrade_screen(self, mouse_pos, upgrades, currency):
        # Kept for compatibility but bypassed in main loop
        return [], pygame.Rect(0,0,0,0)
