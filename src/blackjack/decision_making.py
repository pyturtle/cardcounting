import cv2
import mss
import pytesseract
import numpy as np
import re

card_count_values = {
    '2': 1, '3': 1, '4': 1, '5': 1, '6': 1,
    '7': 0, '8': 0, '9': 0,
    '10': -1, 'J': -1, 'Q': -1, 'K': -1, 'A': -1
}

card_values = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
    '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10, 'A': [1, 11]
}


cards_region = {'top': 500, 'left': 495, 'width': 600, 'height': 32}
player_dealer_count_region = {'top': 615, 'left': 490, 'width': 300, 'height': 30}
cards_remaining_region = {'top': 640, 'left': 490, 'width': 200, 'height': 35}
overlay_text = ""
update_flag = False


def preprocess_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    inverted = cv2.bitwise_not(thresh)
    black_bar = np.zeros((35, inverted.shape[1]), dtype=np.uint8)
    inverted_with_black_bar = np.vstack((inverted, black_bar))
    return inverted_with_black_bar


def extract_cards(preprocessed_img):
    contours, _ = cv2.findContours(preprocessed_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    white_background = np.ones((preprocessed_img.shape[0], preprocessed_img.shape[1], 3), dtype=np.uint8) * 255

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        card_region = preprocessed_img[y:y+h, x:x+w]
        white_background[y:y+h, x:x+w] = cv2.cvtColor(card_region, cv2.COLOR_GRAY2BGR)

    return white_background

def check_win_loss_tie(player_amount, dealer_amount, stood):
    if player_amount[0] > 21:
        return "Loss"
    elif dealer_amount[0] > 21:
        return "Win"
    elif stood[0]:
        if player_amount[0] > dealer_amount[0]:
            return "Win"
        elif player_amount[0] < dealer_amount[0]:
            return "Loss"
        else:
            return "Tie"
    elif player_amount[0] == 21:
        if player_amount[0] > dealer_amount[0]:
            return "Win"
        else:
            return "Tie"
    elif dealer_amount[0] == 21 and stood[0] == False:
        return "Loss"
    else:
        return "Playing"

def make_decision(count, cards_remaining, player_hand, dealer_hand, player_amount, dealer_amount, stood):
        with mss.mss() as sct:
            cards_img = np.array(sct.grab(cards_region))
            preprocessed_img = preprocess_image(cards_img)
            final_img = extract_cards(preprocessed_img)

            config = '--psm 6 -c tessedit_char_whitelist=0123456789JQKA'
            card_text = pytesseract.image_to_string(final_img, config=config)

            player_dealer_img = np.array(sct.grab(player_dealer_count_region))
            player_dealer_text = pytesseract.image_to_string(player_dealer_img, config='--psm 6')

            cards_remaining_img = np.array(sct.grab(cards_remaining_region))
            cards_remaining_text = pytesseract.image_to_string(cards_remaining_img, config='--psm 6 -c tessedit_char_whitelist=0123456789')

        
        # Calculate the running count
        cards = card_text.replace("\n", "").split(" ")
        print(cards)

        for card in cards:
            if card in card_count_values:
                count[0] += card_count_values[card]


        true_count = count[0] / 3
        
        if "Blackjack" in player_dealer_text:
            if player_dealer_text.count("Blackjack") == 2:
                return "Tie"
            if "Blackjack" in player_dealer_text.split("V")[1]:
                return "Win"
            else:
                return "Loss"
            
        player_amount[0], dealer_amount[0] =list(map(int, re.findall(r'\d+', player_dealer_text)))
        cards_remaining[0] = int(cards_remaining_text)

        #Figure out the player's hand and the dealer's hand
        player_hand.clear()
        dealer_hand.clear()
        ace_count = 0
        running_count = 0
        for card in cards:
            print(running_count, player_amount[0], card_values[card], card)
            if running_count < player_amount[0]:
                if card == 'A':
                    if running_count + card_values[card][1] <= player_amount[0]:
                        ace_count += 1
                        running_count += card_values[card][1]
                        player_hand.append(card)
                    elif running_count + card_values[card][0] <= player_amount[0]:
                        running_count += card_values[card][0]
                        player_hand.append(card)
                else:
                    if ((running_count + card_values[card]) > (player_amount[0])) & ace_count > 0:
                        ace_count -= 1
                        running_count += card_values[card]
                        running_count -= 10
                        player_hand.append(card)
                    elif running_count + card_values[card] <= player_amount[0]:
                        running_count += card_values[card]
                        player_hand.append(card)
            else:
                break
         
        for card in cards[len(player_hand):]:
            dealer_hand.append(card)


        result = check_win_loss_tie(player_amount, dealer_amount, stood)

        # if result != "Playing":
        #     return result
        return result
        

            










