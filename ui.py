import pygame
import json
import os

class UI:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.font_large = pygame.font.SysFont("Arial", 48, bold=True)
        self.font_medium = pygame.font.SysFont("Arial", 32, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 20)
        self.leaderboard_file = "data/leaderboard.json"
        
        # Load leaderboard
        if os.path.exists(self.leaderboard_file):
            try:
                with open(self.leaderboard_file, "r") as f:
                    self.leaderboard = json.load(f)
            except:
                self.leaderboard = []
        else:
            self.leaderboard = []

    def draw_text(self, text, font, color, x, y, center=False):
        surface = font.render(text, True, color)
        rect = surface.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        self.screen.blit(surface, rect)
        return rect

    def draw_button(self, text, x, y, w, h, hover=False):
        color = (100, 100, 100) if not hover else (150, 150, 150)
        rect = pygame.Rect(x - w//2, y - h//2, w, h)
        pygame.draw.rect(self.screen, color, rect, border_radius=5)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, 2, border_radius=5)
        self.draw_text(text, self.font_small, (255, 255, 255), x, y, center=True)
        return rect

    def draw_main_menu(self, mouse_pos):
        self.screen.fill((20, 20, 20))
        self.draw_text("AI MIND GAMES ARENA", self.font_large, (255, 255, 255), self.width//2, 150, center=True)
        
        play_btn = self.draw_button("START NEW GAME", self.width//2, 300, 250, 50, hover=pygame.Rect(self.width//2-125, 275, 250, 50).collidepoint(mouse_pos))
        leaderboard_btn = self.draw_button("LEADERBOARD", self.width//2, 380, 250, 50, hover=pygame.Rect(self.width//2-125, 355, 250, 50).collidepoint(mouse_pos))
        quit_btn = self.draw_button("QUIT", self.width//2, 460, 250, 50, hover=pygame.Rect(self.width//2-125, 435, 250, 50).collidepoint(mouse_pos))
        
        return play_btn, leaderboard_btn, quit_btn

    def draw_loadout_screen(self, mouse_pos, selected_armor, selected_weapon):
        self.screen.fill((20, 20, 20))
        self.draw_text("CHOOSE LOADOUT", self.font_medium, (255, 255, 255), self.width//2, 100, center=True)
        
        # Armor Selection
        armors = ["none", "light", "medium", "heavy"]
        armor_btns = []
        self.draw_text("Armor Type:", self.font_small, (200, 200, 200), 200, 180)
        for i, armor in enumerate(armors):
            is_selected = selected_armor == armor
            color = (0, 255, 0) if is_selected else (255, 255, 255)
            btn = self.draw_button(armor.upper(), 200 + i*150, 230, 130, 40, hover=is_selected or pygame.Rect(135 + i*150, 210, 130, 40).collidepoint(mouse_pos))
            armor_btns.append((btn, armor))
            
        # Weapon Selection
        weapons = ["shotgun", "sniper", "dmr", "ar", "smg", "lmg"]
        weapon_btns = []
        self.draw_text("Primary Weapon:", self.font_small, (200, 200, 200), 200, 300)
        for i, weapon in enumerate(weapons):
            is_selected = selected_weapon == weapon
            color = (0, 255, 0) if is_selected else (255, 255, 255)
            row = i // 3
            col = i % 3
            btn = self.draw_button(weapon.upper(), 200 + col*200, 350 + row*60, 180, 40, hover=is_selected or pygame.Rect(110 + col*200, 330 + row*60, 180, 40).collidepoint(mouse_pos))
            weapon_btns.append((btn, weapon))
            
        start_btn = self.draw_button("ENTER ARENA", self.width//2, 550, 250, 60, hover=pygame.Rect(self.width//2-125, 520, 250, 60).collidepoint(mouse_pos))
        
        return armor_btns, weapon_btns, start_btn

    def draw_upgrade_screen(self, mouse_pos, upgrades):
        self.screen.fill((30, 30, 40))
        self.draw_text("VICTORY! CHOOSE AN UPGRADE", self.font_medium, (255, 255, 0), self.width//2, 100, center=True)
        
        upgrade_btns = []
        for i, upgrade in enumerate(upgrades):
            rect = pygame.Rect(self.width//2 - 300, 180 + i*80, 600, 60)
            hover = rect.collidepoint(mouse_pos)
            color = (80, 80, 120) if not hover else (100, 100, 150)
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 2, border_radius=10)
            
            self.draw_text(upgrade['name'], self.font_small, (255, 255, 255), self.width//2, 200 + i*80, center=True)
            self.draw_text(upgrade['desc'], self.font_small, (200, 200, 200), self.width//2, 225 + i*80, center=True)
            upgrade_btns.append((rect, upgrade))
            
        return upgrade_btns

    def draw_game_over(self, mouse_pos, level, score):
        self.screen.fill((50, 10, 10))
        self.draw_text("DEFEAT", self.font_large, (255, 50, 50), self.width//2, 150, center=True)
        self.draw_text(f"Level Reached: {level}", self.font_medium, (255, 255, 255), self.width//2, 250, center=True)
        self.draw_text(f"Final Score: {score}", self.font_medium, (255, 255, 255), self.width//2, 300, center=True)
        
        menu_btn = self.draw_button("MAIN MENU", self.width//2, 450, 250, 50, hover=pygame.Rect(self.width//2-125, 425, 250, 50).collidepoint(mouse_pos))
        return menu_btn

    def draw_leaderboard(self, mouse_pos):
        self.screen.fill((20, 20, 20))
        self.draw_text("TOP OPERATORS", self.font_medium, (255, 255, 255), self.width//2, 80, center=True)
        
        # Draw header
        self.draw_text("RANK", self.font_small, (150, 150, 150), 200, 150)
        self.draw_text("LEVEL", self.font_small, (150, 150, 150), 400, 150)
        self.draw_text("SCORE", self.font_small, (150, 150, 150), 600, 150)
        
        # Sort and show top 10
        sorted_scores = sorted(self.leaderboard, key=lambda x: x['score'], reverse=True)[:10]
        for i, entry in enumerate(sorted_scores):
            self.draw_text(str(i+1), self.font_small, (255, 255, 255), 200, 200 + i*30)
            self.draw_text(str(entry['level']), self.font_small, (255, 255, 255), 400, 200 + i*30)
            self.draw_text(str(entry['score']), self.font_small, (255, 255, 255), 600, 200 + i*30)
            
        back_btn = self.draw_button("BACK", self.width//2, 550, 200, 50, hover=pygame.Rect(self.width//2-100, 525, 200, 50).collidepoint(mouse_pos))
        return back_btn

    def save_score(self, level, score):
        self.leaderboard.append({"level": level, "score": score})
        # Keep only top 50
        self.leaderboard = sorted(self.leaderboard, key=lambda x: x['score'], reverse=True)[:50]
        try:
            with open(self.leaderboard_file, "w") as f:
                json.dump(self.leaderboard, f)
        except:
            pass
