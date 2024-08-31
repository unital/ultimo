"""Utility interpolation functions"""


def linear(x, y, t):
    """Linear interpolation between x and y."""
    return (1-t) * x +  t * y
