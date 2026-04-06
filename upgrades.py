import random

class UpgradeManager:
    def __init__(self):
        self.upgrade_pool = [
            {"id": "fire_rate", "name": "Rapid Fire", "desc": "+20% Fire Rate", "type": "weapon"},
            {"id": "damage", "name": "Heavy Rounds", "desc": "+25% Damage", "type": "weapon"},
            {"id": "spread", "name": "Match Grade", "desc": "-30% Spread", "type": "weapon"},
            {"id": "reload", "name": "Quick Hands", "desc": "-25% Reload Time", "type": "weapon"},
            {"id": "speed", "name": "Lightweight", "desc": "+15% Movement Speed", "type": "player"},
            {"id": "hp", "name": "Nano Armor", "desc": "+1 Max HP", "type": "player"},
            {"id": "lifesteal", "name": "Siphon", "desc": "Heal 0.2 HP on hit", "type": "special"},
            {"id": "dodge", "name": "Blur", "desc": "10% chance to dodge bullets", "type": "special"}
        ]
        self.active_upgrades = []

    def get_random_upgrades(self, count=3):
        return random.sample(self.upgrade_pool, min(count, len(self.upgrade_pool)))

    def apply_upgrade(self, player, upgrade):
        self.active_upgrades.append(upgrade)
        uid = upgrade["id"]
        
        if uid == "fire_rate":
            player.stats["fire_rate"] *= 0.8
        elif uid == "damage":
            player.stats["damage"] *= 1.25
        elif uid == "spread":
            player.stats["spread"] *= 0.7
        elif uid == "reload":
            player.stats["reload_time"] *= 0.75
        elif uid == "speed":
            player.base_speed *= 1.15
        elif uid == "hp":
            player.hp_max += 1
            player.hp += 1
        # Lifesteal and dodge are handled in the main game loop check
        
    def check_dodge(self):
        dodge_chance = 0
        for u in self.active_upgrades:
            if u["id"] == "dodge":
                dodge_chance += 0.1
        return random.random() < dodge_chance

    def get_lifesteal(self):
        lifesteal = 0
        for u in self.active_upgrades:
            if u["id"] == "lifesteal":
                lifesteal += 0.2
        return lifesteal
