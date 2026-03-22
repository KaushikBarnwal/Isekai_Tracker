
EXP_PER_STEP = 0.1 # 10 steps = 1 EXP
BASE_XP_REQ = 100
LEVEL_EXPONENT = 1.3

WORLD_REGIONS = {
    # --- Early Game: The Terrestrial Realm ---
    1: {"location": "Humble Village of Starting", "region": "Greenleaf Kingdom", "env_desc": "quaint cottages, dirt paths, and sunflower fields"},
    10: {"location": "The Whispering Woods", "region": "The Shadow Border", "env_desc": "ancient glowing trees, thick mist, and bioluminescent moss"},
    20: {"location": "Ironforge Peaks", "region": "Dwarven Highlands", "env_desc": "snow-capped mountains, steam-powered elevators, and jagged cliffs"},
    # --- Mid Game: Elemental and Ancient Lands ---
    35: {"location": "Oasis of Echoes", "region": "The Golden Sea", "env_desc": "shifting sand dunes, hidden palm groves, and sandstone ruins under a dual sun"},
    50: {"location": "Azure Harbor", "region": "Sapphire Archipelago", "env_desc": "tropical islands, white sand, coral reefs, and pirate shipwrecks"},
    65: {"location": "Glimmering Hollows", "region": "The Deep-Core Labyrinth", "env_desc": "vast underground caverns, giant crystal clusters, and subterranean rivers of liquid mana"},
    # --- Late Game: High Fantasy and Magitech ---
    80: {"location": "Floating Bastion of Aeris", "region": "The Sky-High Dominion", "env_desc": "marble castles floating on clouds, waterfalls falling into the sky, and airship docks"},
    100: {"location": "Imperial Citadel of Valoria", "region": "Central Hegemony", "env_desc": "massive golden spires, bustling cobblestone plazas, and a giant mechanical clocktower"},
    120: {"location": "The Obsidian Rim", "region": "Magma Sanctum", "env_desc": "rivers of lava, black basalt towers, and soot-filled air with glowing embers"},
    # --- End Game: The Astral and Celestial Planes ---
    140: {"location": "Clockwork Arcane Labs", "region": "Technomancy Peaks", "env_desc": "brass gears integrated into stone, lightning capacitors, and floating holographic runes"},
    160: {"location": "Glacial Spire of Silence", "region": "The Permafrost Waste", "env_desc": "endless blizzards, towers made of unbreakable blue ice, and frozen dragons in the sky"},
    180: {"location": "Starlight Terrace", "region": "The Celestial Weave", "env_desc": "platforms made of pure light, nebulae visible in the daytime, and bridges of stardust"},
    # --- Final Tier: The Absolute Horizon ---
    200: {"location": "The Absolute Horizon", "region": "The Void's Edge", "env_desc": "shattered reality fragments, a white void background, and a single golden throne atop a mountain of glass"},
}

REGION_ENEMIES = {
    # --- Early Game: The Terrestrial Realm ---
    "Greenleaf Kingdom": ["Green Slimes", "Horned Rabbits", "Forest Goblins", "Bandit Scavengers"],
    "The Shadow Border": ["Shadow Wolves", "Mist Wraiths", "Corrupted Treants", "Venomous Arachnids"],
    "Dwarven Highlands": ["Stone Golems", "Frost Wyverns", "Rogue Automatons", "Mountain Trolls"],
    # --- Mid Game: Elemental and Ancient Lands ---
    "The Golden Sea": ["Dune Basilisks", "Sandstorm Elementals", "Cursed Tomb Guards", "Mirage Assassins"],
    "Sapphire Archipelago": ["Pirate Specters", "Coral Golems", "Siren Illusionists", "Deep Sea Leviathans"],
    "The Deep-Core Labyrinth": ["Mana-Crazed Elementals", "Crystal Crawlers", "Subterranean Behemoths", "Blind Cave Wyrms"],
    # --- Late Game: High Fantasy and Magitech ---
    "The Sky-High Dominion": ["Zephyr Knights", "Storm Griffons", "Cloud Serpents", "Valkyrie Sentinels"],
    "Central Hegemony": ["Imperial Inquisitors", "Clockwork Titan-Guards", "Elite Spellblades", "Mechanized Gargoyles"],
    "Magma Sanctum": ["Ash Demons", "Obsidian Colossi", "Lava Drakes", "Pyroclastic Elementals"],
    # --- End Game: The Astral and Celestial Planes ---
    "Technomancy Peaks": ["Lightning Revenants", "Rogue AI Constructs", "Brass Minotaurs", "Arcane Amalgamations"],
    "The Permafrost Waste": ["Frost-Lich Sorcerers", "Rimeblood Behemoths", "Shattered Ice Golems", "Undead Glacier Dragons"],
    "The Celestial Weave": ["Astral Sentinels", "Nebula Weavers", "Star-Devourer Entities", "Cosmic Seraphim"],
    # --- Final Tier: The Absolute Horizon ---
    "The Void's Edge": ["Echoes of the First God", "Reality-Shattering Phantoms", "Reflections of the Fallen Hero", "The Void Sovereign"],
}

