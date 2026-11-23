"""
vocabulary.py
-------------
Every word the parser understands lives HERE, not in the parsing logic.
To teach the parser something new, add a line in this file and nothing else.

Format:  "canonical value": ["extra alias", "another alias", ...]

 * The canonical value is what ends up in the report.
 * The canonical value itself is always accepted too (you don't repeat it).
 * Aliases are other ways the driver might say it, OR ways Whisper might
   mis-write it (e.g. "kea" for Kia). Grow these lists from your REAL tests.
 * Write aliases in plain lowercase; accents and punctuation are ignored.
"""

# ----------------------------------------------------------------------------
# Colors  (and shades that can appear right before a color: "dark blue")
# ----------------------------------------------------------------------------
COLORS = {
    "white": [],
    "black": [],
    "blue": ["navy"],
    "red": ["maroon", "burgundy", "bordeaux"],
    "grey": ["gray"],
    "silver": [],
    "green": [],
    "yellow": [],
    "orange": [],
    "brown": [],
    "beige": [],
    "gold": [],
    "purple": [],
}

SHADES = {
    "dark": ["deep"],
    "light": ["pale"],
}

# ----------------------------------------------------------------------------
# Makes (brands)
# ----------------------------------------------------------------------------
MAKES = {
    "Toyota": ["toyata"],
    "Kia": ["kea", "kya", "kiya"],
    "Hyundai": ["hundai", "hyundi", "hunday", "hyundae"],
    "Peugeot": ["pejo", "pezho", "pujo", "pugeot", "peugot"],
    "Renault": ["reno", "renaud"],
    "Dacia": [],
    "Volkswagen": ["vw", "volks wagen", "volkswagon"],
    "Seat": [],
    "Fiat": [],
    "Citroen": ["citron"],
    "Ford": [],
    "Opel": [],
    "Skoda": [],
    "Suzuki": [],
    "Nissan": [],
    "Mercedes-Benz": ["mercedes", "benz", "mercedes benz", "merc"],
    "BMW": ["b m w"],
    "Audi": [],
    "Honda": [],
    "Mazda": [],
    "Mitsubishi": [],
    "Chevrolet": ["chevy"],
    "Chery": [],
    "MG": [],
    "Isuzu": [],
}

# ----------------------------------------------------------------------------
# Models:  "Model": ("Make it belongs to", [aliases])
# If the driver only says the model ("Yaris"), the make is filled in for them.
# ----------------------------------------------------------------------------
MODELS = {
    # Toyota
    "Yaris": ("Toyota", ["yarris", "yaros"]),
    "Corolla": ("Toyota", []),
    "Hilux": ("Toyota", ["hi lux"]),
    "Land Cruiser": ("Toyota", ["landcruiser"]),
    "RAV4": ("Toyota", ["rav 4"]),
    "Camry": ("Toyota", []),
    "Auris": ("Toyota", []),
    "Prado": ("Toyota", []),
    # Kia
    "Rio": ("Kia", []),
    "Picanto": ("Kia", []),
    "Sportage": ("Kia", []),
    "Sorento": ("Kia", []),
    "Cerato": ("Kia", []),
    "Stonic": ("Kia", []),
    # Hyundai
    "Accent": ("Hyundai", []),
    "i10": ("Hyundai", ["i 10"]),
    "i20": ("Hyundai", ["i 20"]),
    "i30": ("Hyundai", ["i 30"]),
    "Tucson": ("Hyundai", []),
    "Elantra": ("Hyundai", []),
    "Creta": ("Hyundai", []),
    "Santa Fe": ("Hyundai", ["santafe"]),
    "Kona": ("Hyundai", []),
    # Peugeot
    "208": ("Peugeot", ["two oh eight", "two zero eight"]),
    "308": ("Peugeot", ["three oh eight", "three zero eight"]),
    "301": ("Peugeot", []),
    "206": ("Peugeot", []),
    "207": ("Peugeot", []),
    "2008": ("Peugeot", []),
    "3008": ("Peugeot", []),
    "Partner": ("Peugeot", []),
    # Renault / Dacia
    "Clio": ("Renault", ["cleo"]),
    "Symbol": ("Renault", []),
    "Megane": ("Renault", ["megan"]),
    "Kangoo": ("Renault", []),
    "Captur": ("Renault", []),
    "Twingo": ("Renault", []),
    "Sandero": ("Dacia", []),
    "Logan": ("Dacia", []),
    "Duster": ("Dacia", []),
    "Dokker": ("Dacia", []),
    # Volkswagen / Seat / Skoda
    "Golf": ("Volkswagen", []),
    "Polo": ("Volkswagen", []),
    "Passat": ("Volkswagen", []),
    "Tiguan": ("Volkswagen", []),
    "Caddy": ("Volkswagen", []),
    "Jetta": ("Volkswagen", []),
    "Ibiza": ("Seat", []),
    "Leon": ("Seat", []),
    "Arona": ("Seat", []),
    "Octavia": ("Skoda", []),
    "Fabia": ("Skoda", []),
    # Others
    "Panda": ("Fiat", []),
    "Tipo": ("Fiat", []),
    "Doblo": ("Fiat", []),
    "Punto": ("Fiat", []),
    "C3": ("Citroen", []),
    "C4": ("Citroen", []),
    "Berlingo": ("Citroen", []),
    "Fiesta": ("Ford", []),
    "Focus": ("Ford", []),
    "Ranger": ("Ford", []),
    "Transit": ("Ford", []),
    "Kuga": ("Ford", []),
    "Corsa": ("Opel", []),
    "Astra": ("Opel", []),
    "Mokka": ("Opel", []),
    "Swift": ("Suzuki", []),
    "Alto": ("Suzuki", []),
    "Vitara": ("Suzuki", []),
    "Qashqai": ("Nissan", []),
    "Micra": ("Nissan", []),
    "Juke": ("Nissan", []),
    "Navara": ("Nissan", []),
    "Civic": ("Honda", []),
    "Accord": ("Honda", []),
    "CR-V": ("Honda", ["cr v"]),
    "Tiggo": ("Chery", []),
    "D-Max": ("Isuzu", ["d max"]),
    "L200": ("Mitsubishi", ["l 200"]),
}

