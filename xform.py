import numpy as np

def identity():
  return np.matrix([[1., 0., 0.],
                    [0., 1., 0.],
                    [0., 0., 1.]])

def rotate(clockwise):
  if clockwise:
    return np.matrix([[ 0., -1.,  0.],
                      [ 1.,  0.,  0.],
                      [ 0.,  0.,  1.]])
  else:
    return np.matrix([[ 0.,  1.,  0.],
                      [-1.,  0.,  0.],
                      [ 0.,  0.,  1.]])

def scale(x, y):
  return np.matrix([[ x, 0., 0.],
                    [0.,  y, 0.],
                    [0., 0., 1.]])

def translate(x, y):
  return np.matrix([[1., 0., 0.],
                    [0., 1., 0.],
                    [ x,  y, 1.]])
