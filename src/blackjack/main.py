import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from blackjack import display_overlay
from blackjack import evaluate_game_state
from pynput import keyboard
from time import sleep
import easyocr
import threading
import pyautogui
import mss
import pytesseract
import numpy as np
import re


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

def split_hand(hands, split_count=2):
    while len(hands) < split_count:
        count[0] = previous_count[0]
        result = evaluate_game_state(reader, count, cards_remaining, player_hand, dealer_hand, player_amount, dealer_amount, stood, split=True)
        #TODO when ever the decision is to split, the player should be able to split the hand again by calling itself
        #TODO if the player stands the hand will be saved to the list of hands
        #TODO if the player hits the hand will be saved if he busted, but you need to check if it is the same hand else then you too check above to see the value cause if it is 21 then it auto moves on 
        #TODO if the player doubles down the hand will be saved once you check above 
        #TODO if the player splits again the process will repeat

        #TODO add special stuff for when you have a pair of ten or aces cause you might get a black jack messing up spacing

        #TODO disable the checking for win loss and tie during spiting cause it will mess up the percentages
        if result not in ["Hit", "Double Down", "Split", "Stand"]:
            previous_count[0] = count[0]
            hands.append(player_amount[0])
            break
        if result == "Hit":
            pyautogui.click(hit)
            previous = player_amount[0]
            dummy_count = [0]
            result = evaluate_game_state(reader, dummy_count, cards_remaining, player_hand, dealer_hand, player_amount, dealer_amount, stood, split=True)
            if len(player_hand) == 2:
                previous_count[0] = count[0]
                with mss.mss() as sct:
                    screenshot = sct.grab({'top': 185, 'left': 490, 'width': 50, 'height': 25})
                    img = np.array(screenshot)
                    text = pytesseract.image_to_string(img, config='--psm 6')
                
                if "Blackjack" in text:
                    previous_count[0] -= 1
                    hands.append("Blackjack")
                    break
                else:
                    amount = list(map(int, re.findall(r'\d+', text)))[0]
                    difference = amount - previous
                
                if difference < 6:
                    previous_count[0] += 1
                elif difference > 9:
                    previous_count[0] -= 1    
                hands.append(amount)
                break

        elif result == "Stand":
            previous_count[0] = count[0]
            hands.append(player_amount[0])
            pyautogui.click(stand)
            break
        elif result == "Double Down":
            previous_count[0] = count[0]   
            pyautogui.click(double_down)
            previous = player_amount[0]
            dummy_count = [0]
            result = evaluate_game_state(reader ,dummy_count, cards_remaining, player_hand, dealer_hand, player_amount, dealer_amount, stood, split=True)
            if len(player_hand) == 2:
                with mss.mss() as sct:
                    screenshot = sct.grab({'top': 190, 'left': 490, 'width': 50, 'height': 25})
                    img = np.array(screenshot)
                    text = pytesseract.image_to_string(img, config='--psm 6')
                    
                if "Blackjack" in text:
                    previous_count[0] -= 1
                    hands.append("Blackjack")
                    break
                else:
                    amount = list(map(int, re.findall(r'\d+', text)))[0]
                    difference = amount - previous
                
                if difference < 6:
                    previous_count[0] += 1
                elif difference > 9:
                    previous_count[0] -= 1    
                hands.append(amount)
                hands.append(player_amount[0])
                break    
            
        elif result == "Split":
            previous_count[0] = count[0]
            pyautogui.click(split)
            split_hand(hands, split_count +  1)

            
    split_hand(hands, split_count)

def game_loop():
    sleep(5)
    while game[0]:
        sleep(2)
        previous_count[0] = count[0]
        stood[0] = False
        place_bet(round((count[0]/(cards_remaining[0]/52)) * 100))
        sleep(2)
        while game[0]:
            count[0] = previous_count[0]
            result = evaluate_game_state(reader ,count, cards_remaining, player_hand, dealer_hand, player_amount, dealer_amount, stood)
            print(result)
            if result not in ["Hit", "Double Down", "Split", "Stand"]:
                # Update win, loss, tie count
                if result == "Win":
                    win_count[0] += 1
                elif result == "Loss":
                    loss_count[0] += 1
                elif result == "Tie":
                    tie_count[0] += 1
                previous_count[0] = count[0]

                # Save previous count to a text file
                with open('cardcounting/src/blackjack/files/prevcount.txt', 'a') as file:
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
                previous_count[0] = count[0]            
                hands = []
                pyautogui.click(split)
                split_hand(hands)
                print(hands)
                evaluate_game_state(reader, count, cards_remaining, player_hand, dealer_hand, player_amount, dealer_amount, stood, split=True)
                for hand in hands:
                    if hand == "Blackjack" and dealer_amount != "Blackjack":
                        print("Win")
                        win_count[0] += 1
                    elif hand != "Blackjack" and dealer_amount == "Blackjack":
                        print("Loss")
                        loss_count[0] += 1
                    elif hand == "Blackjack" and dealer_amount == "Blackjack":
                        print("Tie")
                        tie_count[0] += 1
                    elif hand > 21:
                        print("Loss")
                        loss_count[0] += 1
                    elif dealer_amount > 21:
                        print("Win")
                        win_count[0] += 1
                    elif hand > dealer_amount:
                        print("Win")
                        win_count[0] += 1
                    elif hand < dealer_amount:
                        print("Loss")
                        loss_count[0] += 1
                    elif hand == dealer_amount:
                        print("Tie")
                        tie_count[0] += 1
                break

            # Clear hands
            dealer_hand.clear()
            player_hand.clear()

            sleep(2)
        

def on_press(key):
    try:
        if key.char == 'p':
            count[0] = previous_count[0]
            result = evaluate_game_state(reader, count, cards_remaining, player_hand, dealer_hand, player_amount, dealer_amount, stood)
            print(result)
            if result not in ["Playing", "Hit", "Double Down", "Split", "Stand"]:
                previous_count[0] = count[0]
        if key.char == 's':
            stood[0] = True
            result = evaluate_game_state(reader, count, cards_remaining, player_hand, dealer_hand, player_amount, dealer_amount, stood)
            print(result)
            previous_count[0] = count[0]
            stood[0] = False
        if key.char == 'h':
            game[0] = not game[0]

    except AttributeError:
        pass



if __name__ == "__main__":
    with open('cardcounting/src/blackjack/files/prevcount.txt', 'r') as file:
        lines = file.readlines()
        if lines:
            previous_count = [int(lines[-1])]
        else:
            previous_count = [0]
    reader = easyocr.Reader(['en'])
    count = [previous_count[0]]
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

    listener.join()
