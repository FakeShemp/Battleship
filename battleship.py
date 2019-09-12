# TODO - Check that ships aren't overlapping when okay is pressed
# TODO - Actually add text to okay button so you know wth it does
# TODO - Replace hard-coded phases with self-stated entities
# TODO - Make a real resolution system instead of hard-coded percentages
# TODO - Make things better-looking
# TODO - Make the grid system matrix-based instead of collision-based

import pygame

# Some globals instead of config since it's a small game
colors = {"red": (255, 0, 0), "green": (0, 255, 0), "blue": (0, 0, 255), "black": (0, 0, 0), "white": (255, 255, 255)}
screen_width = 720
screen_height = 540
fps = 30
game_phase = 0
current_player = 0


class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Button:
    #  Class for a clickable button
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
    #  Class that handles functionality of a grid
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

    # Area within outer lines, i.e. the area of the playing field
    def line_area(self) -> pygame.rect.Rect:
        return pygame.rect.Rect(self.screen_pos.x - self.line_width,
                                self.screen_pos.y - self.line_width,
                                self.width(),
                                self.height())

    def width(self):
        return (self.block_size + self.line_width) * self.columns + self.line_width

    def height(self):
        return (self.block_size + self.line_width) * self.rows + self.line_width

    # Calculates the position and functionality of every block on the grid
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
    #  Class that handles ONE ship
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
    #  Handles everything related to a player
    def __init__(self, guess_grid: Grid, ship_grid: Grid):
        self.name = None
        self.grid_player = guess_grid
        self.grid_enemy = ship_grid
        self.ships = [Ship(colors.get("blue"), "carrier", 5, Pos(screen_width / 3, (screen_height / 50))),
                      Ship(colors.get("blue"), "battleship", 4, Pos(screen_width / 3, (screen_height / 50) * 3)),
                      Ship(colors.get("blue"), "destroyer", 3, Pos(screen_width / 3, (screen_height / 50) * 5)),
                      Ship(colors.get("blue"), "submarine", 3, Pos(screen_width / 3, (screen_height / 50) * 7)),
                      Ship(colors.get("blue"), "patrol_boat", 2, Pos(screen_width / 3, (screen_height / 50) * 9))]
        self.ship_positions = None
        self.guesses = []
        self.hits = []


class Text:
    #  Simple class for drawing one line of text to screen
    def __init__(self, color, font, pos: Pos, text: str):
        self.color = color
        self.font = font
        self.pos = pos
        self.text = text
        self.surface = self.render()

    def render(self):
        return self.font.render(self.text, True, self.color)

    def draw(self, window):
        window.blit(self.surface, (self.pos.x, self.pos.y))


def place_ships(event, ships, grid_ship, dragging, offset: Pos):
    #  Mouse drag and drop functionality for ships
    changed_offset = offset
    ship_dragging = dragging
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
            for ship in ships:
                if ship.rect(grid_ship).collidepoint(event.pos):
                    ship_dragging = ship
                    mouse_x, mouse_y = event.pos
                    changed_offset = Pos(ship.position.x - mouse_x, ship.position.y - mouse_y)
        # Rotate ship with RMB
        if event.button == 3:
            for ship in ships:
                if ship.rect(grid_ship).collidepoint(event.pos):
                    ship.rotate()

    elif event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1:
            if ship_dragging:
                if grid_ship.line_area().colliderect(ship_dragging.rect(grid_ship)):
                    # If the ship is inside the play field, snap it to grid
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
        # Cheap way out for user error
        print("Ships not placed correctly")


def calc_ship_positions(player: Player):
    # When done with placing ships, this stores their positions
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
    # If a block is pressed, find out if it was a hit or miss
    player, enemy, block = kwargs
    if block in player.guesses:
        return False
    player.guesses.append(block)
    # Using human_name for readability, it's fast enough for this purpose
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


