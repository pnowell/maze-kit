#!/usr/bin/python

from PIL import Image
from maze import Maze
from maze import Point
from maze import Edge
from canvas import Canvas

MAZE_SMALL_WIDTH = 5
MAZE_SMALL_HEIGHT = 6

MAZE_WIDTH = 9
MAZE_HEIGHT = 9

PIXELS_PER_SQUARE = 4

COLOR_LIST = Canvas.random_color_list()

MAZE_EXITS = [
  # South
  Maze.BOTTOM_MIDDLE,
  # North
  Maze.TOP_MIDDLE,
  # West
  Maze.MIDDLE_LEFT,
  # East
  Maze.MIDDLE_RIGHT,
]

CORRIDOR_EDGES = [
  # South
  [
    Edge(Edge.VERT, 0, -1),
    Edge(Edge.VERT, 1, -1),
  ],
  # North
  [
    Edge(Edge.VERT, 0, 0),
    Edge(Edge.VERT, 1, 0),
  ],
  # West
  [
    Edge(Edge.HORZ, -1, 0),
    Edge(Edge.HORZ, -1, 1),
  ],
  # East
  [
    Edge(Edge.HORZ, 0, 0),
    Edge(Edge.HORZ, 0, 1),
  ],
]

CORRIDOR_DIR = [
  # South
  (0, -1),
  # North
  (0, 1),
  # West
  (-1, 0),
  # East
  (1, 0),
]

PADDING = 2
MAX_IMAGE_SIZE = 0.85


mini_maze = Maze(MAZE_SMALL_WIDTH, MAZE_SMALL_HEIGHT)
mini_maze.create_border([
    mini_maze.border_edges[Maze.TOP_LEFT_V],
    mini_maze.border_edges[Maze.BOTTOM_RIGHT_V]])
mini_maze.generate_all_walls(same_branch_probability=0.7)

mazes = []
for y in xrange(0, MAZE_SMALL_HEIGHT):
  maze_row = []
  for x in xrange(0, MAZE_SMALL_WIDTH):
    maze = Maze(MAZE_WIDTH, MAZE_HEIGHT)
    exits = []
    for i, edge in enumerate(mini_maze.square_edges(x, y)):
      if mini_maze.get_edge(edge) < 0:
        exits.append(maze.border_edges[MAZE_EXITS[i]])
    maze.create_border(exits)
    maze.generate_all_walls(same_branch_probability=0.9)
    maze_row.append(maze)
  mazes.append(maze_row)

total_width = (MAZE_WIDTH + PADDING) * len(mazes[0]) + PADDING
total_height = (MAZE_HEIGHT + PADDING) * len(mazes) + PADDING
master_maze = Maze(total_width, total_height)

for y, maze_row in enumerate(mazes):
  y_offset = PADDING + y * (MAZE_HEIGHT + PADDING)
  for x, maze in enumerate(maze_row):
    x_offset = PADDING + x * (MAZE_WIDTH + PADDING)

    # Copy the maze into the master maze
    for edge in maze.all_edges():
      master_edge = Edge(edge.ori, edge.x + x_offset, edge.y + y_offset)
      master_maze.set_edge(master_edge, maze.get_edge(edge))

    # For each exit, add a corridor of length PADDING
    for i, edge in enumerate(mini_maze.square_edges(x, y)):
      if mini_maze.get_edge(edge) >= 0:
        continue
      padding_dir = CORRIDOR_DIR[i]
      for corr_pos in xrange(0, PADDING):
        for offset_from_exit in CORRIDOR_EDGES[i]:
          exit_edge = maze.border_edges[MAZE_EXITS[i]]
          corr_edge = Edge(
              offset_from_exit.ori,
              exit_edge.x + offset_from_exit.x + x_offset,
              exit_edge.y + offset_from_exit.y + y_offset)
          corr_edge.x += padding_dir[0] * corr_pos
          corr_edge.y += padding_dir[1] * corr_pos
          master_maze.set_edge(corr_edge, 0)

# Fix the edge coloring
master_maze.initialize_state_from_edges()

canvas = master_maze.create_canvas(PIXELS_PER_SQUARE, COLOR_LIST)

# Create the image into which we'll paste the maze
full_canvas = Canvas(size=Canvas.LETTER, dpi=300, color=Canvas.WHITE)

new_size = canvas.compute_max_resize(
    full_canvas.width * MAX_IMAGE_SIZE, full_canvas.height * MAX_IMAGE_SIZE)

color_image = canvas.get_image().copy()
color_image = color_image.resize(new_size, Image.NEAREST)

canvas.fill_rgb([0, 0, 0])
bw_image = canvas.get_image()
bw_image = bw_image.resize(new_size, Image.NEAREST)

image_pos = (
    (full_canvas.width - new_size[0]) / 2,
    (full_canvas.height - new_size[1]) / 2)

full_image = full_canvas.get_image().copy()
full_image.alpha_composite(color_image, dest=image_pos)
full_image.save('images/maze_hierarchical_key.png')

full_image = full_canvas.get_image().copy()
full_image.alpha_composite(bw_image, dest=image_pos)
full_image.save('images/maze_hierarchical_bw.png')
