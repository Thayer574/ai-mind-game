ARMOR_STATS = {
    "none": {"hp": 1, "speed": 6, "color": (200, 200, 200)},
    "light": {"hp": 2, "speed": 5, "color": (150, 255, 150)},
    "medium": {"hp": 3, "speed": 4, "color": (150, 150, 255)},
    "heavy": {"hp": 4, "speed": 3, "color": (255, 150, 150)}
}

WEAPON_STATS = {
    "shotgun": {
        "fire_rate": 800, # ms between shots
        "spread": 15,    # degrees
        "damage": 1,
        "range": 300,
        "pellets": 6,
        "ammo": 5,
        "reload_time": 1500,
        "speed_penalty": 0.9
    },
    "sniper": {
        "fire_rate": 1500,
        "spread": 0,
        "damage": 4,
        "range": 1200,
        "pellets": 1,
        "ammo": 1,
        "reload_time": 2000,
        "speed_penalty": 0.7
    },
    "dmr": {
        "fire_rate": 400,
        "spread": 1,
        "damage": 2,
        "range": 800,
        "pellets": 1,
        "ammo": 10,
        "reload_time": 1200,
        "speed_penalty": 0.85
    },
    "ar": {
        "fire_rate": 150,
        "spread": 3,
        "damage": 1,
        "range": 600,
        "pellets": 1,
        "ammo": 30,
        "reload_time": 1500,
        "speed_penalty": 0.8
    },
    "smg": {
        "fire_rate": 80,
        "spread": 8,
        "damage": 0.8,
        "range": 400,
        "pellets": 1,
        "ammo": 40,
        "reload_time": 1200,
        "speed_penalty": 1.0
    },
    "lmg": {
        "fire_rate": 120,
        "spread": 6,
        "damage": 1.2,
        "range": 700,
        "pellets": 1,
        "ammo": 100,
        "reload_time": 3000,
        "speed_penalty": 0.6
    },
    "pistol": {
        "fire_rate": 300,
        "spread": 2,
        "damage": 1,
        "range": 500,
        "pellets": 1,
        "ammo": 12,
        "reload_time": 1000,
        "speed_penalty": 1.0
    },
    "auto_pistol": {
        "fire_rate": 100,
        "spread": 10,
        "damage": 0.7,
        "range": 350,
        "pellets": 1,
        "ammo": 20,
        "reload_time": 1000,
        "speed_penalty": 1.0
    }
}
