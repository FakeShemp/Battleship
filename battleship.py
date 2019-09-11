# TODO - Create phase one: place ships
# TODO - Click on block and register it
# TODO - Check if hit/miss
# TODO - Check that ships aren't overlapping
# TODO
# TODO - Two players
# TODO - Add text
# TODO - Make things better looking

import pygame

colors = {"red": (255, 0, 0), "green": (0, 255, 0), "blue": (0, 0, 255), "black": (0, 0, 0), "white": (255, 255, 255)}
screen_height = 768
screen_width = 1024
fps = 30
game_phase = 0
current_player = 0


class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Button:
    def __init__(self, width, height, pos: Pos = Pos(0, 0), color=(0, 0, 0), click_action=None, text: str = None,
                 text_color=None,
                 font: str = None,
                 font_size: int = None):
        self.height = height
        self.width = width
        self.color = color
        self.text = text
        self.pos = pos
        self.text_color = text_color
        self.font = font
        self.font_size = font_size
        self.click_action = click_action
        self.clicked = False

    def rect(self):
        return pygame.rect.Rect(self.pos.x, self.pos.y, self.width, self.height)

    def draw(self, window):
        pygame.draw.rect(window, self.color, self.rect())

    def click(self, event, kwargs):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.rect().collidepoint(event.pos):
                    self.clicked = True
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.clicked:
                    if self.rect().collidepoint(event.pos):
                        global game_phase
                        self.clicked = False
                        self.click_action(kwargs)


class Grid:
    def __init__(self, bg_color=(0, 0, 0), line_color=(255, 255, 255), columns: int = 1, rows: int = 1, block_size=10,
                 screen_pos: Pos = Pos(0, 0), line_width=1):
        self.bg_color = bg_color
        self.line_color = line_color
        self.columns = columns
        self.rows = rows
        self.block_size = block_size
        self.screen_pos = screen_pos
        self.line_width = line_width
        self.blocks = self.__calc_blocks()

    def line_area(self) -> pygame.rect.Rect:
        return pygame.rect.Rect(self.screen_pos.x - self.line_width,
                                self.screen_pos.y - self.line_width,
                                self.width(),
                                self.height())

    def width(self):
        return (self.block_size + self.line_width) * self.columns + self.line_width

    def height(self):
        return (self.block_size + self.line_width) * self.rows + self.line_width

    def __calc_blocks(self):
        blocks = []
        number = "1"
        letter = "A"
        for row in range(self.rows):
            number = str(row + 1)
            for col in range(self.columns):
                letter = chr(col + 65)  # ASCII
                rect = pygame.rect.Rect(self.screen_pos.x + row * (self.block_size + self.line_width),
                                        self.screen_pos.y + col * (self.block_size + self.line_width),
                                        self.block_size, self.block_size)
                blocks.append({"rect": rect, "human_name": str(letter + number), "color": self.bg_color,
                               "button": Button(rect.width, rect.height,
                                                pos=Pos(self.screen_pos.x + row * (self.block_size + self.line_width),
                                                        self.screen_pos.y + col * (self.block_size + self.line_width)),
                                                click_action=guess_block)})
        return blocks

    def draw(self, window):
        pygame.draw.rect(window, self.line_color, self.line_area())

        for block in self.blocks:
            pygame.draw.rect(window, block["color"], block["rect"])


class Ship:
    def __init__(self, color=(0, 0, 0), name: str = None, size: int = 1, position: Pos = Pos(0, 0)):
        self.color = color
        self.size = size
        self.vertical = False
        self.type = name
        self.position = position

    def rect(self, grid: Grid):
        if not self.vertical:
            return pygame.rect.Rect(self.position.x, self.position.y,
                                    (grid.block_size + grid.line_width) * self.size - grid.line_width, grid.block_size)
        else:
            return pygame.rect.Rect(self.position.x, self.position.y,
                                    grid.block_size, (grid.block_size + grid.line_width) * self.size - grid.line_width)

    def rotate(self):
        self.vertical = not self.vertical

    def draw(self, window, grid):
        pygame.draw.rect(window, self.color, self.rect(grid))


