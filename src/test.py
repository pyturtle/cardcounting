import cv2
import mss
import pytesseract
import numpy as np
import re
from pynput import keyboard

def preprocess_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    inverted = cv2.bitwise_not(thresh)
    black_bar = np.zeros((50, inverted.shape[1]), dtype=np.uint8)
    inverted_with_black_bar = np.vstack((black_bar, inverted, black_bar))
    return inverted_with_black_bar

def extract_cards(preprocessed_img, spacing, contour_count):
    contours, _ = cv2.findContours(preprocessed_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    contour_count[0] = len(contours)

    bounding_boxes = [cv2.boundingRect(cnt) for cnt in contours]

    bounding_boxes = sorted(bounding_boxes, key=lambda x: x[0])

    
    # cv2.imwrite("bounding_box_2.jpg", preprocessed_img[bounding_boxes[0][1]:bounding_boxes[0][1]+bounding_boxes[0][3], bounding_boxes[0][0]:bounding_boxes[0][0]+bounding_boxes[0][2]])

    bounding_boxes.append(bounding_boxes[-1])
    bounding_boxes.append(bounding_boxes[-1])
    # bounding_boxes.insert(0,bounding_boxes[-1])
    # bounding_boxes.insert(0,bounding_boxes[-1])



    total_width = sum(bbox[2] for bbox in bounding_boxes) + spacing * (len(bounding_boxes) - 1)
    
    original_width = preprocessed_img.shape[1]
    if total_width > original_width:
        spacing = (original_width - sum(bbox[2] for bbox in bounding_boxes)) // (len(bounding_boxes) - 1)
    

    new_x_positions = []
    current_x = 30
    for i, bbox in enumerate(bounding_boxes):
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
        # elif i == 0:
        #     saved_image = cv2.imread("cardcounting/src/blackjack/files/bounding_box_2.jpg")
        #     resized_saved_image = cv2.resize(saved_image, (w, h))
        #     white_background[y:y+h, new_x_positions[i]:new_x_positions[i]+w] = resized_saved_image
        # elif i == 1:
        #     saved_image = cv2.imread("cardcounting/src/blackjack/files/bounding_box_2.jpg")
        #     resized_saved_image = cv2.resize(saved_image, (w, h))
        #     white_background[y:y+h, new_x_positions[i]:new_x_positions[i]+w] = resized_saved_image
        else:
            white_background[y:y+h, new_x_positions[i]:new_x_positions[i]+w] = cv2.cvtColor(card_region, cv2.COLOR_GRAY2BGR)
    
    scale_factor = 2.0  # Adjust the scale factor as desired
    scaled_image = cv2.resize(white_background, None, fx=scale_factor, fy=scale_factor)
    return scaled_image

def add_number(image, number):
    # Dumb fix for the fact that pytesseract can't recognize the number 7
    h, w = image.shape[:2]
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 1.8
    color = (0, 0, 0)
    thickness = 3
    
    text_size, _ = cv2.getTextSize(str(number), font, scale, thickness)
    text_w, text_h = text_size
    
    x = w - text_w - 20
    y = h // 2 + text_h // 2

    cv2.putText(image, str(number), (x, y), font, scale, color, thickness)
    
    return image


monitor = {'top': 535, 'left': 495, 'width': 900, 'height': 28}
player_dealer_count_region = {'top': 615, 'left': 490, 'width': 900, 'height': 30}
cards_remaining_region = {'top': 640, 'left': 490, 'width': 200, 'height': 35}



while True:
    with mss.mss() as sct:
        screenshot = sct.grab(monitor)
        img = np.array(screenshot)
        contour_count = [0]
        preprocessed_img = preprocess_image(img)
        final_img = add_number(extract_cards(preprocessed_img, -15, contour_count), "")
        config = '--psm 7 -c tessedit_char_whitelist=23456789AJQK'
        text = pytesseract.image_to_string(final_img, config=config)
        print(text)
        cards = re.findall(r'10|[2-9AJQK]', text)
        print(cards)

        cards.pop()
        cards.pop()
        # cards.pop(0)
        # cards.pop(0)

        if len(cards) > contour_count[0] and "J" in cards:
                jack_index = cards.index("J")
                if jack_index < len(cards) - 1 and cards[jack_index + 1] == "5":
                    cards.pop(jack_index + 1)


        print(cards)
        cv2.imshow("Original Screenshot", img)
        cv2.imshow("Preprocessed Screenshot", preprocessed_img)
        cv2.imshow("Final Image", final_img)


        count_img = np.array(sct.grab(player_dealer_count_region))
        count_text = pytesseract.image_to_string(count_img, config='--psm 6')
        # numbers = list(map(int, re.findall(r'\d+', count_text)))
        # print(numbers)
        print (count_text.split("V"))


        cards_remaining_img = np.array(sct.grab(cards_remaining_region))
        cards_remaining_text = pytesseract.image_to_string(cards_remaining_img, config='--psm 6 -c tessedit_char_whitelist=0123456789')
    
        # player_amount, dealer_amount =list(map(int, re.findall(r'\d+', count_text)))
        # print(player_amount, dealer_amount)

        print(cards_remaining_text)
        cv2.imshow("Cards Remaining", cards_remaining_img)
        cv2.imshow("Player/Dealer Count", count_img)

        cv2.waitKey(0)
        cv2.destroyAllWindows()