def render_graphics(players: [Player], screen, ok_button: Button, game_ended):
    # this should ideally be made with an entity system that handles their own states, but you know...
    default_font = pygame.font.SysFont('Comic Sans MS', round((screen_height / 100) * 6))  # Best font :)
    p1text = Text(colors.get("black"), default_font, Pos(screen_width / 100, (screen_height / 100) * 39), "Player 1")
    p2text = Text(colors.get("black"), default_font, Pos(screen_width / 100, (screen_height / 100) * 39), "Player 2")
    place = Text(colors.get("black"), default_font, Pos((screen_width / 100) * 50, (screen_height / 100) * 10),
                 "<- Place ships")
    guess = Text(colors.get("black"), default_font, Pos((screen_width / 100) * 50, (screen_height / 100) * 60),
                 "<- Bombs away")

    if game_phase == 0:
        players[0].grid_player.draw(screen)
        players[0].grid_enemy.draw(screen)
        ok_button.draw(screen)
        for ship in players[0].ships:
            ship.draw(screen, players[0].grid_player)
        p1text.draw(screen)
        place.draw(screen)
    elif game_phase == 1:
        players[1].grid_player.draw(screen)
        players[1].grid_enemy.draw(screen)
        ok_button.draw(screen)
        for ship in players[1].ships:
            ship.draw(screen, players[1].grid_player)
        p2text.draw(screen)
        place.draw(screen)
    elif game_phase == 2:
        if not game_ended:
            guess.draw(screen)
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
            # This score screen is an afterthought and handled really poorly
            game_over = Text(colors.get("black"), default_font, Pos(screen_width / 8, (screen_height / 8) * 2),
                             f"Player {game_ended} wins!")
            score1 = Text(colors.get("black"), default_font, Pos(screen_width / 8, (screen_height / 8) * 4),
                          f"Player 1: {len(players[0].hits)} points)")
            score2 = Text(colors.get("black"), default_font, Pos(screen_width / 8, (screen_height / 8) * 6),
                          f"Player 2: {len(players[1].hits)} points)")
            game_over.draw(screen)
            score1.draw(screen)
            score2.draw(screen)


def main():
    global game_phase
    pygame.init()
    pygame.display.set_caption("Battleship")
    screen = pygame.display.set_mode((screen_width, screen_height))

    players = [
        Player(Grid(colors.get("white"), colors.get("black"), 10, 10, round((screen_height / 100) * 3), Pos(0, 0), 1),
               Grid(colors.get("green"), colors.get("black"), 10, 10, round((screen_height / 100) * 4),
                    Pos(0, (screen_height / 100) * 50),
                    1)),
        Player(Grid(colors.get("white"), colors.get("black"), 10, 10, round((screen_height / 100) * 3),
                    Pos(0, 0), 1),
               Grid(colors.get("green"), colors.get("black"), 10, 10, round((screen_height / 100) * 4),
                    Pos(0, (screen_height / 100) * 50), 1))]

    clock = pygame.time.Clock()

    running = True
    mouse_offset = Pos(0, 0)
    game_ended = False
    ship_dragged = False
    ok_button = Button(screen_width / 6, screen_height / 20,
                       Pos(screen_width / 2 - (screen_width / 6) / 2, screen_height - (screen_height / (20 - 10))),
                       colors.get("green"),
                       ok_button_clicked)

    while running:
        screen.fill(colors.get("white"))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_phase == 0:
                # Place ships Player 1
                ship_dragged, mouse_offset = place_ships(event, players[0].ships, players[0].grid_player, ship_dragged,
                                                         mouse_offset)
                ok_button.click(event, players[0])
            elif game_phase == 1:
                # Place ships Player 2
                ship_dragged, mouse_offset = place_ships(event, players[1].ships, players[1].grid_player, ship_dragged,
                                                         mouse_offset)
                ok_button.click(event, players[1])
            elif game_phase == 2:
                # Battle on
                if not game_ended:
                    if current_player == 0:
                        for block in players[0].grid_enemy.blocks:
                            block["button"].click(event, (players[0], players[1], block))
                    else:
                        for block in players[1].grid_enemy.blocks:
                            block["button"].click(event, (players[1], players[0], block))
                    game_ended = check_if_win(players)

        render_graphics(players, screen, ok_button, game_ended)
        pygame.display.flip()

        clock.tick(fps)


if __name__ == "__main__":
    main()
