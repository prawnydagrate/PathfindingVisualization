from xnode import XNode
import math
import os
import sys
import time

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
pygame = __import__("pygame")


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


def fix_cols():
    global cols
    if cols not in range(cols_min, cols_max + 1, cols_step):
        cols = cols_default


def increase_cols():
    global cols
    if cols < cols_max:
        cols += cols_step
        update()


def decrease_cols():
    global cols
    if cols > cols_min:
        cols -= cols_step
        update()


def distance(pos1: tuple[int, int], pos2: tuple[int, int]) -> int:
    r1, c1 = pos1
    r2, c2 = pos2
    return round(math.sqrt((r2 - r1) ** 2 + (c2 - c1) ** 2) * h_multiplier)


def explore_step():
    global exploring, fast
    if not exploring or start_cell is None or end_cell is None:
        fast = False
        return
    if len(xnodes) > 0:
        xns = list(xn for xn in xnodes if not xn.closed)
        if len(xns) == 0:
            fast = False
            return
        cell = min(xns)
    else:
        cell = XNode(0, distance(start_cell, end_cell), start_cell)
        xnodes.append(cell)
    cell.closed = True
    r, c = cell.pos
    for npos in (
        (r - 1, c - 1),
        (r - 1, c),
        (r - 1, c + 1),
        (r, c - 1),
        (r + 1, c),
        (r + 1, c - 1),
        (r, c + 1),
        (r + 1, c + 1),
    ):
        if npos == end_cell:
            exploring = False
            cell.path = True
            c = cell
            while (c := c.from_) is not None:
                c.path = True
            fast = False
            return
        if npos in obstacles or npos == start_cell:
            continue
        nr, nc = npos
        if not (0 <= nr < rows and 0 <= nc < cols):
            continue
        newg = cell.g + distance(cell.pos, npos)
        newh = distance(npos, end_cell)
        xn = next((xn for xn in xnodes if xn.pos == npos), None)
        if xn is None:
            xn = XNode(newg, newh, npos, from_=cell)
            xnodes.append(xn)
            continue
        if xn.closed:
            continue
        if newg < xn.g:
            xn.g = newg
            xn.from_ = cell


def save_state():
    fname = f"PathfindingVisualization_State-{time.time_ns()}.{ss}"
    with open(fname, "wb") as f:
        ss_mod.dump(
            {
                ss_start_cell_key: start_cell,
                ss_end_cell_key: end_cell,
                ss_obstacles_key: obstacles,
                ss_cols_key: cols,
            },
            f,
        )
    print(f"Current state written to {fname}!")


def load_state():
    global cols, rows, cell_size, cells, start_cell, end_cell, obstacles
    saved_state = {}
    if (
        len(sys.argv) == 2
        and os.path.isfile(sfname := sys.argv[1])
        and os.path.splitext(sfname)[1] == f".{ss}"
    ):
        with open(sfname, "rb") as sf:
            s = ss_mod.load(sf)
            if isinstance(s, dict):
                saved_state = s
    cols = c if isinstance(c := saved_state.get(ss_cols_key), int) else cols_default
    fix_cols()
    rows = 0
    cell_size = 0
    cells = []
    update()
    start_cell = (
        tuple(s)
        if isinstance(s := saved_state.get(ss_start_cell_key), list)
        or isinstance(s, tuple)
        and len(s) == 2
        else None
    )
    end_cell = (
        tuple(e)
        if isinstance(e := saved_state.get(ss_end_cell_key), list)
        or isinstance(e, tuple)
        and len(e) == 2
        else None
    )
    obstacles = (
        [
            tuple(o)
            for o in obs
            if isinstance(o, list) or isinstance(o, tuple) and len(o) == 2
        ]
        if isinstance(obs := saved_state.get(ss_obstacles_key), list)
        or isinstance(obs, tuple)
        else []
    )
    if start_cell in obstacles:
        start_cell = None
    if end_cell in obstacles:
        end_cell = None


# constants
scr_width = 960
scr_height = 600
scr_size = (scr_width, scr_height)

cols_default = 32
cols_min = 8
cols_max = 64
cols_step = 8
border = 1

cell_color = "#efefef"
cell_color_hover = "#d6d6d6"

start_cell_color = "lightgreen"
end_cell_color = "#ff8f8f"

obstacle_color = "#5f5f5f"

xnode_color = "#e3e3e3"
xnode_color_path = "#ffff8f"
xnode_color_closed = "#cccccc"
h_multiplier = 1000

border_color = "#333333"

caption = "A* Pathfinding Visualization"


ss = "pickle"
ss_mod = __import__(ss)
ss_start_cell_key = "start_cell"
ss_end_cell_key = "end_cell"
ss_obstacles_key = "obstacles"
ss_cols_key = "cols"

EXPLOREEVENT = pygame.USEREVENT + 1

# initialize pygame window
pygame.init()
scr = pygame.display.set_mode(scr_size)
pygame.display.set_caption(caption)

# initialize variables
cols = 0
rows = 0
cell_size = 0
cells = []
start_cell = None
end_cell = None
obstacles = []
load_state()

