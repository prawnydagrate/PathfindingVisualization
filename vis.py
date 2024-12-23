import pygame


# helpers
def calc_cell_size():
    global cell_size
    cell_size = (scr_width - (cols - 1) * border) / cols


def repopulate_cells():
    global rows
    cells.clear()
    row = 0
    while True:
        cells.append([])
        y = row * (cell_size + border)
        if (endy := y + cell_size) > scr_height:
            break
        for col in range(cols):
            x = col * (cell_size + border)
            cells[row].append((x, y, x + cell_size, endy))
        row += 1
    rows = row


def update():
    calc_cell_size()
    repopulate_cells()


def get_hovered_cell() -> tuple[int, int] | None:
    if not pygame.mouse.get_focused():
        return None
    mx, my = pygame.mouse.get_pos()
    for r, row in enumerate(cells):
        for c, (x, y, endx, endy) in enumerate(row):
            if pygame.mouse.get_focused() and x <= mx <= endx and y <= my <= endy:
                return r, c


def validate_selections():
    return (
        start_cell
        and end_cell
        and start_cell[0] < rows
        and start_cell[1] < cols
        and end_cell[0] < rows
        and end_cell[1] < cols
    )


def increase_cols():
    global cols, cell_size
    if cols < 64:
        cols += 8
        update()


def decrease_cols():
    global cols, cell_size
    if cols > 8:
        cols -= 8
        update()


# constants
scr_width = 960
scr_height = 600
scr_size = (scr_width, scr_height)

cols = 32
rows = 0
border = 1

cell_color = "#efefef"
cell_color_hover = "#dddddd"
start_cell_color = "lightgreen"
end_cell_color = "#ff8f8f"
obstacle_color = "#888888"
border_color = "#333333"

caption = "A* Pathfinding Visualization"

# initialize pygame window
pygame.init()
scr = pygame.display.set_mode(scr_size)
pygame.display.set_caption(caption)

# initialize variables
cell_size = 0
cells = []
update()

start_cell = None
end_cell = None
obstacles = []

ldragging = False
lmoved = False
rdragging = False
rmoved = False

while True:
    # handle events
    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                pygame.quit()
                exit()
            case pygame.KEYUP:
                match event.key:
                    case pygame.K_UP:
                        increase_cols()
                    case pygame.K_DOWN:
                        decrease_cols()
                    case pygame.K_x:
                        obstacles.clear()
                    case _:
                        pass
            case pygame.MOUSEWHEEL:
                if event.y > 0:
                    decrease_cols()
                elif event.y < 0:
                    increase_cols()
            case pygame.MOUSEBUTTONDOWN:
                match event.button:
                    case pygame.BUTTON_LEFT:
                        ldragging = True
                        lmoved = False
                    case pygame.BUTTON_RIGHT:
                        rdragging = True
                        rmoved = False
            case pygame.MOUSEMOTION:
                if ldragging:
                    lmoved = True
                    if (
                        (hovered := get_hovered_cell())
                        and start_cell != hovered
                        and end_cell != hovered
                        and hovered not in obstacles
                    ):
                        obstacles.append(hovered)
                elif rdragging:
                    rmoved = True
                    if (
                        (hovered := get_hovered_cell())
                        and hovered in obstacles
                    ):
                        obstacles.remove(hovered)
            case pygame.MOUSEBUTTONUP:
                if ldragging:
                    if event.button == pygame.BUTTON_LEFT:
                        hovered = get_hovered_cell()
                        if lmoved and hovered and hovered not in obstacles:
                            obstacles.append(hovered)
                        elif not lmoved:
                            if hovered in obstacles:
                                obstacles.remove(hovered)
                            elif start_cell != hovered != end_cell:
                                obstacles.append(hovered)
                        ldragging = False
                        lmoved = False
                else:
                    match event.button:
                        case pygame.BUTTON_RIGHT:  # start cell
                            if not rmoved:
                                sel = get_hovered_cell()
                                if start_cell == sel:
                                    start_cell = None
                                elif end_cell != sel and sel not in obstacles:
                                    start_cell = sel
                            rmoved = False
                            rdragging = False
                        case pygame.BUTTON_MIDDLE:  # end cell
                            sel = get_hovered_cell()
                            if end_cell == sel:
                                end_cell = None
                            elif start_cell != sel and sel not in obstacles:
                                end_cell = sel
            case _:
                pass

    # draw borders
    scr.fill(border_color)

    # draw cells
    hovered = get_hovered_cell()
    for r, row in enumerate(cells):
        for c, (x, y, endx, endy) in enumerate(row):
            rect = pygame.Rect(x, y, cell_size, cell_size)
            pygame.draw.rect(
                scr,
                (
                    start_cell_color
                    if start_cell == (r, c)
                    else (
                        end_cell_color
                        if end_cell == (r, c)
                        else obstacle_color if (r, c) in obstacles
                        else cell_color_hover if (r, c) == hovered
                        else cell_color
                    )
                ),
                rect,
            )

    # update screen
    pygame.display.flip()