class Player:
    def __init__(self, guess_grid: Grid, ship_grid: Grid):
        self.name = None
        self.grid_player = guess_grid
        self.grid_enemy = ship_grid
        self.ships = [Ship(colors.get("blue"), "carrier", 5, Pos(600, 100)),
                      Ship(colors.get("blue"), "battleship", 4, Pos(600, 150)),
                      Ship(colors.get("blue"), "destroyer", 3, Pos(600, 200)),
                      Ship(colors.get("blue"), "submarine", 3, Pos(600, 250)),
                      Ship(colors.get("blue"), "patrol_boat", 2, Pos(600, 300))]
        self.ship_positions = None
        self.guesses = []
        self.hits = []


class Text:
    def __init__(self, color, font, pos: Pos, text: str):
        self.color = color
        self.font = font
        self.pos = pos
        self.text = text
        self.surface = self.render()
        self.is_dirty = False

    def render(self):
        return self.font.render(self.text, True, self.color)

    def draw(self, window):
        window.blit(self.surface, (self.pos.x, self.pos.y))


def place_ships(event, ships, grid_ship, dragging, offset: Pos):
    changed_offset = offset
    ship_dragging = dragging
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
            for ship in ships:
                if ship.rect(grid_ship).collidepoint(event.pos):
                    ship_dragging = ship
                    mouse_x, mouse_y = event.pos
                    changed_offset = Pos(ship.position.x - mouse_x, ship.position.y - mouse_y)
        if event.button == 3:
            for ship in ships:
                if ship.rect(grid_ship).collidepoint(event.pos):
                    ship.rotate()

    elif event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1:
            if ship_dragging:
                if grid_ship.line_area().colliderect(ship_dragging.rect(grid_ship)):
                    ship_dragging.position.x = grid_ship.screen_pos.x + (round(
                        ship_dragging.position.x / (grid_ship.block_size + grid_ship.line_width))) * (
                                                       grid_ship.block_size + grid_ship.line_width)
                    ship_dragging.position.y = grid_ship.screen_pos.y + (round(
                        ship_dragging.position.y / (grid_ship.block_size + grid_ship.line_width))) * (
                                                       grid_ship.block_size + grid_ship.line_width)
                ship_dragging = False

    elif event.type == pygame.MOUSEMOTION:
        if ship_dragging:
            mouse_x, mouse_y = event.pos
            ship_dragging.position.x = mouse_x + changed_offset.x
            ship_dragging.position.y = mouse_y + changed_offset.y

    return ship_dragging, changed_offset


def ok_button_clicked(player: Player):
    global game_phase
    positions = calc_ship_positions(player)
    if positions:
        player.ship_positions = positions
        game_phase = game_phase + 1
        print("Game Phase: " + str(game_phase + 1))
    else:
        print("Ships not placed correctly")


def calc_ship_positions(player: Player):
    positions = []
    #  Check that ALL ships are on playing field
    for ship in player.ships:
        if not player.grid_player.line_area().contains(ship.rect(player.grid_player)):
            return False
    #  Calculate their filled positions
    for ship in player.ships:
        for block in player.grid_player.blocks:
            if block["rect"].colliderect(ship.rect(player.grid_player)):
                positions.append(block)
    return positions


def guess_block(kwargs):
    player, enemy, block = kwargs
    if block in player.guesses:
        return False
    player.guesses.append(block)
    # Using human_name for code readability, it's fast enough for this purpose
    for pos in enemy.ship_positions:
        if block["human_name"] == pos["human_name"]:
            block["color"] = colors.get("red")
            enemy.hits.append(pos)
            change_player()
            return block
    block["color"] = colors.get("black")
    change_player()
    return True


