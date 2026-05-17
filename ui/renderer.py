import pygame


class BoardRenderer:
    def __init__(self, x=24, y=34, cell_size=26, cols=10, rows=20):
        self.x = x
        self.y = y
        self.cell_size = cell_size
        self.cols = cols
        self.rows = rows

        self.panel_height = 690

        self.panel_color = (28, 33, 44)
        self.panel_border_color = (90, 112, 148)

        self.grid_bg_color = (39, 45, 58)
        self.grid_line_color = (76, 91, 116)
        self.empty_cell_color = (43, 49, 63)

        self.tetromino_colors = {
            1: (245, 208, 66),
            2: (110, 203, 244),
            3: (178, 119, 255),
            4: (95, 220, 130),
            5: (245, 95, 95),
            6: (95, 140, 245),
            7: (245, 160, 75),
        }

        self.title_color = (248, 250, 252)
        self.font_title = pygame.font.SysFont("arial", 24, bold=True)

    def get_cell_color(self, value):
        if not value:
            return self.empty_cell_color

        return self.tetromino_colors.get(value, (110, 203, 244))

    def draw(self, surface, board):
        grid_width = self.cols * self.cell_size
        grid_height = self.rows * self.cell_size

        panel_width = grid_width + 32
        panel_height = self.panel_height

        panel_rect = pygame.Rect(self.x, self.y, panel_width, panel_height)

        pygame.draw.rect(surface, self.panel_color, panel_rect, border_radius=18)
        pygame.draw.rect(surface, self.panel_border_color, panel_rect, 2, border_radius=18)

        title_x = self.x + 14
        title_y = self.y + 20

        surface.blit(
            self.font_title.render("Board", True, self.title_color),
            (title_x, title_y),
        )

        grid_x = self.x + 14
        grid_y = self.y + 86

        grid_rect = pygame.Rect(grid_x, grid_y, grid_width, grid_height)

        pygame.draw.rect(surface, self.grid_bg_color, grid_rect)
        pygame.draw.rect(surface, self.panel_border_color, grid_rect, 1)

        for row in range(self.rows):
            for col in range(self.cols):
                value = 0

                if row < len(board) and col < len(board[row]):
                    value = board[row][col]

                cell_rect = pygame.Rect(
                    grid_x + col * self.cell_size,
                    grid_y + row * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                )

                pygame.draw.rect(surface, self.get_cell_color(value), cell_rect)
                pygame.draw.rect(surface, self.grid_line_color, cell_rect, 1)