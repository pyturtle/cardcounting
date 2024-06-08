import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from blackjack import display_overlay
from blackjack import evaluate_game_state
from pynput import keyboard
from time import sleep
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

def withdraw(amount):
    pyautogui.click(chat)
    pyautogui.typewrite(f"/withdraw {amount}")
    pyautogui.press('enter')

def deposit(amount):
    pyautogui.click(chat)
    pyautogui.typewrite(f"/deposit {amount}")
    pyautogui.press('enter')

def place_bet(amount):
    if amount < 100:
        amount = 100
    elif amount > 1000:
        amount = 1000
    bet_amount[0] = amount

    if amount_withdrawn[0] + profit_loss[0] > amount * 4:
        deposit_amount = amount_withdrawn[0] + profit_loss[0] - amount * 4
        deposit(deposit_amount)
        amount_withdrawn[0] -= deposit_amount
        sleep(3)


    if amount_withdrawn[0] + profit_loss[0] < amount * 4:
        withdraw(amount * 4)
        amount_withdrawn[0] += amount * 4
        sleep(3)

    pyautogui.click(chat)
    pyautogui.typewrite(f"/blackjack {amount}")
    pyautogui.press('enter')
    
    sleep(1)
def split_hand(hands, split_count=2):
    while len(hands) < split_count:
        count[0] = previous_count[0]
        result = evaluate_game_state(count, cards_remaining, player_hand, dealer_hand, player_amount, dealer_amount, stood, split=True)
        if result not in ["Hit", "Double Down", "Split", "Stand"]:
            previous_count[0] = count[0]
            hands.append(player_amount[0])
            continue
        if result == "Hit":
            pyautogui.click(hit)
            previous = player_amount[0]
            dummy_count = [0]
            result = evaluate_game_state(dummy_count, cards_remaining, player_hand, dealer_hand, player_amount, dealer_amount, stood, split=True)
            if len(player_hand) == 2:
                previous_count[0] = count[0]
                with mss.mss() as sct:
                    screenshot = sct.grab({'top': 190, 'left': 490, 'width': 130, 'height': 25})
                    img = np.array(screenshot)
                    text = pytesseract.image_to_string(img, config='--psm 6')
                
                    amount = list(map(int, re.findall(r'\d+', text)))[0]
                    difference = amount - previous
                
                if difference < 6:
                    previous_count[0] += 1
                elif difference > 9:
                    previous_count[0] -= 1    
                hands.append(amount)
                continue

        elif result == "Stand":
            previous_count[0] = count[0]
            hands.append(player_amount[0])
            pyautogui.click(stand)
            continue
        elif result == "Double Down":
            previous_count[0] = count[0]   
            bet_amount[len(hands)] *= 2
            pyautogui.click(double_down)
            previous = player_amount[0]
            dummy_count = [0]
            result = evaluate_game_state(dummy_count, cards_remaining, player_hand, dealer_hand, player_amount, dealer_amount, stood, split=True)
            if len(player_hand) == 2:
                with mss.mss() as sct:
                    screenshot = np.array(sct.grab({'top': 190, 'left': 490, 'width': 130, 'height': 25}))
                    text = pytesseract.image_to_string(screenshot, config='--psm 6')
                    
   
                amount = list(map(int, re.findall(r'\d+', text)))[0]
                difference = amount - previous
            
                if difference < 6:
                    previous_count[0] += 1
                elif difference > 9:
                    previous_count[0] -= 1    
                hands.append(amount)
                continue    
            else:
                hands.append(player_amount[0])
                continue
        elif result == "Split":
            bet_amount.append(bet_amount[len(hands)])
            previous_count[0] = count[0]
            pyautogui.click(split)

            # Check if the player has blackjack right after splitting the hand
            with mss.mss() as sct:
                screenshot = sct.grab({'top': 510, 'left': 490, 'width': 70, 'height': 20})
                img = np.array(screenshot)
                text = pytesseract.image_to_string(img, config='--psm 6')
                if str(len(hands) + 2) in text:
                    hands.append("Blackjack")
                    previous_count[0] += 1

            split_count += 1

    return hands   