def change_player():
    global current_player
    if current_player == 1:
        current_player = 0
    else:
        current_player = 1


def check_if_win(players: [Player]):
    if len(players[0].hits) == 17:
        return 2
    elif len(players[1].hits) == 17:
        return 1
    else:
        return False


def main():
    global game_phase

    pygame.init()

    pygame.display.set_caption("Battleship")

    screen = pygame.display.set_mode((screen_width, screen_height))

    players = [Player(Grid(colors.get("white"), colors.get("black"), 10, 10, round(screen_width / 50), Pos(0, 10), 1),
                      Grid(colors.get("green"), colors.get("black"), 10, 10, round(screen_width / 40), Pos(0, 320),
                           1)),
               Player(Grid(colors.get("white"), colors.get("black"), 10, 10, round(screen_width / 50),
                           Pos(0, 10), 1),
                      Grid(colors.get("green"), colors.get("black"), 10, 10, round(screen_width / 40),
                           Pos(0, 320), 1))]

    clock = pygame.time.Clock()

    default_font = pygame.font.SysFont('Comic Sans MS', 30)  # Best font :)
    p1text = Text(colors.get("black"), default_font, Pos(10, 275), "Player 1")
    p2text = Text(colors.get("black"), default_font, Pos(10, 275), "Player 2")

    running = True
    offset = Pos(0, 0)
    game_ended = False
    ship_dragging = False
    ok_button = Button(100, 30, Pos(screen_width / 2 + 100 / 2, screen_height - 30 - 10), colors.get("green"),
                       ok_button_clicked)

    while running:
        screen.fill(colors.get("white"))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_phase == 0:
                # Place ships Player 1
                ship_dragging, offset = place_ships(event, players[0].ships, players[0].grid_player, ship_dragging,
                                                    offset)
                ok_button.click(event, players[0])
            elif game_phase == 1:
                # Place ships Player 2
                ship_dragging, offset = place_ships(event, players[1].ships, players[1].grid_player, ship_dragging,
                                                    offset)
                ok_button.click(event, players[1])
            elif game_phase == 2:
                if not game_ended:
                    if current_player == 0:
                        for block in players[0].grid_enemy.blocks:
                            block["button"].click(event, (players[0], players[1], block))
                    else:
                        for block in players[1].grid_enemy.blocks:
                            block["button"].click(event, (players[1], players[0], block))
                    game_ended = check_if_win(players)

        if game_phase == 0:
            players[0].grid_player.draw(screen)
            players[0].grid_enemy.draw(screen)
            ok_button.draw(screen)
            for ship in players[0].ships:
                ship.draw(screen, players[0].grid_player)
            p1text.draw(screen)
        elif game_phase == 1:
            players[1].grid_player.draw(screen)
            players[1].grid_enemy.draw(screen)
            ok_button.draw(screen)
            for ship in players[1].ships:
                ship.draw(screen, players[1].grid_player)
            p2text.draw(screen)
        elif game_phase == 2:
            if not game_ended:
                if current_player == 0:
                    players[0].grid_player.draw(screen)
                    players[0].grid_enemy.draw(screen)
                    for ship in players[0].ships:
                        ship.draw(screen, players[0].grid_player)
                    for hit in players[0].hits:
                        pygame.draw.rect(screen, colors.get("red"), hit["rect"])
                    p1text.draw(screen)
                else:
                    players[1].grid_player.draw(screen)
                    players[1].grid_enemy.draw(screen)
                    for ship in players[1].ships:
                        ship.draw(screen, players[1].grid_player)
                        for hit in players[1].hits:
                            pygame.draw.rect(screen, colors.get("red"), hit["rect"])
                    p2text.draw(screen)
            else:
                game_over = Text(colors.get("black"), default_font, Pos(screen_width / 2, screen_height / 2), str("Player " + str(game_ended) + " wins!"))
                game_over.draw()

        pygame.display.flip()

        clock.tick(fps)


if __name__ == "__main__":
    main()
