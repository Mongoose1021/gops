#!/usr/bin/env python

# Ignore the prizes and play cards in a random order.

import random, sys
cards = range(1, 14)

# ignore game setup info
sys.stdin.readline()

while True:
  # ignore prize
  sys.stdin.readline()
  card = random.choice(cards)
  cards.remove(card)
  print card
  sys.stdout.flush()
  # ignore plays
  sys.stdin.readline()