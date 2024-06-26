import cv2
import mss
import pytesseract
import numpy as np
from pynput import keyboard
import time

# Card values for counting
card_values = {
    '2': 1, '3': 1, '4': 1, '5': 1, '6': 1,
    '7': 0, '8': 0, '9': 0,
    '10': -1, 'J': -1, 'Q': -1, 'K': -1, 'A': -1
}

hit_coordinates = (520, 715)
stand_coordinates = (615, 715)
double_coordinates = (740, 715)
split_coordinates = (860, 715)

count = 0
cards_region = {'top': 500, 'left': 495, 'width': 600, 'height': 32}
player_dealer_count_region = {'top': 615, 'left': 490, 'width': 300, 'height': 30}
cards_remaining_region = {'top': 640, 'left': 490, 'width': 60, 'height': 30}

# Overlay text
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

def update_count():
    global count, overlay_text, update_flag
    with mss.mss() as sct:
        # Grab the screenshot of the cards
        cards_img = np.array(sct.grab(cards_region))
        preprocessed_img = preprocess_image(cards_img)
        final_img = extract_cards(preprocessed_img)

        # Extract the card text
        config = '--psm 6 -c tessedit_char_whitelist=0123456789JQKA'
        card_text = pytesseract.image_to_string(final_img, config=config)

        # Grab the screenshot of the player/dealer count
        count_img = np.array(sct.grab(player_dealer_count_region))
        count_text = pytesseract.image_to_string(count_img, config='--psm 6 -c tessedit_char_whitelist=0123456789')

        # Grab the screenshot of the cards remaining
        cards_remaining_img = np.array(sct.grab(cards_remaining_region))
        cards_remaining_text = pytesseract.image_to_string(cards_remaining_img, config='--psm 6 -c tessedit_char_whitelist=0123456789')

        # Calculate the count
        cards = card_text.replace("\n", "").split(" ")
        for card in cards:
            if card in card_values:
                count += card_values[card]
        true_count = count / 3 

        print(cards)
        print(count_text)
        print(count)
        print(cards_remaining_text)


        overlay_text = f"Count: {count}  \nTrue Count: {true_count:.2f} \nCards Remaining: {cards_remaining_text}"
        update_flag = True

def display_overlay():
    global update_flag, overlay_text
    while True:
        overlay_img = np.zeros((1000, 400, 3), dtype=np.uint8)
        if update_flag:
            y0, dy = 30, 30
            for i, line in enumerate(overlay_text.split('\n')):
                y = y0 + i*dy
                cv2.putText(overlay_img,  line, (50, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
            update_flag = False
        else:
            # If not updated, keep the last overlay text
            y0, dy = 30, 30
            for i, line in enumerate(overlay_text.split('\n')):
                y = y0 + i*dy
                cv2.putText(overlay_img,  line, (50, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.imshow("Count Overlay", overlay_img)
        cv2.moveWindow("Count Overlay", -200, 0)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        time.sleep(0.1)

def on_press(key):
    global update_flag
    try:
        if key.char == 'p' and not update_flag:
            update_count()
    except AttributeError:
        pass

if __name__ == "__main__":

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    display_overlay()

    listener.join()
