class Piece:
    SHAPES = {
        "I": [
            [(0, 1), (1, 1), (2, 1), (3, 1)],
            [(2, 0), (2, 1), (2, 2), (2, 3)],
        ],
        "O": [
            [(0, 0), (1, 0), (0, 1), (1, 1)],
        ],
        "T": [
            [(1, 0), (0, 1), (1, 1), (2, 1)],
            [(1, 0), (1, 1), (2, 1), (1, 2)],
            [(0, 1), (1, 1), (2, 1), (1, 2)],
            [(1, 0), (0, 1), (1, 1), (1, 2)],
        ],
        "S": [
            [(1, 0), (2, 0), (0, 1), (1, 1)],
            [(1, 0), (1, 1), (2, 1), (2, 2)],
        ],
        "Z": [
            [(0, 0), (1, 0), (1, 1), (2, 1)],
            [(2, 0), (1, 1), (2, 1), (1, 2)],
        ],
        "J": [
            [(0, 0), (0, 1), (1, 1), (2, 1)],
            [(1, 0), (2, 0), (1, 1), (1, 2)],
            [(0, 1), (1, 1), (2, 1), (2, 2)],
            [(1, 0), (1, 1), (0, 2), (1, 2)],
        ],
        "L": [
            [(2, 0), (0, 1), (1, 1), (2, 1)],
            [(1, 0), (1, 1), (1, 2), (2, 2)],
            [(0, 1), (1, 1), (2, 1), (0, 2)],
            [(0, 0), (1, 0), (1, 1), (1, 2)],
        ],
    }

    CELL_VALUES = {
        "O": 1,
        "I": 2,
        "T": 3,
        "S": 4,
        "Z": 5,
        "J": 6,
        "L": 7,
    }

    def __init__(self, name, rotation_index=0):
        if name not in self.SHAPES:
            raise ValueError(f"Unknown piece: {name}")

        self.name = name
        self.rotation_index = rotation_index % len(self.SHAPES[name])

    def get_blocks(self):
        return self.SHAPES[self.name][self.rotation_index]

    def get_rotated(self, rotation_offset=1):
        return Piece(
            self.name,
            self.rotation_index + rotation_offset,
        )

    def get_rotation_count(self):
        return len(self.SHAPES[self.name])

    def get_cell_value(self):
        return self.CELL_VALUES[self.name]