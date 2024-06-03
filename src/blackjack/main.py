import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from blackjack import display_overlay
from blackjack import make_decision
from blackjack import place_bet
from pynput import keyboard



def game_loop():
    while True:
        place_bet(10)
        decision = make_decision()


def on_press(key):
    try:
        if key.char == 'p':
            count[0] = previous_count[0]
            result = make_decision(count, cards_remaining, player_hand, dealer_hand, player_amount, dealer_amount, stood)
            print(result)
            if result != "Playing":
                previous_count[0] = count[0]
        if key.char == 's':
            stood[0] = True
            result = make_decision(count, cards_remaining, player_hand, dealer_hand, player_amount, dealer_amount, stood)
            print(result)
            previous_count[0] = count[0]
            stood[0] = False
    except AttributeError:
        pass

if __name__ == "__main__":
    previous_count = [0]
    count = [0]
    stood = [False]
    player_hand = []
    dealer_hand = []
    player_amount = [0]
    dealer_amount = [0]
    cards_remaining = [0]


    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    display_overlay(count, cards_remaining, player_hand, dealer_hand, player_amount, dealer_amount)

    print ("Game Loop")
    # game_loop()

    listener.join()
