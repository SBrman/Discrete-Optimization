class ArmorPiece:
    
    def __init__(self, name, type, weight, physical, strike, slash, pierce, magic, 
                 fire, lightning, holy, immunity, robustness, focus, vitality, poise):

        self.name: str = name
        self.type: str = type
        self.weight: float = weight
        self.physical: float = physical
        self.strike: float = strike
        self.slash: float = slash
        self.pierce: float = pierce
        self.magic: float = magic
        self.fire: float = fire 
        self.lightning: float = lightning
        self.holy: float = holy 
        self.immunity: int = immunity
        self.robustness: int = robustness
        self.focus: int = focus
        self.vitality: int = vitality
        self.poise: int = poise

        # For storing solver variables
        self.var = None

    def __hash__(self):
        return hash(self.name)
    
    