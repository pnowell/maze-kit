import random
import numpy as np
from PIL import Image

class Canvas:

  LETTER = [8.5, 11]

  COLORS = {
    'RED': [255, 0, 0, 255],
    'ORANGE': [255, 191, 0, 255],
    'YELLOW': [255, 255, 0, 255],
    'GREEN': [0, 255, 0, 255],
    'BLUE': [0, 127, 255, 255],
    'PURPLE': [127, 0, 255, 255],
    'BLACK': [0, 0, 0, 255],
    'WHITE': [255, 255, 255, 255],
  }

  @staticmethod
  def random_color_list():
    color_list = [
        Canvas.COLORS[c] for c in Canvas.COLORS if c not in ['BLACK', 'WHITE']
    ]
    random.shuffle(color_list)
    return color_list

  def __init__(self, width=None, height=None, size=None, dpi=None, color=[0, 0, 0, 0]):
    if size is not None and dpi is not None:
      width = int(size[0] * dpi)
      height = int(size[1] * dpi)
    self.width = width
    self.height = height
    self.image_data = np.empty((height, width, 4), dtype=np.uint8)
    self.image_data[:] = color

  def get_image(self):
    return Image.fromarray(self.image_data)

  def save(self, filename):
    self.get_image().save(filename)

  def compute_max_resize(self, width, height):
    max_width = int(width)
    max_height = int(height)
    limit_aspect = float(max_height) / float(max_width)
    self_aspect = float(self.height) / float(self.width)
    if limit_aspect > self_aspect:
      # Limiting space has relatively more height than needed, so limit on width
      return (max_width, int(self_aspect * max_width))
    else:
      # Limiting space has relatively little height, so limit on height
      return (max_height, int(max_height / self_aspect))

  def draw_line(self, p0, p1, color):
    disp = p1 - p0
    axis0 = 0 if abs(disp[0, 0]) > abs(disp[0, 1]) else 1
    axis1 = 1 - axis0
    if disp[0, axis0] < 0:
      swap = p1
      p1 = p0
      p0 = swap
      disp = -disp

    axis1_inc = 1
    modulus = disp[0, axis0]
    slope = disp[0, axis1]
    if slope < 0:
      slope = -slope
      axis1_inc = -1
    remainder = modulus / 2

    p = p0.copy()
    self.image_data[self.height - 1 - p[0, 1], p[0, 0]] = color
    while p[0, axis0] < p1[0, axis0]:
      p[0, axis0] += 1
      remainder += slope
      if remainder > modulus:
        remainder -= modulus
        p[0, axis1] += axis1_inc
      self.image_data[self.height - 1 - p[0, 1], p[0, 0]] = color

  def fill_rgb(self, rgb):
    for y in xrange(0, len(self.image_data)):
      for x in xrange(0, len(self.image_data[0])):
        self.image_data[y, x][0:3] = rgb
