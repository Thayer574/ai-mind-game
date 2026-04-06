import random
from weapons import PERKS_BY_RARITY

class UpgradeManager:
    def __init__(self):
        self.currency = 0
        self.perks_owned = []
        self.rarity_weights = {
            "common": 0.70,
            "rare": 0.20,
            "epic": 0.07,
            "legendary": 0.03
        }

    def get_random_perks(self, count=3):
        selected_perks = []
        for _ in range(count):
            r = random.random()
            if r < self.rarity_weights["legendary"]:
                rarity = "legendary"
            elif r < self.rarity_weights["legendary"] + self.rarity_weights["epic"]:
                rarity = "epic"
            elif r < self.rarity_weights["legendary"] + self.rarity_weights["epic"] + self.rarity_weights["rare"]:
                rarity = "rare"
            else:
                rarity = "common"
            
            available = [p for p in PERKS_BY_RARITY[rarity] if p not in selected_perks]
            if not available:
                available = [p for p in PERKS_BY_RARITY["common"] if p not in selected_perks]
                
            if available:
                selected_perks.append(random.choice(available))
        return selected_perks

    def apply_perk(self, player, perk):
        self.perks_owned.append(perk["id"])
        # Immediate stat changes
        if perk["id"] == "quick_reload":
            for slot in ["primary", "secondary"]:
                player.weapons[slot]["stats"]["reload_time"] *= 0.75
        elif perk["id"] == "scope":
            for slot in ["primary", "secondary"]:
                player.weapons[slot]["stats"]["range"] *= 1.5
        elif perk["id"] == "switch":
            for slot in ["primary", "secondary"]:
                player.weapons[slot]["stats"]["is_auto"] = True
                player.weapons[slot]["stats"]["fire_rate"] *= 0.8
        elif perk["id"] == "akimbo":
            player.weapons["primary"]["stats"]["spread"] *= 1.5

    def has_perk(self, perk_id):
        return perk_id in self.perks_owned

    def get_lifesteal(self):
        # Even if lifesteal isn't a current perk, we provide this to avoid AttributeError
        return 0

    def get_damage_reduction(self):
        return 0.15 if self.has_perk("iron_will") else 0.0

    def check_bandage(self, player):
        if self.has_perk("bandage") and player.hp < player.hp_max * 0.25:
            player.hp = player.hp_max * 0.6
            return True
        return False

    def check_dodge(self):
        # Provided for backward compatibility
        return False

    def check_scavenger(self, player):
        # Provided for backward compatibility
        pass
