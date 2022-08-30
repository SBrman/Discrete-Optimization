#! python3

from armor import ArmorPiece

ATTRIBUTES = {'physical', 'strike', 'slash', 'pierce', 'magic', 'fire', 
              'lightning', 'holy', 'immunity', 'robustness', 'focus', 'poise'}

class Pieces:
    def __init__(self):
        self.head = set()
        self.hands = set()
        self.chest = set()
        self.legs = set()
        
        self.max_attributes = {p: 0 for p in ATTRIBUTES}
        self._read_data_flag = 0
        
        self.read_data()

    def correct_cast(self, attr):
        """Returns the attribute in the correct format."""
        attr = attr.strip()
        if attr != '':
            return float(attr) if '.' in attr else int(attr)
        else:
            return 0

    def normalize_attribute_values(self, final=False):
        """
        Divides the attribute value for each class of armor by 
        the maximum attribute value of that class.
        """
        assert self._read_data_flag, "Should not be called before the entire dataset is read."
        
        if final: final_normalizer = max(self.max_attributes[attr] for attr in ATTRIBUTES)
            
        for armor in [self.head, self.hands, self.chest, self.legs]:
            for armor_piece in armor:
                for attribute in ATTRIBUTES:
                    normalizer = self.max_attributes[attribute] if not final else final_normalizer

                    if not hasattr(armor_piece, f'_attribute'):
                        # Keeping the originals attribute values
                        attr_value = getattr(armor_piece, attribute)
                        setattr(armor_piece, f'_{attribute}', attr_value)

                    normalized_value = attr_value / normalizer
                    setattr(armor_piece, attribute, normalized_value)
                    

    def read_data(self, data_file='data.csv'):
        """Reads the data and creates the armor pieces."""

        with open(data_file) as file:
            for i, line in enumerate(file.readlines()):
                if not i: 
                    continue

                _, name, type, *attrs = line.split(',')
                attrs = [self.correct_cast(attr) for attr in attrs]
                piece = ArmorPiece(name, type, *attrs)
                
                for attribute in ATTRIBUTES:
                    piece_attr = getattr(piece, attribute)
                    if piece_attr > self.max_attributes[attribute]:
                        self.max_attributes[attribute] = piece_attr

                self.__getattribute__(piece.type).add(piece)
                
        self._read_data_flag = 1
        self.normalize_attribute_values()
        self.normalize_attribute_values(True)
        
    
PIECES = Pieces()

if __name__ == "__main__":
    for t in PIECES.head:
        print(t.name)
        for attr in ATTRIBUTES:
            print(getattr(t, attr))
