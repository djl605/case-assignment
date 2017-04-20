import sys


def debug(*args):
  print(*args, file=sys.stderr)
