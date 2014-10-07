from __future__ import absolute_import
import os, random, copy, operator
import logging
from argparse import ArgumentParser
from subprocess import Popen, PIPE, STDOUT

max_card = 14
split_wins = True

player_dir = os.path.join(os.getcwd(), 'strats')

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter())
logger.addHandler(handler)

def cleanup_processes(process_dict):
  """Remove terminated players from a list of active processes"""
  for p in process_dict.values():
    p.poll()
  return {id: process for id, process in process_dict.iteritems() if process.returncode == None}

def tell_player(id, process, message, disqualified):
  """Attempt to send a player a message. If something goes wrong, DQ them."""
  try:
    logger.debug("Sending message %s to player %d", message, id)
    process.stdin.write(message)
    process.stdin.flush()
  except:
    logger.info("Error communicating with player %d - disqualified.", id)
    process.kill()
    disqualified.add(id)

def play(players):
  """Run n Python players representing GOPS strategies against each other."""
  player_ids = {id: player for id, player in enumerate(players)}
  # Shuffle the prize deck
  prizes = range(1, max_card)
  random.shuffle(prizes)
  # Get everyone's victory pile ready...
  won_prizes = {id: [] for id in player_ids}
  # Start all participants
  process_dict = {id: Popen(os.path.join(player_dir, player_ids[id]), stdin=PIPE, stdout=PIPE, stderr=STDOUT) for id in player_ids}
  # Presumably no one has screwed up yet...
  disqualified = set()
  # and everyone still owns all their cards to play
  legal_plays = {id: set(range(1, max_card)) for id in player_ids}
  
  # Share initial information with the players.
  # Each process gets a single newline-terminated line of two numbers separated by a space.
  # First number is that player's ID, zero-indexed. Second number is the # of players in game.
  # This is important if you want to write a strategy that keeps track of others' cards.
  for id, process in process_dict.iteritems():
    tell_player(id, process, '%d %d\n' % (id, len(player_ids)), disqualified)    
  # Anyone who crashed on that news (or on startup) was disqualified -- get rid of them.
  process_dict = cleanup_processes(process_dict)
  
  # Run all rounds
  for i, prize in enumerate(prizes):
    logger.info("Beginning round %d (prize = %d).", i, prize)
    
    # 1. Tell everyone what card is available
    for id, process in process_dict.iteritems():
      tell_player(id, process, '%d\n' % prize, disqualified)
    # Clean up anyone crashed or disqualified
    process_dict = cleanup_processes(process_dict)
    
    # 2: See what everyone wants to play
    plays = {}
    for id, process in process_dict.iteritems():
      try:
        play = int(process.stdout.readline().strip())
        if play not in legal_plays[id]:
          logger.info("Illegal card (%d) played.", play)
          raise ValueError
        legal_plays[id].remove(play)
        plays[id] = play
      except:
        logger.info("Illegal play by player %d (%s) - disqualified", id, player_ids[id])
        process.kill()
        disqualified.add(id)
    # Clean up anyone crashed or disqualified
    process_dict = cleanup_processes(process_dict)
    
    # 3: Figure out who won and award points
    if not process_dict or not plays:  # ... assuming that *anyone* won.
      continue
    winning_play = max(plays.values())
    logger.info("Winning play was %d.", winning_play)
    winners = [id for id in plays if plays[id] == winning_play]
    logger.info("Winning player(s): %s", ','.join([str(w) for w in winners]))
    logger.info("Each winning player gets %4.2f", prize / len(winners))
    for winner in winners:
      won_prizes[winner].append(prize / len(winners))
      
    # 4: Inform players of the results of the round.
    # The results consist of a single newline-terminated string. The whitespace-separated
    # values are the card played by each player, in ID order. If a player has been
    # disqualified in or during this round, a '-' character replaces the card number.
    cards_played = ' '.join([str(plays.get(id, '-')) for id in range(len(players))])
    for id, process in process_dict.iteritems():
      tell_player(id, process, cards_played + '\n', disqualified)
    # ugly housekeeping
    process_dict = cleanup_processes(process_dict)
    
  # Rounds complete; determine scores.
  scores = [(sum(wins), id, player_ids[id]) for id, wins in won_prizes.iteritems()]
  scores.sort(reverse=True)
  logger.info('Game Complete')
  logger.info('Score   Player ID    Player')
  logger.info('-' * 30)
  for score in scores:
    logger.info('%4.02f   %9d    %s' % score)
  return [sum(won_prizes[id]) for id in range(len(player_ids))]
  
def update_elo(winner_old_rating, loser_old_rating, k=32, draw=False):
  winner_ev = 1.0 / (1.0 + 10**((loser_old_rating - winner_old_rating)/400.0))
  loser_ev = 1.0 - winner_ev
  if not draw:
    return winner_old_rating + k * (1.0 - winner_ev), loser_old_rating - k * (loser_ev) 
  else:
    return winner_old_rating + k * (0.5 - winner_ev), loser_old_rating + k * (0.5 - loser_ev)
    
def get_contestants(
  
def main():
  argp = ArgumentParser()
  argp.add_argument("-v", "--verbose", action="store_true")
  argp.add_argument("-q", "--quiet", action="store_true", help="abuse features for easy print change for now")
  cfg = argp.parse_args()
  if cfg.verbose:
    logger.setLevel(logging.DEBUG)
  else:
    logger.setLevel(logging.INFO)
  if cfg.quiet:
    logger.setLevel(logging.WARNING)
  play(["random_strat.py", "simple_strat.py"])

if __name__=="__main__":
  main()