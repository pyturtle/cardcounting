import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from blackjack import update_count, display_overlay
from blackjack import make_decision, check_win_loss
from blackjack import place_bet
from pynput import keyboard



def game_loop():
    while True:
        place_bet(10)
        update_count()
        # decision = make_decision()
        result = check_win_loss()
        print(f"Result: {result}")
        if result == "Win" or result == "Loss":
            break

def on_press(key):
    try:
        if key.char == 'p':
            make_decision(count,cards_remaining,player_hand,dealer_hand)
    except AttributeError:
        pass

if __name__ == "__main__":
    count = [0]
    player_hand = []
    dealer_hand = []
    cards_remaining = [0]


    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    display_overlay(count, cards_remaining)

    print ("Game Loop")
    # game_loop()

    listener.join()