def game_loop():
    """
    Function to run the game loop.

    This function controls the flow of the game, including placing bets, evaluating game states,
    and updating win/loss/tie counts. It also handles actions like hitting, standing, doubling down,
    and splitting hands.

    Returns:
        None
    """
    sleep(2)
    while game[0]:
        previous_count[0] = count[0]
        stood[0] = False
        place_bet(round((count[0]/((cards_remaining[0] if cards_remaining[0] else 156)/52)) * 75))
        while game[0]:
            count[0] = previous_count[0]
            result = evaluate_game_state(count, cards_remaining, player_hand, dealer_hand, player_amount, dealer_amount, stood)
            print(result)
            if result not in ["Hit", "Double Down", "Split", "Stand"]:
                # Update win, loss, tie count
                if result == "Win":
                    win_count[0] += 1
                    profit_loss[0] += bet_amount[0]
                    if player_amount[0] == "Blackjack":
                        profit_loss[0] += bet_amount[0] / 2
                    bet_amount[0] = 0
                elif result == "Loss":
                    loss_count[0] += 1
                    profit_loss[0] -= bet_amount[0]
                    bet_amount[0] = 0
                elif result == "Tie":
                    tie_count[0] += 1
                    bet_amount[0] = 0
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
                bet_amount[0] = bet_amount[0] * 2
            elif result == "Split":
                # Implement split
                previous_count[0] = count[0]   
                bet_amount.append(bet_amount[0])         
                pyautogui.click(split)
                sleep(2)
                hands = []

                with mss.mss() as sct:
                    screenshot = sct.grab({'top': 510, 'left': 490, 'width': 70, 'height': 20})
                    img = np.array(screenshot)
                    text = pytesseract.image_to_string(img, config='--psm 6')
                    if str(len(hands) + 2) in text:
                        hands.append("Blackjack")
                        previous_count[0] += 1

                
                hands = split_hand(hands)
                print(hands)
                evaluate_game_state(count, cards_remaining, player_hand, dealer_hand, player_amount, dealer_amount, stood, split=True)
                for i, hand in enumerate(hands):
                    if hand == "Blackjack" and dealer_amount[0] != "Blackjack":
                        print("Win")
                        win_count[0] += 1
                        profit_loss[0] += bet_amount[i] + bet_amount[i] / 2
                    elif hand != "Blackjack" and dealer_amount[0] == "Blackjack":
                        print("Loss")
                        loss_count[0] += 1
                        profit_loss[0] -= bet_amount[i]
                    elif hand == "Blackjack" and dealer_amount[0] == "Blackjack":
                        print("Tie")
                        tie_count[0] += 1
                    elif hand > 21:
                        print("Loss")
                        loss_count[0] += 1
                        profit_loss[0] -= bet_amount[i]
                    elif dealer_amount[0] > 21:
                        print("Win")
                        win_count[0] += 1
                        profit_loss[0] += bet_amount[i]
                    elif hand > dealer_amount[0]:
                        print("Win")
                        win_count[0] += 1
                        profit_loss[0] += bet_amount[i]
                    elif hand < dealer_amount[0]:
                        print("Loss")
                        loss_count[0] += 1
                        profit_loss[0] -= bet_amount[i]
                    elif hand == dealer_amount[0]:
                        print("Tie")
                        tie_count[0] += 1
                bet_amount[0] = 0
                del bet_amount[1:]
                break

            sleep(2)
        

def on_press(key):
    try:
        if key.char == 'n':
            count[0] = previous_count[0]
            result = evaluate_game_state(count, cards_remaining, player_hand, dealer_hand, player_amount, dealer_amount, stood)
            print(result)
            if result not in ["Playing", "Hit", "Double Down", "Split", "Stand"]:
                previous_count[0] = count[0]
        if key.char == 'm':
            game[0] = not game[0]

    except AttributeError:
        pass



if __name__ == "__main__":

    with open('cardcounting/src/blackjack/files/prevcount.txt', 'w') as file:
        file.write('')

    profit_loss = [0]
    bet_amount = [0]
    amount_withdrawn = [0]
    previous_count = [0]
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

    display_overlay(count, cards_remaining, player_hand, dealer_hand, player_amount, dealer_amount, win_count, loss_count, tie_count, bet_amount, profit_loss, amount_withdrawn)

    listener.join()
