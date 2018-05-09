#!/usr/bin/env python

from PIL import Image
from maze import Maze
from maze import Point
from maze import Edge
from canvas import Canvas

MAZE_WIDTH = 20
MAZE_HEIGHT = 20

PIXELS_PER_SQUARE = 4

COLOR_LIST = Canvas.random_color_list()

# Maximum percent of available space to occupy
MAX_IMAGE_SIZE = 0.85

def gen_maze(image_index):
  maze = Maze(MAZE_WIDTH, MAZE_HEIGHT)
  exits = maze.choose_exits(2)
  maze.create_border(exits)
  maze.generate_all_walls(same_branch_probability=1.0)
  canvas = maze.create_canvas(PIXELS_PER_SQUARE, COLOR_LIST)
  color_image = canvas.get_image().copy()
  canvas.fill_rgb([0, 0, 0])
  bw_image = canvas.get_image()

  # Create the image into which we'll paste the maze
  full_canvas = Canvas(size=Canvas.LETTER, dpi=300, color=Canvas.WHITE)
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
  full_image.save('images/maze_%03d.png' % image_index)


# Make a few
for i in xrange(0, 20):
  print 'Generating maze %d...' % i
  gen_maze(i)
