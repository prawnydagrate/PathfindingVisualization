from typing import Self
from functools import total_ordering


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