ldown = False
lmoved = False
rdown = False
rmoved = False
mdown = False
mmoved = False
shift = False

exploring = False
fast = False
xnodes = []

pygame.time.set_timer(EXPLOREEVENT, 10)

while True:
    # handle events
    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                pygame.quit()
                exit()
            case pygame.KEYDOWN:
                match event.key:
                    case pygame.K_LSHIFT | pygame.K_RSHIFT:
                        shift = True
                    case _:
                        pass
            case pygame.KEYUP:
                match event.key:
                    case pygame.K_w:
                        if not shift:
                            save_state()
                    case pygame.K_LSHIFT | pygame.K_RSHIFT:
                        shift = False
                    case pygame.K_UP:
                        increase_cols()
                    case pygame.K_DOWN:
                        decrease_cols()
                    case pygame.K_SPACE:
                        if (
                            not any(
                                (
                                    ldown,
                                    lmoved,
                                    rdown,
                                    rmoved,
                                    exploring,
                                    xnodes,
                                )
                            )
                            and validate_selections()
                        ):
                            exploring = True
                        if exploring:
                            explore_step()
                    case pygame.K_EQUALS:
                        if (
                            not any(
                                (
                                    ldown,
                                    lmoved,
                                    rdown,
                                    rmoved,
                                    # exploring,
                                    # xnodes,
                                )
                            )
                            and validate_selections()
                        ):
                            exploring = True
                            fast = True
                    case pygame.K_x:
                        if shift:
                            obstacles.clear()
                            ldown = False
                            lmoved = False
                            rdown = False
                            rmoved = False
                        exploring = False
                        fast = False
                        xnodes.clear()
                    case _:
                        pass
            case pygame.MOUSEWHEEL:
                if not exploring:
                    if event.y > 0:
                        decrease_cols()
                    elif event.y < 0:
                        increase_cols()
            case pygame.MOUSEBUTTONDOWN:
                if not exploring:
                    match event.button:
                        case pygame.BUTTON_LEFT:
                            ldown = True
                            lmoved = False
                        case pygame.BUTTON_RIGHT:
                            rdown = True
                            rmoved = False
                        case pygame.BUTTON_MIDDLE:
                            mdown = True
                            mmoved = False
            case pygame.MOUSEMOTION:
                if not exploring:
                    if ldown:
                        lmoved = True
                        if (
                            (hovered := get_hovered_cell())
                            and start_cell != hovered
                            and end_cell != hovered
                            and hovered not in obstacles
                            and not xnodes
                        ):
                            obstacles.append(hovered)
                    elif rdown:
                        rmoved = True
                        if (
                            (hovered := get_hovered_cell())
                            and hovered in obstacles
                            and not xnodes
                        ):
                            obstacles.remove(hovered)
                    elif mdown:
                        mmoved = True
            case pygame.MOUSEBUTTONUP:
                if not exploring:
                    if ldown:
                        if event.button == pygame.BUTTON_LEFT:
                            hovered = get_hovered_cell()
                            if (
                                lmoved
                                and hovered
                                and hovered not in obstacles
                                and not xnodes
                            ):
                                obstacles.append(hovered)
                            elif not lmoved and not xnodes:
                                if hovered in obstacles:
                                    obstacles.remove(hovered)
                                elif start_cell != hovered != end_cell:
                                    obstacles.append(hovered)
                            ldown = False
                            lmoved = False
                    else:
                        match event.button:
                            case pygame.BUTTON_RIGHT:  # start cell
                                if not rmoved and not xnodes:
                                    sel = get_hovered_cell()
                                    if start_cell == sel:
                                        start_cell = None
                                    elif end_cell != sel and sel not in obstacles:
                                        start_cell = sel
                                rmoved = False
                                rdown = False
                            case pygame.BUTTON_MIDDLE:  # end cell
                                if not mmoved:
                                    if not xnodes:
                                        sel = get_hovered_cell()
                                        if end_cell == sel:
                                            end_cell = None
                                        elif start_cell != sel and sel not in obstacles:
                                            end_cell = sel
                                mdown = False
                                mmoved = False
            case glob:
                if fast and glob == EXPLOREEVENT:
                    if exploring:
                        explore_step()

    # draw borders
    scr.fill(border_color)

    # draw cells
    hovered = get_hovered_cell()
    for r, row in enumerate(cells):
        for c, (x, y, endx, endy) in enumerate(row):
            pos = (r, c)
            rect = pygame.Rect(x, y, cell_size, cell_size)
            pygame.draw.rect(
                scr,
                (  # color logic 💀
                    start_cell_color
                    if start_cell == pos
                    else (
                        end_cell_color
                        if end_cell == pos
                        else (
                            obstacle_color
                            if pos in obstacles
                            else (
                                (
                                    xnode_color_path
                                    if xn.path
                                    else (
                                        xnode_color_closed if xn.closed else xnode_color
                                    )
                                )
                                if (
                                    xn := next(
                                        (xn for xn in xnodes if xn.pos == pos), None
                                    )
                                )
                                is not None
                                else cell_color_hover if pos == hovered else cell_color
                            )
                        )
                    )
                ),
                rect,
            )

    # update screen
    pygame.display.flip()
