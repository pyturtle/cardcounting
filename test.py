import cv2
import mss
import pytesseract
import numpy as np
from pynput import keyboard

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

monitor = {'top': 500, 'left': 495, 'width': 600, 'height': 32}
player_dealer_count_region = {'top': 615, 'left': 490, 'width': 300, 'height': 30}



while True:
    with mss.mss() as sct:
        screenshot = sct.grab(monitor)
        img = np.array(screenshot)
        preprocessed_img = preprocess_image(img)
        final_img = extract_cards(preprocessed_img)
        config = '--psm 6 -c tessedit_char_whitelist=0123456789JQKA'
        text = pytesseract.image_to_string(final_img, config=config)
        print(text)
        cv2.imshow("Original Screenshot", img)
        cv2.imshow("Preprocessed Screenshot", preprocessed_img)
        cv2.imshow("Final Image", final_img)


        count_img = np.array(sct.grab(player_dealer_count_region))
        count_text = pytesseract.image_to_string(count_img, config='--psm 6 -c tessedit_char_whitelist=0123456789')
        print(count_text)

        cv2.imshow("Player/Dealer Count", count_img)

        cv2.waitKey(0)
        cv2.destroyAllWindows()
