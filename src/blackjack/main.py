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

card_count_values = {
    '2': 1, '3': 1, '4': 1, '5': 1, '6': 1,
    '7': 0, '8': 0, '9': 0,
    '10': -1, 'J': -1, 'Q': -1, 'K': -1, 'A': -1
}

chat = (500, 840)
hit = (520, 715)
stand = (615, 715)
double_down = (750, 715)
split = (855, 715)

def click(pos):
    x, y = pos
    pyautogui.click(x, y)
    pyautogui.click(x, y)

def withdraw(bet_amount, in_game=False):
    amount_withdrawn[0] += bet_amount
    if in_game:
        click(chat)
        pyautogui.typewrite(f"/withdraw {bet_amount}")
        pyautogui.press('enter')
        sleep(1.5)
    else:
        click((280,740))
        sleep(1)
        click(chat)
        pyautogui.typewrite(f"/withdraw {bet_amount}")
        pyautogui.press('enter')
        sleep(0.5)
        click((280,710))
        sleep(3)

def deposit(bet_amount):
    if amount_withdrawn[0] + profit_loss[0] > bet_amount:
        deposit_amount = amount_withdrawn[0] + profit_loss[0] - bet_amount
        amount_withdrawn[0] -= deposit_amount
        click(chat)
        pyautogui.typewrite(f"/deposit {deposit_amount}")
        pyautogui.press('enter')



def place_bet(amount):
    # Save previous count to a text file
    with open('cardcounting/src/blackjack/files/profitLoss.txt', 'a') as file:
        file.write(str(profit_loss[0]) + '\n')

    if amount_withdrawn[0] + profit_loss[0] < amount:
        withdraw(amount, in_game=True)
    print(f"Placing bet {amount}")
    click(chat)
    pyautogui.typewrite(f"/blackjack {amount}")
    pyautogui.press('enter')



def calculate_amount():
    amount = round(count[0]/((cards_remaining[0] if cards_remaining[0] else 156)/52) * 1000)
    if amount < 2000:
        amount = 100
    elif amount > 5000:
        amount = 5000
    if cards_remaining[0] < 3 and count[0] < 2:
        amount = 100
    bet_amount[0] = amount



def split_hand(hands, split_count=2):
    while len(hands) < split_count:

        sleep(2)
        count[0] = previous_count[0]
        result = evaluate_game_state(count, cards_remaining, player_hand, dealer_hand, player_amount, dealer_amount, stood, split=True)

        print(result)
        if result not in ["Hit", "Double Down", "Split", "Stand"]:
            with mss.mss() as sct:
                screenshot = np.array(sct.grab({'top': 505, 'left': 490, 'width': 70, 'height': 30}))
                text = pytesseract.image_to_string(screenshot, config='--psm 6')
                if '1' in text:
                    hands.append("Blackjack")
                    previous_count[0] -= 1
                else:
                    previous_count[0] = count[0]
                    hands.append(player_amount[0])
            continue
        if result == "Hit":
            click(hit)
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
                
                if difference < 7:
                    previous_count[0] += 1
                elif difference > 9:
                    previous_count[0] -= 1    
                hands.append(amount)
                continue

        elif result == "Stand":
            previous_count[0] = count[0]
            hands.append(player_amount[0])
            click(stand)
            continue
        elif result == "Double Down":
            previous_count[0] = count[0]   
            withdraw(bet_amount[len(hands)])
            bet_amount[len(hands)] *= 2
            click(double_down)
            previous = player_amount[0]
            dummy_count = [0]
            result = evaluate_game_state(dummy_count, cards_remaining, player_hand, dealer_hand, player_amount, dealer_amount, stood, split=True)
            if len(player_hand) == 2:
                with mss.mss() as sct:
                    screenshot = np.array(sct.grab({'top': 190, 'left': 490, 'width': 130, 'height': 25}))
                    text = pytesseract.image_to_string(screenshot, config='--psm 6')
                    
   
                amount = list(map(int, re.findall(r'\d+', text)))[0]
                difference = amount - previous
            
                if difference < 7:
                    previous_count[0] += 1
                elif difference > 9:
                    previous_count[0] -= 1    
                hands.append(amount)
                continue    
            else:
                hands.append(player_amount[0])
                continue
        elif result == "Split":
            withdraw(bet_amount[len(hands)])
            bet_amount.append(bet_amount[len(hands)])
            previous_count[0] = count[0]
            click(split)

            # Check if the player has blackjack right after splitting the hand
            with mss.mss() as sct:
                screenshot = sct.grab({'top': 510, 'left': 490, 'width': 70, 'height': 20})
                img = np.array(screenshot)
                text = pytesseract.image_to_string(img, config='--psm 6')
                if str(len(hands) + 2) in text:
                    hands.append("Blackjack")
                    previous_count[0] -= 1

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
    sleep(10)
    while game[0]:
        previous_count[0] = count[0]
        stood[0] = False
        calculate_amount()
        deposit(bet_amount[0])
        sleep(17)
        place_bet(bet_amount[0])
        sleep(2)
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
                click(hit)
            elif result == "Stand":
                stood[0] = True
                click(stand)
            elif result == "Double Down":
                stood[0] = True
                withdraw(bet_amount[0])
                click(double_down)
                bet_amount[0] = bet_amount[0] * 2
            elif result == "Split":
                if player_hand == ['A', 'A']:
                    print("Splitting Aces")
                # Implement split
                withdraw(bet_amount[0])
                previous_count[0] = count[0]   
                bet_amount.append(bet_amount[0])      
                click(split)
                sleep(2)
                hands = []
                with mss.mss() as sct:
                    screenshot = sct.grab({'top': 505, 'left': 490, 'width': 70, 'height': 30})
                    img = np.array(screenshot)
                    text = pytesseract.image_to_string(img, config='--psm 6')
                    if str(len(hands) + 2) in text:
                        hands.append("Blackjack")
                        previous_count[0] -= 1

                hands = split_hand(hands)
                print(hands)
                evaluate_game_state(count, cards_remaining, player_hand, dealer_hand, player_amount, dealer_amount, stood, split=True)
                for card in dealer_hand[1:]:
                    previous_count[0] += card_count_values[card]  
                count[0] = previous_count[0]
                for i, hand in enumerate(hands):
                    if hand == "Blackjack" and dealer_amount[0] != "Blackjack":
                        print("Win")
                        win_count[0] += 1
                        profit_loss[0] += bet_amount[i] + round(bet_amount[i] / 2 - 0.1)
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

            sleep(1)
        

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
    previous_count = [-1]
    count = [previous_count[0]]
    stood = [False]
    player_hand = []
    dealer_hand = []
    player_amount = [0]
    dealer_amount = [0]
    cards_remaining = [0]
    game = [True]
    win_count = [0]
    loss_count = [0]
    tie_count = [0]

    threading.Thread(target=game_loop).start()

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    display_overlay(count, cards_remaining, player_hand, dealer_hand, player_amount, dealer_amount, win_count, loss_count, tie_count, bet_amount, profit_loss, amount_withdrawn)

    listener.join()
