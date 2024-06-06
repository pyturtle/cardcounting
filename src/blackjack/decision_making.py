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
    'J': 10, 'Q': 10, 'K': 10, 'A': 11
}


cards_region = {'top': 535, 'left': 495, 'width': 900, 'height': 28}
player_dealer_count_region = {'top': 615, 'left': 490, 'width': 900, 'height': 30}
cards_remaining_region = {'top': 640, 'left': 490, 'width': 200, 'height': 35}



def preprocess_image(img):
    """
    Preprocesses an image by converting it to grayscale, applying a binary inverse threshold,
    inverting the colors, and adding a black bar at the bottom.

    Args:
        img (numpy.ndarray): The input image.

    Returns:
        numpy.ndarray: The preprocessed image.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    inverted = cv2.bitwise_not(thresh)
    black_bar = np.zeros((30, inverted.shape[1]), dtype=np.uint8)
    inverted_with_black_bar = np.vstack((black_bar, inverted, black_bar))
    return inverted_with_black_bar

def extract_cards(preprocessed_img, spacing):
    """
    Extracts individual cards from a preprocessed image and arranges them horizontally with a specified spacing.

    Args:
        preprocessed_img (numpy.ndarray): The preprocessed image containing the cards.
        spacing (int): The spacing between the extracted cards.

    Returns:
        numpy.ndarray: The image with the extracted cards arranged horizontally.

    """
    contours, _ = cv2.findContours(preprocessed_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    bounding_boxes = [cv2.boundingRect(cnt) for cnt in contours]

    bounding_boxes = sorted(bounding_boxes, key=lambda x: x[0])
    
    bounding_boxes.append(bounding_boxes[-1])
    bounding_boxes.append(bounding_boxes[1])

    total_width = sum(bbox[2] for bbox in bounding_boxes) + spacing * (len(bounding_boxes) - 1)
    
    original_width = preprocessed_img.shape[1]
    if total_width > original_width:
        spacing = (original_width - sum(bbox[2] for bbox in bounding_boxes)) // (len(bounding_boxes) - 1)
    

    new_x_positions = []
    current_x = 0
    for bbox in bounding_boxes:
        new_x_positions.append(current_x)
        current_x += bbox[2] + spacing  # width of the bounding box + spacing


    white_background = np.ones((preprocessed_img.shape[0], original_width, 3), dtype=np.uint8) * 255
    
    for i, (x, y, w, h) in enumerate(bounding_boxes):
        card_region = preprocessed_img[y:y+h, x:x+w]
        if i == len(bounding_boxes) - 2:
            saved_image = cv2.imread("cardcounting/src/blackjack/files/bounding_box_1.jpg")
            resized_saved_image = cv2.resize(saved_image, (w, h))
            white_background[y:y+h, new_x_positions[i]:new_x_positions[i]+w] = resized_saved_image
        elif i == len(bounding_boxes) - 1:
            saved_image = cv2.imread("cardcounting/src/blackjack/files/bounding_box_0.jpg")
            resized_saved_image = cv2.resize(saved_image, (w, h))
            white_background[y:y+h, new_x_positions[i]:new_x_positions[i]+w] = resized_saved_image
        else:
            white_background[y:y+h, new_x_positions[i]:new_x_positions[i]+w] = cv2.cvtColor(card_region, cv2.COLOR_GRAY2BGR)

    return white_background

def add_number(image, number):
    # Dumb fix for the fact that pytesseract can't recognize the number 7
    h, w = image.shape[:2]
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 2
    color = (0, 0, 0)
    thickness = 5
    
    text_size, _ = cv2.getTextSize(str(number), font, scale, thickness)
    text_w, text_h = text_size
    
    x = w - text_w - 20
    y = h // 2 + text_h // 2

    cv2.putText(image, str(number), (x, y), font, scale, color, thickness)
    
    return image

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


def make_decision(true_count, player_amount, dealer_amount, player_hand, dealer_hand, ace_count):
    """
    Makes a decision based on the current state of the game.

    Args:
        count (list): A list containing the running count of the cards.
        player_amount (list): A list containing the player's current hand value.
        dealer_amount (list): A list containing the dealer's current hand value.
        player_hand (list): A list representing the player's hand.
        dealer_hand (list): A list representing the dealer's hand.

    Returns:
        str: The decision made by the function. Possible values are "Stand", "Hit", "Double Down", or "Split".
    """
    player_total = player_amount[0]
    dealer_showing = card_values[dealer_hand[0]]

    
    # Check for splitting
    if len(player_hand) == 2 and player_hand[0] == player_hand[1]:
        if player_hand[0] in ['A', '8']:
            return "Split"
        elif player_hand[0] in ['2', '3', '7'] and dealer_showing in [2, 3, 4, 5, 6, 7]:
            return "Split"
        elif player_hand[0] in ['4'] and dealer_showing in [5, 6]:
            return "Split"
        elif player_hand[0] in ['6'] and dealer_showing in [2, 3, 4, 5, 6]:
            return "Split"
        elif player_hand[0] in ['9'] and dealer_showing not in [7, 10, 'A']:
            return "Split"
        elif true_count >= 4 and player_hand[0] == '10':
            if dealer_showing == 6:
                return "Split"
            elif dealer_showing == 5 and true_count >= 5:
                return "Split"
            elif dealer_showing == 4 and true_count >= 6:
                return "Split"

    # Check for doubles and standing  With ace
    if ace_count > 0:
        if player_total in [13, 14] and dealer_showing in [5, 6]:
            return "Double Down"
        elif player_total in [15, 16] and dealer_showing in [4, 5, 6]:
            return "Double Down"
        elif player_total in [17]:
            if dealer_showing in [3, 4, 5, 6]:
                return "Double Down"
            elif dealer_showing in [2] and true_count >= 1:
                return "Double Down"
        elif player_total in [18]:
            if dealer_showing in  [3, 4, 5, 6]:
                return "Double Down"
            elif dealer_showing in [2] and true_count >= 1:
                return "Double Down"
        elif player_total in [19]:
            if dealer_showing in [5, 6] and true_count >= 1:
                return "Double Down"
            elif dealer_showing in [4] and true_count >= 4:
                return "Double Down"

    # Check for doubling down
    if len(player_hand) == 2:
        if player_total in [8] and true_count >= 2:
            return "Double Down"
        if player_total in [9]:
            if dealer_showing in [3, 4, 5, 6]:
                return "Double Down"
            elif true_count >= 1 and dealer_showing == 2:
                return "Double Down"
            elif true_count >= 3 and dealer_showing == 7:
                return "Double Down"
        elif player_total in [10]:
            if dealer_showing in [2, 3, 4, 5, 6, 7, 8, 9]:
                return "Double Down"
            elif dealer_showing in [10,11] and true_count >= 4:
                return "Double Down"
        elif player_total in [11]:
            if dealer_showing != 11:
                return "Double Down"
            elif true_count >= 1:
                return "Double Down"
            

    # Check for standing and hitting
    if player_total >= 17:
        return "Stand"
    elif player_total <= 11:
        return "Hit"
    elif player_total == 12:
        if dealer_showing in [7,8,9,10,11]:
            return "Hit"
        elif dealer_showing in [4] and true_count < 0:
            return "Hit"
        elif dealer_showing in [2] and true_count >= 2:
            return "Stand"
        elif dealer_showing in [3] and true_count >= 3:
            return "Stand"
        elif dealer_showing in [5, 6]:
            return "Stand"
        else:
            return "Hit"
    elif 13 <= player_total <= 16:
        if player_total == 13 and true_count <= -1 and dealer_showing == 2:
            return "Hit"
        elif player_total == 16 :
            if dealer_showing == 7 and true_count >= 9:
                return "Stand"
            elif dealer_showing == 8 and true_count >= 7:
                return "Stand"
            elif dealer_showing == 9 and true_count >= 4:
                return "Stand"
            elif dealer_showing == 10 and true_count > 0:
                return "Stand"
            else:
                return "Hit"
        elif player_total == 15 and dealer_showing == 10 and true_count >= 4:
            return "Stand"
        if dealer_showing in [2, 3, 4, 5, 6]:
            return "Stand"
        else:
            return "Hit"
    
        


def evaluate_game_state(count, cards_remaining, player_hand, dealer_hand, player_amount, dealer_amount, stood, split = False):
    """
    Makes a decision based on the current state of the game.

    Args:
        count (list): A list containing the running count of the cards.
        cards_remaining (list): A list containing the number of cards remaining in the deck.
        player_hand (list): A list representing the player's hand.
        dealer_hand (list): A list representing the dealer's hand.
        player_amount (list): A list containing the player's current hand value.
        dealer_amount (list): A list containing the dealer's current hand value.
        stood (bool): A boolean indicating whether the player has stood or not.

    Returns:
        str: The decision made by the function. Possible values are "Tie", "Win", "Loss", or "Playing".
    """
    with mss.mss() as sct:
        
        # Grab the cards region
        cards_img = np.array(sct.grab(cards_region))
        preprocessed_img = preprocess_image(cards_img)
        final_img = (add_number(extract_cards(preprocessed_img, 15), "000"))
        config = '--psm 7 -c tessedit_char_whitelist=0123456789AJQK'
        card_text = pytesseract.image_to_string(final_img, config=config)

        # Grab the player and dealer count regions
        player_dealer_img = np.array(sct.grab(player_dealer_count_region))
        player_dealer_text = pytesseract.image_to_string(player_dealer_img, config='--psm 6')

        # Grab the cards remaining region
        cards_remaining_img = np.array(sct.grab(cards_remaining_region))
        cards_remaining_text = pytesseract.image_to_string(cards_remaining_img, config='--psm 6 -c tessedit_char_whitelist=0123456789')


    # Calculate the running count
    cards = re.findall(r'10|[2-9AJQK]', card_text)
    # If there is a Letter at the end it recognizes it at zero so I add two random cards to fix it don't ask
    cards.pop() # Remove the extra card that was added to fix recognition
    cards.pop() # Remove the extra card that was added to fix recognition 
    print(cards)

    if "Blackjack" in player_dealer_text:
        if player_dealer_text.count("Blackjack") == 2:
            player_amount[0], dealer_amount[0] = "Blackjack", "Blackjack"
            return "Tie"
        if "Blackjack" in player_dealer_text.split("V")[1]:
            player_amount[0] = "Blackjack"
            return "Win"
        else:
            dealer_amount[0] = "Blackjack"
            return "Loss"

    player_amount[0], dealer_amount[0] =list(map(int, re.findall(r'\d+', player_dealer_text)))
    cards_remaining[0] = int(cards_remaining_text)

    # Figure out the player's hand and the dealer's hand
    player_hand.clear()
    dealer_hand.clear()
    ace_count = 0
    running_count = 0
    for card in cards:
        if running_count < player_amount[0]:
            if card == 'A':
                if running_count + card_values[card] <= player_amount[0]:
                    ace_count += 1
                    running_count += card_values[card]
                    player_hand.append(card)
                elif running_count + 1 <= player_amount[0]:
                    running_count += 1
                    player_hand.append(card)
            else:
                if ((running_count + card_values[card]) > (player_amount[0])) and ace_count > 0:
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

    if split:
        for card in player_hand[1:]:
            count[0] += card_count_values[card]
        
        for card in dealer_hand[1:]:
            count[0] += card_count_values[card]
    else:
        for card in player_hand:
            count[0] += card_count_values[card]
        
        for card in dealer_hand:
            count[0] += card_count_values[card]


    result = check_win_loss_tie(player_amount, dealer_amount, stood)

    if result != "Playing":
        return result
    else:
        decision = make_decision(count[0]/((cards_remaining[0] if cards_remaining[0] else 156)/52), player_amount, dealer_amount, player_hand, dealer_hand, ace_count)
        return decision
        
