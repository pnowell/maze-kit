#!/usr/bin/env python

import sys
import random
from PIL import Image
from maze import Maze
from maze import Point
from maze import Edge
from canvas import Canvas

if len(sys.argv) < 3:
  print 'Usage: %s maze_template.png output.png' % sys.argv[0]
  exit(1)

MAZE_TEMPLATE = sys.argv[1]

PIXELS_PER_SQUARE = 4

COLOR_LIST = Canvas.random_color_list()

# Maximum percent of available space to occupy
MAX_IMAGE_SIZE = 0.85

# First read the template
maze_template = Image.open(MAZE_TEMPLATE)
image_width = maze_template.width
image_height = maze_template.height
if image_width % 2 != 1 or image_height % 2 != 1:
  print 'Maze template must have odd sized dimensions (2*n + 1)'
  exit(1)
maze_width = image_width / 2
maze_height = image_height / 2

maze = Maze(maze_width, maze_height)

# Iterate over the template to reserve edges and set edges
x_range = {
  Edge.HORZ: [1, image_width, 2],
  Edge.VERT: [0, image_width, 2],
}
y_range = {
  Edge.HORZ: [image_height-1, -1, -2],
  Edge.VERT: [image_height-2, -1, -2],
}
for ori in [Edge.HORZ, Edge.VERT]:
  for maze_x, image_x in enumerate(xrange(*x_range[ori])):
    for maze_y, image_y in enumerate(xrange(*y_range[ori])):
      pixel = maze_template.getpixel((image_x, image_y))
      if pixel[3] < 128:
        continue

      edge = Edge(ori, maze_x, maze_y)
      if pixel[0] < 128:
        maze.fill_edge(edge)
      elif pixel[1] < 128:
        maze.paint_edge(edge)
      else:
        maze.reserve_edge(edge)
        print 'Reserving %s x=%d y=%d' % (
            'HORZ' if ori == Edge.HORZ else 'VERT', maze_x, maze_y)

for step in maze.generate_each_wall(same_branch_probability=1.0):
  pass
  '''
  canvas = maze.create_canvas(PIXELS_PER_SQUARE, COLOR_LIST)
  image = canvas.get_image().copy()
  image.save('images/maze_from_template_%03d.png' % step)
  '''

canvas = maze.create_canvas(PIXELS_PER_SQUARE, COLOR_LIST)
color_image = canvas.get_image().copy()
canvas.fill_rgb([0, 0, 0])
bw_image = canvas.get_image()

# Create the image into which we'll paste the maze
full_canvas = Canvas(size=Canvas.LETTER, dpi=300, color=Canvas.COLORS['WHITE'])
full_image = full_canvas.get_image()

# Scale the two images appropriately
half_height = full_canvas.height / 2
new_size = canvas.compute_max_resize(
  full_canvas.width * MAX_IMAGE_SIZE, half_height * MAX_IMAGE_SIZE)
color_image = color_image.resize(new_size, Image.NEAREST)
bw_image = bw_image.resize(new_size, Image.NEAREST)

# Create a copy and change all colors to opaque black
bw_pos = (
  (full_canvas.width - new_size[0]) / 2,
  (half_height - new_size[1]) / 2)
color_pos = (bw_pos[0], bw_pos[1] + half_height)
full_image.alpha_composite(bw_image, dest=bw_pos)
full_image.alpha_composite(color_image, dest=color_pos)

# Save the full image
full_image.save(sys.argv[2])
