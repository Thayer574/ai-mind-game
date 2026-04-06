# DEFINITIVE TACTICAL REFINEMENT: Slower Movement, Lethal Combat, Specialized Roles
# Armor and Speed Stats (Scaled for smaller characters and larger maps)
ARMOR_STATS = {
    "none": {"hp": 10, "speed": 4.0, "color": (200, 200, 200)},
    "light": {"hp": 25, "speed": 3.4, "color": (150, 255, 150)},
    "medium": {"hp": 50, "speed": 2.8, "color": (150, 150, 255)},
    "heavy": {"hp": 100, "speed": 2.2, "color": (255, 150, 150)}
}

# Weapon Stats (Shared by Player and AI)
# Speed penalties are more impactful to force tactical positioning
WEAPON_STATS = {
    "shotgun": {
        "fire_rate": 850, "spread": 18, "damage": 12, "range": 250, "pellets": 6, "ammo": 5,
        "reload_time": 1800, "speed_penalty": 0.85, "is_auto": False, "bullet_speed": 18
    },
    "sniper": {
        "fire_rate": 1800, "spread": 0, "damage": 100, "range": 1500, "pellets": 1, "ammo": 1,
        "reload_time": 2500, "speed_penalty": 0.6, "is_auto": False, "bullet_speed": 45
    },
    "dmr": {
        # FIXED: Reduced damage to 35 (from 100) to prevent one-tapping.
        # Now requires 2-3 shots for most targets.
        "fire_rate": 450, "spread": 1, "damage": 35, "range": 1000, "pellets": 1, "ammo": 10,
        "reload_time": 1500, "speed_penalty": 0.75, "is_auto": False, "bullet_speed": 30
    },
    "ar": {
        "fire_rate": 140, "spread": 4, "damage": 15, "range": 700, "pellets": 1, "ammo": 30,
        "reload_time": 1600, "speed_penalty": 0.75, "is_auto": True, "bullet_speed": 22
    },
    "smg": {
        "fire_rate": 75, "spread": 10, "damage": 8, "range": 400, "pellets": 1, "ammo": 40,
        "reload_time": 1300, "speed_penalty": 0.95, "is_auto": True, "bullet_speed": 20
    },
    "lmg": {
        "fire_rate": 110, "spread": 7, "damage": 10, "range": 800, "pellets": 1, "ammo": 100,
        "reload_time": 3500, "speed_penalty": 0.5, "is_auto": True, "bullet_speed": 22
    },
    "pistol": {
        "fire_rate": 350, "spread": 2, "damage": 12, "range": 600, "pellets": 1, "ammo": 12,
        "reload_time": 1100, "speed_penalty": 1.0, "is_auto": False, "bullet_speed": 20
    },
    "auto_pistol": {
        "fire_rate": 70, "spread": 14, "damage": 6, "range": 250, "pellets": 1, "ammo": 20,
        "reload_time": 1200, "speed_penalty": 1.0, "is_auto": True, "bullet_speed": 18
    }
}

GRENADE_STATS = {
    "frag": {"damage": 80, "radius": 50, "fuse": 2000, "color": (100, 100, 100)},
    "flash": {"damage": 0, "radius": 50, "fuse": 1500, "blind_duration": 3500, "color": (255, 255, 200)}
}

# Perk Rarity Definitions (Kept for future use, though disabled currently)
RARITY_COLORS = {
    "common": (150, 150, 150), "rare": (0, 120, 255), "epic": (180, 0, 255), "legendary": (255, 180, 0)
}

PERKS_BY_RARITY = {
    "common": [
        {"id": "quick_reload", "name": "Quick Reload", "desc": "-25% Reload Time", "rarity": "common"},
        {"id": "iron_will", "name": "Iron Will", "desc": "-15% Damage Taken", "rarity": "common"},
        {"id": "adrenaline", "name": "Adrenaline", "desc": "Taking damage boosts speed for 2s", "rarity": "common"}
    ],
    "rare": [
        {"id": "special_ops", "name": "Special Ops", "desc": "Can use pistol while primary reloads", "rarity": "rare"},
        {"id": "throwable_recharge", "name": "Recharge", "desc": "Regen grenades every 10s", "rarity": "rare"},
        {"id": "bandage", "name": "Emergency Bandage", "desc": "Heal to 60% if under 25% HP", "rarity": "rare"}
    ],
    "epic": [
        {"id": "scope", "name": "Enhanced Scope", "desc": "Greatly increased range (+50%)", "rarity": "epic"},
        {"id": "bleeding", "name": "Bleeding Rounds", "desc": "Hits deal 1% HP damage per second", "rarity": "epic"}
    ],
    "legendary": [
        {"id": "akimbo", "name": "Akimbo", "desc": "Dual wield primary (2x shots, -50% accuracy)", "rarity": "legendary"},
        {"id": "switch", "name": "The Switch", "desc": "ALL weapons full auto & +25% fire rate", "rarity": "legendary"}
    ]
}
