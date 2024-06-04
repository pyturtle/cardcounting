import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from blackjack import display_overlay
from blackjack import evaluate_game_state
from blackjack import place_bet
from pynput import keyboard
from time import sleep
import threading
import pyautogui

chat = (500, 840)
hit = (520, 715)
stand = (615, 715)
double_down = (750, 715)
split = (855, 715)

def place_bet(amount):
    if amount < 100:
        amount = 100
    print(f"Placing a bet of {amount}")
    pyautogui.click(chat)
    pyautogui.typewrite(f"/blackjack {amount}", interval=0.1)
    pyautogui.press('enter')


def game_loop():
    sleep(5)
    while game[0]:
        sleep(0.5)
        previous_count[0] = count[0]
        stood[0] = False
        place_bet(round((count[0]/(cards_remaining[0]/52)) * 100))
        sleep(3)
        while game[0]:
            count[0] = previous_count[0]
            result = evaluate_game_state(count, cards_remaining, player_hand, dealer_hand, player_amount, dealer_amount, stood)
            print(result)
            if result not in ["Playing", "Hit", "Double Down", "Split", "Stand"]:
                break
            if result == "Hit":
                pyautogui.click(hit)
            elif result == "Stand":
                stood[0] = True
                pyautogui.click(stand)
            elif result == "Double Down":
                stood[0] = True
                pyautogui.click(double_down)
            elif result == "Split":
                pyautogui.click(split)
            sleep(2)
        




def on_press(key):
    try:
        if key.char == 'p':
            count[0] = previous_count[0]
            result = evaluate_game_state(count, cards_remaining, player_hand, dealer_hand, player_amount, dealer_amount, stood)
            print(result)
            if result not in ["Playing", "Hit", "Double Down", "Split", "Stand"]:
                previous_count[0] = count[0]
        if key.char == 's':
            stood[0] = True
            result = evaluate_game_state(count, cards_remaining, player_hand, dealer_hand, player_amount, dealer_amount, stood)
            print(result)
            previous_count[0] = count[0]
            stood[0] = False
        if key.char == 'h':
            game[0] = not game[0]

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
    cards_remaining = [156]
    game = [True]

    threading.Thread(target=game_loop).start()

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    display_overlay(count, cards_remaining, player_hand, dealer_hand, player_amount, dealer_amount)
    

    # game_loop()

    listener.join()
