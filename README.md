# Pathfinding visualization

This project uses Pygame to simulate the A\* pathfinding algorithm.

## How-to

- Right click to set the starting point
- Middle click (press the mouse wheel) to set the ending point

- Left click to toggle an obstacle at a cell
- Left click and drag to create multiple obstacles
- Right click and drag to delete multiple obstacles

- Press <kbd>Space</kbd> to explore one step deeper in the algorithm (this is also used to begin pathfinding)
- Press <kbd>&equals;</kbd> as the equivalent of repeatedly hitting <kbd>Space</kbd> (once every 10 milliseconds) until the shortest path has been found
- Press <kbd>D</kbd> to toggle the ability to move diagonally (this is `True` by default)
- Press <kbd>X</kbd> to clear the nodes explored by the algorithm

- Press <kbd>Shift</kbd>+<kbd>X</kbd> to clear everything

- Scroll to change the grid size

- Press <kbd>W</kbd> to write the current state (starting point, ending point, and obstacles) to a file. This state can be loaded by running the program with the path to the file. For example:

```bash
python3 main.py PathfindingVisualization_State-1735065000000000000.pickle
```

## Examples

Examples are available in the `examples/` directory (🤯). To try one, load the appropriate file as saved state:

```bash
python3 main.py examples/maze1.pickle
```

## Installation

Clone the repo, and install the dependencies (only Pygame in this case):

```bash
$ git clone https://github.com/prawnydagrate/PathfindingVisualization
$ cd PathfindingVisualization
$ python3 -m pip install -r requirements.txt
```

Start with:

```bash
$ python3 main.py
```
