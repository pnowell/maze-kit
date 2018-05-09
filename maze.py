import random
import numpy as np
from canvas import Canvas

class Edge:

  # Enum values for edge orientations.
  HORZ = 0
  VERT = 1

  def __init__(self, ori, x, y):
    self.ori = ori
    self.x = x
    self.y = y

  def __repr__(self):
    return 'Edge(ori={ori}, x={x}, y={y})'.format(
        ori = 'HORZ' if self.ori == Edge.HORZ else 'VERT',
        x = self.x,
        y = self.y)

  def __eq__(self, other):
    if isinstance(other, Edge):
      return (
          (self.ori == other.ori)
          and (self.x == other.x)
          and (self.y == other.y))
    return False

  def __hash__(self):
    return hash(self.__repr__())


class Point:

  TAKEN = 'TAKEN'

  def __init__(self, x, y):
    self.x = x
    self.y = y

  def __repr__(self):
    return 'Point(x={x}, y={y})'.format(
        x = self.x,
        y = self.y)

  def __eq__(self, other):
    if isinstance(other, Edge):
      return (
          (self.x == other.x)
          and (self.y == other.y))
    return False

  def __hash__(self):
    return hash(self.__repr__())


class Maze:

  BOTTOM_LEFT_H = 'BOTTOM_LEFT_H'
  BOTTOM_MIDDLE = 'BOTTOM_MIDDLE'
  BOTTOM_RIGHT_H = 'BOTTOM_RIGHT_H'
  BOTTOM_LEFT_V = 'BOTTOM_LEFT_V'
  MIDDLE_LEFT = 'MIDDLE_LEFT'
  TOP_LEFT_V = 'TOP_LEFT_V'
  BOTTOM_RIGHT_V = 'BOTTOM_RIGHT_V'
  MIDDLE_RIGHT = 'MIDDLE_RIGHT'
  TOP_RIGHT_V = 'TOP_RIGHT_V'
  TOP_LEFT_H = 'TOP_LEFT_H'
  TOP_MIDDLE = 'TOP_MIDDLE'
  TOP_RIGHT_H = 'TOP_RIGHT_H'

  # Enum values for edge states.
  EMPTY = -1
  RESERVED = -2
  PAINTED = -3

  def __init__(self, width, height):
    self.width = width
    self.height = height
    self.edges = (2 * width * height + width + height) * [Maze.EMPTY]
    self.edge_size = [(width, height + 1), (width + 1, height)]
    self.edge_offset = [0, width * (height + 1)]
    self.points = ((width+1) * (height+1)) * [None]
    self.potential_edge_points = []
    self.wall_size = []
    self.border_edges = {
        'BOTTOM_LEFT_H'  : Edge(Edge.HORZ,         0,          0),
        'BOTTOM_MIDDLE'  : Edge(Edge.HORZ, width / 2,          0),
        'BOTTOM_RIGHT_H' : Edge(Edge.HORZ, width - 1,          0),
        'TOP_LEFT_H'     : Edge(Edge.HORZ,         0,     height),
        'TOP_MIDDLE'     : Edge(Edge.HORZ, width / 2,     height),
        'TOP_RIGHT_H'    : Edge(Edge.HORZ, width - 1,     height),
        'BOTTOM_LEFT_V'  : Edge(Edge.VERT,         0,          0),
        'MIDDLE_LEFT'    : Edge(Edge.VERT,         0, height / 2),
        'TOP_LEFT_V'     : Edge(Edge.VERT,         0, height - 1),
        'BOTTOM_RIGHT_V' : Edge(Edge.VERT,     width,          0),
        'MIDDLE_RIGHT'   : Edge(Edge.VERT,     width, height / 2),
        'TOP_RIGHT_V'    : Edge(Edge.VERT,     width, height - 1),
    }

  def get_edge(self, edge):
    return self.edges[
        self.edge_offset[edge.ori]
        + edge.y * self.edge_size[edge.ori][0]
        + edge.x]

  def set_edge(self, edge, v):
    self.edges[
        self.edge_offset[edge.ori]
        + edge.y * self.edge_size[edge.ori][0]
        + edge.x] = v

  def get_point(self, point):
    return self.points[point.y * self.width + point.x]

  def set_point(self, point, v):
    self.points[point.y * self.width + point.x] = v

  # Iterates around the border of the maze.
  # Yields 4-tuple of:
  #   edge
  #   point
  #   perpendicular edge (None for corners)
  #   point at end of perpendicular edge (None for corners)
  def border_iter(self):
    # Bottom left -> bottom right
    for x in xrange(0, self.width-1):
      yield (
          Edge(Edge.HORZ, x, 0),
          Point(x+1, 0),
          Edge(Edge.VERT, x+1, 0),
          Point(x+1, 1))
    yield (
        Edge(Edge.HORZ, self.width-1, 0),
        Point(self.width, 0),
        None,
        None)
    # Bottom right -> top right
    for y in xrange(0, self.height-1):
      yield (
          Edge(Edge.VERT, self.width, y),
          Point(self.width, y+1),
          Edge(Edge.HORZ, self.width-1, y+1),
          Point(self.width-1, y+1))
    yield (
        Edge(Edge.VERT, self.width, self.height-1),
        Point(self.width, self.height),
        None,
        None)
    # Top right -> top left
    for x in xrange(self.width-1, 0, -1):
      yield (
          Edge(Edge.HORZ, x, self.height),
          Point(x, self.height),
          Edge(Edge.VERT, x, self.height-1),
          Point(x, self.height-1))
    yield (
        Edge(Edge.HORZ, 0, self.height),
        Point(0, self.height),
        None,
        None)
    # Top left -> bottom left
    for y in xrange(self.height-1, 0, -1):
      yield (
          Edge(Edge.VERT, 0, y),
          Point(0, y),
          Edge(Edge.HORZ, 0, y),
          Point(1, y))
    yield (
        Edge(Edge.VERT, 0, 0),
        Point(0, 0),
        None,
        None)

  def choose_exits(self, num_exits):
    potential_edges = set()
    for border, pnt, perp, perp_pnt in self.border_iter():
      if perp:
        potential_edges.add(border)
    return random.sample(potential_edges, num_exits)

  def add_potential(self, wall, edge, pnt):
    point_info = self.get_point(pnt)
    # Check to see if the point has been claimed.
    if point_info == Point.TAKEN:
      return
    # Check to see if the edge is empty
    if self.get_edge(edge) != Maze.EMPTY:
      return

    if point_info is None:
      point_info = set()
    point_info.add((wall, edge))
    self.set_point(pnt, point_info)

    if self.potential_edge_points[wall] is None:
      self.potential_edge_points[wall] = {}
    self.potential_edge_points[wall][edge] = (pnt, self.wall_size[wall])

  def create_border(self, exits=None):
    exit_set = set(exits or [])
    for border, pnt, perp, perp_pnt in self.border_iter():
      if border not in exit_set:
        self.set_edge(border, 0)

  def fill_edge(self, edge):
    self.set_edge(edge, 0)

  def reserve_edge(self, edge):
    self.set_edge(edge, Maze.RESERVED)

  def paint_edge(self, edge):
    self.set_edge(edge, Maze.PAINTED)

  def _discover_wall_from_edge(self, edge, wall, processed_edges):
    temp_wall_size = 0
    neighbors_to_check = [edge]
    processed_edges.add(edge)
    while neighbors_to_check:
      edge = neighbors_to_check.pop()
      self.set_edge(edge, wall)
      temp_wall_size += 1

      # Claim both ends of this edge
      for neighbor_pnt in self.edge_points(edge):
        self.take_point(neighbor_pnt)

      # Check all neighbors of this edge to see if we need to process them.
      for neighbor_edge, neighbor_pnt in self.neighbors_of_edge(edge):
        if neighbor_edge in processed_edges:
          continue
        processed_edges.add(neighbor_edge)
        neighbor_value = self.get_edge(neighbor_edge)
        if neighbor_value == Maze.EMPTY:
          self.add_potential(wall, neighbor_edge, neighbor_pnt)
        elif neighbor_value >= 0:
          neighbors_to_check.append(neighbor_edge)

    self.wall_size[wall] = temp_wall_size

  def all_edges(self):
    for ori in [Edge.HORZ, Edge.VERT]:
      for x in xrange(0, self.edge_size[ori][0]):
        for y in xrange(0, self.edge_size[ori][1]):
          yield Edge(ori, x, y)

  def initialize_state_from_edges(self):
    # Reset things to make this method re-callable
    self.wall_size = []

    processed_edges = set()
    for edge in self.all_edges():
      if edge in processed_edges:
        continue
      edge_value = self.get_edge(edge)
      if edge_value < 0:
        continue

      # At this point we've discovered part of a new wall
      wall = len(self.wall_size)
      self.wall_size.append(0)
      self.potential_edge_points.append(None)
      self._discover_wall_from_edge(edge, wall, processed_edges)

    # Do an iteration around the border to detect double-wide gaps and
    # insert a potential edge with a new wall in between.
    last_pnt = None
    last_perp = None
    last_perp_pnt = None
    last_empty = False
    curr_pnt = None
    curr_perp = None
    curr_perp_pnt = None
    curr_empty = False
    for border, pnt, perp, perp_pnt in self.border_iter():
      last_pnt = curr_pnt
      last_perp = curr_perp
      last_perp_pnt = curr_perp_pnt
      last_empty = curr_empty
      curr_pnt = pnt
      curr_perp = perp
      curr_perp_pnt = perp_pnt
      curr_empty = self.get_edge(border) < 0

      if not (last_empty and curr_empty):
        continue

      if not last_perp or self.get_edge(last_perp) >= 0:
        continue

      wall = len(self.wall_size)
      self.wall_size.append(0)
      self.potential_edge_points.append(None)
      self.take_point(last_pnt)
      self.add_potential(wall, last_perp, last_perp_pnt)

  def generate_all_walls(self, same_branch_probability):
    for step in self.gen_each_wall(same_branch_probability):
      pass

  def generate_each_wall(self, same_branch_probability):
    self.initialize_state_from_edges()

    step = 0
    yield step
    step += 1

    more_to_do = True
    while more_to_do:
      more_to_do = False
      for i in xrange(0, self.num_walls()):
        did_something = self.grow_wall(i, same_branch_probability)
        more_to_do = more_to_do or did_something
      yield step
      step += 1

  def num_walls(self):
    return len(self.wall_size)

  def take_point(self, point):
    point_value = self.get_point(point)
    # Clear any potential claims to this point.
    if point_value is not None and isinstance(point_value, set):
      for neighbor_wall, neighbor_edge in point_value:
        del self.potential_edge_points[neighbor_wall][neighbor_edge]
    # Claim the point
    self.set_point(point, Point.TAKEN)

  def grow_wall(self, wall, same_branch_probability=0.0):
    # First check to see if we have a potential extension from the most recent
    # tag.
    edge_population = set()
    pep = self.potential_edge_points[wall]
    if same_branch_probability > random.random():
      tag = self.wall_size[wall]
      for edge in pep:
        if pep[edge][1] == tag:
          edge_population.add(edge)
    # If we either skipped trying to use the most recent tag, or there weren't
    # any potential edges with that tag, fallback on the set of all potential
    # edges.
    if not edge_population:
      edge_population = set(pep.keys())
    if len(edge_population) == 0:
      return False
    new_edge = random.sample(edge_population, 1)[0]
    self.set_edge(new_edge, wall)
    self.wall_size[wall] += 1
    pnt = pep[new_edge][0]
    self.take_point(pnt)
    # Add all new potential edges for this wall.
    for neighbor_edge, neighbor_pnt in self.neighbors_of_point(pnt):
      self.add_potential(wall, neighbor_edge, neighbor_pnt)
    return True

  def print_maze(self):
    for y in xrange(self.height, -1, -1):
      print '  ',
      for x in xrange(0, self.width):
        print ('% 4d' % self.get_edge(Edge(Edge.HORZ, x, y))),
      print ''
      if y > 0:
        for x in xrange(0, self.width+1):
          print ('% 4d' % self.get_edge(Edge(Edge.VERT, x, y-1))),
        print ''

  def create_canvas(self, pixels_per_square, color_list):
    canvas = Canvas(
        width = self.width * pixels_per_square + 1,
        height = self.height * pixels_per_square + 1)
    scale = pixels_per_square

    p0 = np.matrix([0, 0])
    p1 = np.matrix([0, 0])

    for x in xrange(0, self.width):
      p0[0, 0] = x * scale
      p1[0, 0] = (x + 1) * scale

      for y in xrange(0, self.height + 1):
        edge = self.get_edge(Edge(Edge.HORZ, x, y))
        if edge < 0 and edge != Maze.PAINTED:
          continue

        p0[0, 1] = y * scale
        p1[0, 1] = y * scale

        color = (Canvas.COLORS['BLACK']
            if edge == Maze.PAINTED else color_list[edge])
        canvas.draw_line(p0, p1, color)

    for x in xrange(0, self.width + 1):
      p0[0, 0] = x * scale
      p1[0, 0] = x * scale

      for y in xrange(0, self.height):
        edge = self.get_edge(Edge(Edge.VERT, x, y))
        if edge < 0 and edge != Maze.PAINTED:
          continue

        p0[0, 1] = y * scale
        p1[0, 1] = (y + 1) * scale

        color = (Canvas.COLORS['BLACK']
            if edge == Maze.PAINTED else color_list[edge])
        canvas.draw_line(p0, p1, color)

    return canvas

  def check_neighbors(self, unchecked_generator):
    for t in unchecked_generator:
      edge = t
      if isinstance(t, tuple):
        edge = t[0]
      if edge.x < 0 or edge.y < 0:
        continue
      if edge.x >= self.edge_size[edge.ori][0]:
        continue
      if edge.y >= self.edge_size[edge.ori][1]:
        continue
      yield t

  def unchecked_neighbors_of_edge(self, edge):
    if edge.ori == Edge.HORZ:
      yield Edge(Edge.HORZ, edge.x-1, edge.y),   Point(edge.x-1, edge.y)
      yield Edge(Edge.HORZ, edge.x+1, edge.y),   Point(edge.x+2, edge.y)
      yield Edge(Edge.VERT, edge.x,   edge.y),   Point(edge.x,   edge.y+1)
      yield Edge(Edge.VERT, edge.x,   edge.y-1), Point(edge.x,   edge.y-1)
      yield Edge(Edge.VERT, edge.x+1, edge.y),   Point(edge.x+1, edge.y+1)
      yield Edge(Edge.VERT, edge.x+1, edge.y-1), Point(edge.x+1, edge.y-1)
    else:
      yield Edge(Edge.VERT, edge.x,   edge.y-1), Point(edge.x,   edge.y-1)
      yield Edge(Edge.VERT, edge.x,   edge.y+1), Point(edge.x,   edge.y+2)
      yield Edge(Edge.HORZ, edge.x,   edge.y),   Point(edge.x+1, edge.y)
      yield Edge(Edge.HORZ, edge.x-1, edge.y),   Point(edge.x-1, edge.y)
      yield Edge(Edge.HORZ, edge.x,   edge.y+1), Point(edge.x+1, edge.y+1)
      yield Edge(Edge.HORZ, edge.x-1, edge.y+1), Point(edge.x-1, edge.y+1)

  def neighbors_of_edge(self, edge):
    return self.check_neighbors(self.unchecked_neighbors_of_edge(edge))

  def unchecked_neighbors_of_point(self, point):
    yield Edge(Edge.HORZ, point.x-1, point.y),   Point(point.x-1, point.y)
    yield Edge(Edge.HORZ, point.x,   point.y),   Point(point.x+1, point.y)
    yield Edge(Edge.VERT, point.x,   point.y-1), Point(point.x,   point.y-1)
    yield Edge(Edge.VERT, point.x,   point.y),   Point(point.x,   point.y+1)

  def neighbors_of_point(self, point):
    return self.check_neighbors(self.unchecked_neighbors_of_point(point))

  def edge_points(self, edge):
    if edge.ori == Edge.HORZ:
      yield Point(edge.x,   edge.y)
      yield Point(edge.x+1, edge.y)
    else:
      yield Point(edge.x, edge.y)
      yield Point(edge.x, edge.y+1)

  # Iterates south, north, west, east
  def square_edges(self, x, y):
    yield Edge(Edge.HORZ, x, y)
    yield Edge(Edge.HORZ, x, y+1)
    yield Edge(Edge.VERT, x, y)
    yield Edge(Edge.VERT, x+1, y)
