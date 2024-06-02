import pytesseract
from PIL import Image
import mss
import re
import numpy as np
from pynput import keyboard
import cv2



# Card values for counting
card_values = {
    '2': 1, '3': 1, '4': 1, '5': 1, '6': 1,
    '7': 0, '8': 0, '9': 0,
    '10': -1, 'J': -1, 'Q': -1, 'K': -1, 'A': -1
}

# Function to parse the card hands from the text
def parse_hand(hand_text):
    card_pattern = re.compile(r'([2-9]|10|[JQKA])')
    return card_pattern.findall(hand_text)

# Initialize count
count = 0

# Define the screen region to capture (left, top, width, height)
region = {'top': 470, 'left': 590, 'width': 340, 'height': 70}

def update_count():
    global count
    with mss.mss() as sct:
        # Capture the screen
        screenshot = np.array(sct.grab(region))
        img = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)

        # Use OCR to extract text from the image
        text = pytesseract.image_to_string(img)

        print(text)
        cv2.destroyAllWindows()
        cv2.imshow("Screenshot", screenshot)
        # Check if the text contains a blackjack result
        # if 'Your Hand' in text and 'Dealer Hand' in text:
        #     # Extract hands
        #     hands = re.findall(r'Your Hand(.*?)Dealer Hand(.*?)Value:', text, re.DOTALL)
        #     if hands:
        #         all_hands_text = hands[0][0] + hands[0][1]
        #         cards = parse_hand(all_hands_text)

        #         # Update count based on cards
        #         for card in cards:
        #             count += card_values.get(card, 0)

        #         print(f'Current count is {count}')

# Listener function for key press
def on_press(key):
    try:
        if key.char == 'c':
            update_count()
    except AttributeError:
        pass

# Set up the listener
listener = keyboard.Listener(on_press=on_press)
listener.start()

# Keep the program running
listener.join()
