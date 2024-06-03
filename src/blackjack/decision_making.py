import cv2
import mss
import pytesseract
import numpy as np

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


def make_decision(count, cards_remaining, player_hand, dealer_hand, player_amount, dealer_amount, stood):
        with mss.mss() as sct:
            cards_img = np.array(sct.grab(cards_region))
            preprocessed_img = preprocess_image(cards_img)
            final_img = extract_cards(preprocessed_img)

            config = '--psm 6 -c tessedit_char_whitelist=0123456789JQKA'
            card_text = pytesseract.image_to_string(final_img, config=config)

            player_dealer_img = np.array(sct.grab(player_dealer_count_region))
            player_dealer_text = pytesseract.image_to_string(player_dealer_img, config='--psm 6 -c tessedit_char_whitelist=0123456789')

            cards_remaining_img = np.array(sct.grab(cards_remaining_region))
            cards_remaining_text = pytesseract.image_to_string(cards_remaining_img, config='--psm 6 -c tessedit_char_whitelist=0123456789')

        
        # Calculate the running count
        cards = card_text.replace("\n", "").split(" ")
        for card in cards:
            if card in card_count_values:
                count[0] += card_count_values[card]

        print(cards)
        
        true_count = count[0] / 3
        player_amount[0], dealer_amount[0] = tuple(map(int, player_dealer_text.split(" ")))
        cards_remaining[0] = int(cards_remaining_text)

        running_count = 0
        for card in cards:
            if running_count < player_amount[0]:
                running_count += card_values[card]
                player_hand.append(card)
            else:
                break
         
        for card in cards[len(player_hand):]:
            dealer_hand.append(card)
        print(dealer_hand)

            











def check_win_loss():
    # Placeholder for win/loss logic
    # This should be replaced with actual game state checking
    return np.random.choice(["Win", "Loss"])
