#!/usr/bin/env python

# Simple GOPS strategy.
# Plays the card 1 higher than the prize, if possible -- plays a 1 on the 13.

import sys

class GopsStrategy(object):
  def __init__(self):
    pass
    
  def setup(self, my_id, total_players):
    """Put setup code that should be run at the beginning here."""
    self.my_id = my_id
    self.total_players = total_players
    self.game_log = {id: [] for id in range(total_players)}
    self.remaining_cards = set(range(1, 14))
  
  def play_card(self, prize):
    """Decides a bid to make this round. Prize is the card up for grabs."""
    if prize + 1 in self.remaining_cards:
      self.remaining_cards.remove(prize + 1)
      return prize + 1
    else:
      self.remaining_cards.remove(1)
      return 1
    
  def store_results(self, results):
    """Store cards played in previous rounds."""
    for id, play in enumerate(results):
      self.game_log[id].append(play)

if __name__ == "__main__":
  strategy = GopsStrategy()
  game_info = sys.stdin.readline().split()
  my_id = int(game_info[0])
  total_players = int(game_info[1])
  strategy.setup(my_id, total_players)
  while True:
    prize = int(sys.stdin.readline().strip())
    card = strategy.play_card(prize)
    print card
    sys.stdout.flush()
    results = sys.stdin.readline().split()
    strategy.store_results(results)