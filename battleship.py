import pygame

colors = {"red": (255, 0, 0), "green": (0, 255, 0), "blue": (0, 0, 255), "black": (0, 0, 0), "white": (255, 255, 255)}
screen_height = 1024
screen_width = 768
fps = 30


class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Ship:
    def __init__(self, color, name: str, size: int, position: Pos):
        self.color = color
        self.size = size
        self.vertical = False
        self.type = name
        self.position = position


class Grid:
    def __init__(self, bg_color, line_color, columns: int, rows: int, block_size, screen_pos: Pos, line_width):
        self.bg_color = bg_color
        self.line_color = line_color
        self.columns = columns
        self.rows = rows
        self.block_size = block_size
        self.screen_pos = screen_pos
        self.line_width = line_width

    def line_area(self) -> pygame.rect.Rect:
        return pygame.rect.Rect(self.screen_pos.x - self.line_width,
                                self.screen_pos.y - self.line_width,
                                (self.block_size + self.line_width) * self.columns + self.line_width,
                                (self.block_size + self.line_width) * self.rows + self.line_width)


def main():
    pygame.init()
    pygame.display.set_caption("Battleship")

    screen = pygame.display.set_mode((screen_height, screen_width))

    grid_ship = Grid(colors.get("green"), colors.get("black"), 10, 10, round(screen_width / 30), Pos(0, 0), 1)
    grid_enemy = Grid(colors.get("white"), colors.get("black"), 10, 10, round(screen_width / 20), Pos(300, 300), 1)

    ships = [Ship(colors.get("blue"), "carrier", 5, Pos(600, 100)),
             Ship(colors.get("blue"), "battleship", 4, Pos(600, 150)),
             Ship(colors.get("blue"), "destroyer", 3, Pos(600, 200)),
             Ship(colors.get("blue"), "submarine", 3, Pos(600, 250)),
             Ship(colors.get("blue"), "patrol_boat", 2, Pos(600, 300))]

    ships = {"carrier": ship_carrier(grid_ship.block_size, (600, 100), grid_ship.line_width),
             "battleship": ship_battleship(grid_ship.block_size, (600, 125), grid_ship.line_width),
             "destroyer": ship_destroyer(grid_ship.block_size, (600, 150), grid_ship.line_width),
             "submarine": ship_submarine(grid_ship.block_size, (600, 175), grid_ship.line_width),
             "patrol_boat": ship_patrol_boat(grid_ship.block_size, (600, 200), grid_ship.line_width)}

    ship_dragging = False

    clock = pygame.time.Clock()

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for ship in ships:
                        if ships[ship].collidepoint(event.pos):
                            ship_dragging = ship
                            mouse_x, mouse_y = event.pos
                            offset_x = ships[ship].x - mouse_x
                            offset_y = ships[ship].y - mouse_y
                if event.button == 3:
                    for ship in ships:
                        if ships[ship].collidepoint(event.pos):
                            temp = ships[ship].height
                            ships[ship].height = ships[ship].width
                            ships[ship].width = temp

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if ship_dragging:
                        if grid_ship.line_area().colliderect(ships[ship_dragging]):
                            ships[ship_dragging].x = (round(
                                ships[ship_dragging].x / (grid_ship.block_size + grid_ship.line_width))) * (
                                                             grid_ship.block_size + grid_ship.line_width)
                            ships[ship_dragging].y = (round(
                                ships[ship_dragging].y / (grid_ship.block_size + grid_ship.line_width))) * (
                                                             grid_ship.block_size + grid_ship.line_width)
                        ship_dragging = False

            elif event.type == pygame.MOUSEMOTION:
                if ship_dragging:
                    mouse_x, mouse_y = event.pos
                    ships[ship_dragging].x = mouse_x + offset_x
                    ships[ship_dragging].y = mouse_y + offset_y

        screen.fill(colors.get("white"))

        draw_grid(screen, grid_ship)
        draw_grid(screen, grid_enemy)

        for ship in ships.values():
            pygame.draw.rect(screen, colors.get("red"), ship)

        pygame.display.flip()

        clock.tick(fps)


def ship_carrier(size, pos, spacing):
    return pygame.rect.Rect(pos[0], pos[1], (size + spacing) * 5 - spacing, size)


def ship_battleship(size, pos, spacing):
    return pygame.rect.Rect(pos[0], pos[1], (size + spacing) * 4 - spacing, size)


def ship_destroyer(size, pos, spacing):
    return pygame.rect.Rect(pos[0], pos[1], (size + spacing) * 3 - spacing, size)


def ship_submarine(size, pos, spacing):
    return pygame.rect.Rect(pos[0], pos[1], (size + spacing) * 3 - spacing, size)


def ship_patrol_boat(size, pos, spacing):
    return pygame.rect.Rect(pos[0], pos[1], (size + spacing) * 2 - spacing, size)


def draw_grid(win, grid: Grid):
    pygame.draw.rect(win, grid.line_color, grid.line_area())

    for row in range(grid.rows):
        for col in range(grid.columns):
            rect = pygame.rect.Rect(grid.screen_pos.x + row * (grid.block_size + grid.line_width),
                                    grid.screen_pos.y + col * (grid.block_size + grid.line_width),
                                    grid.block_size, grid.block_size)
            pygame.draw.rect(win, grid.bg_color, rect)


if __name__ == "__main__":
    main()
