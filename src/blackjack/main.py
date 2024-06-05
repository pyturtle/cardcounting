import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from blackjack import display_overlay
from blackjack import evaluate_game_state
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

def split_hand(hands):
    while True:
        result = evaluate_game_state(count, cards_remaining, player_hand, dealer_hand, player_amount, dealer_amount, stood, split=True)
        #TODO when ever the decision is to split, the player should be able to split the hand again by calling itself
        #TODO if the player stands the hand will be saved to the list of hands
        #TODO if the player hits the hand will be saved if he busted, but you need to check if it is the same hand else then you too check above to see the value cause if it is 21 then it auto moves on 
        #TODO if the player doubles down the hand will be saved once you check above 
        #TODO if the player splits again the process will repeat

        #TODO add special stuff for when you have a pair of ten or aces cause you might get a black jack messing up spacing

        #TODO disable the checking for win loss and tie during spliting cause it will mess up the percentages
        if result == "Hit":
            pyautogui.click(hit)
        elif result == "Stand":
            pyautogui.click(stand)
        elif result == "Double Down":
            pyautogui.click(double_down)
        elif result == "Split":
            split_hand(hands)
        sleep(3)

def game_loop():
    sleep(5)
    while game[0]:
        sleep(1)
        previous_count[0] = count[0]
        stood[0] = False
        place_bet(round((count[0]/(cards_remaining[0]/52)) * 100))
        sleep(3)
        while game[0]:
            count[0] = previous_count[0]
            result = evaluate_game_state(count, cards_remaining, player_hand, dealer_hand, player_amount, dealer_amount, stood)
            print(result)
            if result not in ["Playing", "Hit", "Double Down", "Split", "Stand"]:
                # Update win, loss, tie count
                if result == "Win":
                    win_count[0] += 1
                elif result == "Loss":
                    loss_count[0] += 1
                elif result == "Tie":
                    tie_count[0] += 1
                previous_count[0] = count[0]

                # Clear hands
                dealer_hand.clear()
                player_hand.clear()

                # Save previous count to a text file
                with open('cardcounting/src/blackjack/prevcount.txt', 'a') as file:
                    file.write(str(previous_count[0]) + '\n')

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
                # Implement split
                dealer_shown_card = dealer_hand[0]
                previous_count[0] = count[0]
                stood[0] = False                
                hands = []
                # while True:

 
                pyautogui.click(split)
            sleep(3)
        




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
    with open('cardcounting/src/blackjack/prevcount.txt', 'r') as file:
        lines = file.readlines()
        if lines:
            previous_count = [int(lines[-1])]
        else:
            previous_count = [0]
    count = [0]
    stood = [False]
    player_hand = []
    dealer_hand = []
    player_amount = [0]
    dealer_amount = [0]
    cards_remaining = [156]
    game = [True]
    win_count = [0]
    loss_count = [0]
    tie_count = [0]

    threading.Thread(target=game_loop).start()

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    display_overlay(count, cards_remaining, player_hand, dealer_hand, player_amount, dealer_amount, win_count, loss_count, tie_count)
    

    # game_loop()

    listener.join()
