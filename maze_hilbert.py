#!/usr/bin/env python

import numpy as np
import xform
from PIL import Image
from canvas import Canvas


GRID_SIZE = 1024
IMAGE_SIZE = GRID_SIZE + 1
COLOR_LIST = [
  [255,   0,   0, 255], # 1024
  [255, 127,   0, 217], #  512
  [255, 255,   0, 182], #  256
  [127, 255,   0, 152], #  128
  [  0, 255,   0, 123], #   64
  [  0, 255, 127,  98], #   32
  [  0, 255, 255,  74], #   16
  [  0, 127, 255,  51], #    8
  [  0,   0, 255,  31], #    4
]

POINT_BUFFER = [
  np.matrix([-0.5, 3. / 32., 1.]),
  np.matrix([-0.5, -0.5, 1.]),
  np.matrix([0.5, -0.5, 1.]),
  np.matrix([0.5, 3. / 32., 1.]),
  np.matrix([0.0, 0.0, 1.]),
  np.matrix([0.0, 0.5, 1.]),
]

LINE_SEGMENTS = [
  [0, 1],
  [1, 2],
  [2, 3],
  [4, 5],
]

HALF_SCALE_XFORM = xform.scale(0.5, 0.5)

CHILD_XFORMS = [
  # Top right
  xform.rotate(clockwise=True) * xform.translate(0.5, 0.5) * HALF_SCALE_XFORM,
  # Top left
  xform.rotate(clockwise=False) * xform.translate(-0.5, 0.5) * HALF_SCALE_XFORM,
  # Bottom right
  xform.translate(0.5, -0.5) * HALF_SCALE_XFORM,
  # Bottom left
  xform.translate(-0.5, -0.5) * HALF_SCALE_XFORM,
]

class DrawState:

  def __init__(self, level, color_index, xfm):
    self.level = level
    self.color_index = color_index
    self.xfm = xfm

  def create_child_state(self, child_xform):
    return DrawState(
        self.level - 1,
        self.color_index,
        child_xform * self.xfm)

  def draw_pattern(self, canvas):
    for line_segment in LINE_SEGMENTS:
      p0 = POINT_BUFFER[line_segment[0]] * self.xfm
      p1 = POINT_BUFFER[line_segment[1]] * self.xfm
      canvas.draw_line(
          np.rint(p0).astype(int),
          np.rint(p1).astype(int),
          COLOR_LIST[self.color_index])




canvas = Canvas(IMAGE_SIZE, IMAGE_SIZE)

image_xform = (
    xform.translate(0.5, 0.5)
    * xform.scale(1. * GRID_SIZE, 1. * GRID_SIZE))

# Populate the stack with all levels
s = []
size = GRID_SIZE
color_index = 0
level = 0
while size >= 4:
  s.append(DrawState(level, color_index, image_xform))
  size = size / 2
  level = level + 1
  color_index = (color_index + 1) % len(COLOR_LIST)

# Iterate until there's nothing left in the stack
while s:
  state = s.pop()

  # If we're not at the correct level, push back all the children of this
  # state and move on.
  if state.level > 0:
    for child_xform in CHILD_XFORMS:
      s.append(state.create_child_state(child_xform))
  else:
    # Otherwise draw the current state
    state.draw_pattern(canvas)

canvas.save("images/maze_hilbert.png")