# ----------------------------------------------------------------------------
# Vehicle types (what the driver calls the vehicle). YOLO only knows
# car / motorcycle / bus / truck; target_selector.py will map these later.
# ----------------------------------------------------------------------------
VEHICLE_TYPES = {
    "car": ["sedan", "hatchback", "saloon", "coupe", "automobile", "taxi"],
    "suv": ["4x4", "four by four", "crossover", "jeep"],
    "van": ["minivan", "minibus", "mini bus", "louage"],
    "pickup": ["pick up", "pickup truck", "pick up truck"],
    "truck": ["lorry", "trailer", "heavy truck", "dump truck", "semi"],
    "bus": ["coach"],
    "motorcycle": ["motorbike", "motor bike", "scooter", "moped", "motor"],
}

# ----------------------------------------------------------------------------
# Positions. Canonical names use underscores; "left_shoulder" is also accepted
# when spoken as "left shoulder" automatically.
# ----------------------------------------------------------------------------
POSITIONS = {
    "left_shoulder": ["left hand shoulder", "left side shoulder",
                      "shoulder on the left", "shoulder on my left",
                      "left emergency lane"],
    "right_shoulder": ["right hand shoulder", "right side shoulder",
                       "shoulder on the right", "shoulder on my right",
                       "right emergency lane"],
    # side unknown: the driver only said "shoulder"
    "shoulder": ["hard shoulder", "emergency lane", "emergency shoulder",
                 "breakdown lane"],
    "left_lane": ["left hand lane"],
    "right_lane": ["right hand lane"],
    "center_lane": ["middle lane", "centre lane", "central lane"],
    "oncoming": ["opposite lane", "opposite direction"],
    "ahead": ["in front of me", "ahead of me", "in front"],
    "left": ["on the left", "on my left", "to my left", "left side"],
    "right": ["on the right", "on my right", "to my right", "right side"],
}

# ----------------------------------------------------------------------------
# Violation types
# ----------------------------------------------------------------------------
VIOLATIONS = {
    "speeding": ["speed", "overspeeding", "over speeding", "driving too fast",
                 "going too fast", "too fast", "speed limit"],
    "red_light": ["ran a red light", "running a red light", "jumped a red light",
                  "jumped the light", "ran the light", "running the light"],
    "illegal_overtaking": ["overtaking", "overtook", "overtake", "overtaken"],
    "illegal_parking": ["parking", "parked", "double parked", "double parking",
                        "illegally parked"],
    "wrong_way": ["wrong direction", "against traffic"],
    "phone_use": ["texting", "on the phone", "using the phone", "using a phone",
                  "using his phone", "using her phone"],
    "no_seatbelt": ["seatbelt", "seat belt"],
    "tailgating": ["tailgated", "too close"],
    "cutting_off": ["cut me off", "cutting me off", "cut in front"],
    "no_signal": ["without signaling", "without signalling", "no indicator",
                  "without indicator", "without indicating"],
    "shoulder_driving": ["driving on the shoulder", "drove on the shoulder",
                         "driving on the left shoulder",
                         "driving on the right shoulder",
                         "driving on the emergency lane", "using the shoulder"],
}
