import math
from functools import total_ordering
from typing import Self

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
    global cols
    if cols < 64:
        cols += 8
        update()


def decrease_cols():
    global cols
    if cols > 8:
        cols -= 8
        update()


@total_ordering
class XNode:
    def __init__(
        self,
        g: int,
        h: int,
        pos: tuple[int, int],
        closed: bool = False,
        from_: Self | None = None,
        path: bool = False,
    ):
        self._g = g
        self._h = h
        self._pos = pos
        self._closed = closed
        self._from = from_
        self._path = path

    @property
    def f(self):
        return self._g + self._h

    @property
    def g(self):
        return self._g

    @g.setter
    def g(self, value: int):
        self._g = value

    @property
    def h(self):
        return self._h

    @h.setter
    def h(self, value: int):
        self._h = value

    @property
    def cost(self):
        return (self._h + self._g, self._h, self._g)

    @property
    def pos(self):
        return self._pos

    @property
    def closed(self):
        return self._closed

    @closed.setter
    def closed(self, value: bool):
        self._closed = value

    @property
    def from_(self):
        return self._from

    @from_.setter
    def from_(self, value: Self | None):
        self._from = value

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value: bool):
        self._path = value

    def __repr__(self):
        return f"XNode(f={self.f}, h={self._h}, g={self._g}, pos={self._pos}, closed={self._closed}, path={self._path})"

    def __eq__(self, other):
        return (
            self.cost == other.cost and self._pos == other._pos
            if self.__class__ is other.__class__
            else NotImplemented
        )

    def __ne__(self, other):
        eq = self.__eq__(other)
        return NotImplemented if eq is NotImplemented else not eq

    def __hash__(self):
        return hash((self.f, self.g, self.h, self.pos))

    def __lt__(self, other):
        return (
            self.cost < other.cost
            if self.__class__ is other.__class__
            else NotImplemented
        )

    # def __le__(self, other):
    #     return self._cost <= other._cost if self.__class__ is other.__class__ else NotImplemented

    # def __gt__(self, other):
    #     return self._cost > other._cost if self.__class__ is other.__class__ else NotImplemented

    # def __ge__(self, other):
    #     return self._cost >= other._cost if self.__class__ is other.__class__ else NotImplemented


def distance(pos1: tuple[int, int], pos2: tuple[int, int]) -> int:
    r1, c1 = pos1
    r2, c2 = pos2
    return math.floor(math.sqrt((r2 - r1) ** 2 + (c2 - c1) ** 2) * h_multiplier)


def explore_step():
    global exploring
    if not exploring or start_cell is None or end_cell is None:
        return
    if len(xnodes) > 0:
        xns = list(xn for xn in xnodes if not xn.closed)
        if len(xns) == 0:
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
        # BUGFIX
        # if newg + newh < xn.f:
        #     xn.g = newg
        #     xn.h = newh
        #     xn.from_ = cell
        xn.g = newg
        xn.h = newh
        xn.from_ = cell



# constants
scr_width = 960
scr_height = 600
scr_size = (scr_width, scr_height)

cols = 32
border = 1

cell_color = "#efefef"
cell_color_hover = "#d6d6d6"

start_cell_color = "lightgreen"
end_cell_color = "#ff8f8f"

obstacle_color = "#888888"

xnode_color = "#e3e3e3"
xnode_color_path = "#ffff8f"
xnode_color_closed = "#b4b4b4"
h_multiplier = 1000

border_color = "#333333"

caption = "A* Pathfinding Visualization"

# initialize pygame window
pygame.init()
scr = pygame.display.set_mode(scr_size)
pygame.display.set_caption(caption)

# initialize variables
rows = 0
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
mdown = False
mmoved = False
shift = False

exploring = False
xnodes = []

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
                                    ldragging,
                                    lmoved,
                                    rdragging,
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
                    case pygame.K_x:
                        if shift:
                            obstacles.clear()
                            ldragging = False
                            lmoved = False
                            rdragging = False
                            rmoved = False
                        exploring = False
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
                            ldragging = True
                            lmoved = False
                        case pygame.BUTTON_RIGHT:
                            rdragging = True
                            rmoved = False
                        case pygame.BUTTON_MIDDLE:
                            mdown = True
                            mmoved = False
            case pygame.MOUSEMOTION:
                if not exploring:
                    if ldragging:
                        lmoved = True
                        if (
                            (hovered := get_hovered_cell())
                            and start_cell != hovered
                            and end_cell != hovered
                            and hovered not in obstacles
                            and not xnodes
                        ):
                            obstacles.append(hovered)
                    elif rdragging:
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
                    if ldragging:
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
                            ldragging = False
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
                                rdragging = False
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
            case _:
                pass

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
