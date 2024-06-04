import cv2
import time
import numpy as np

card_values = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
    '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10, 'A': [1, 11]
}


def display_overlay(count, cards_remaining, player_hand, dealer_hand, player_amount , dealer_amount, win_count, loss_count, tie_count):
    while True:
        overlay_img = np.zeros((1000, 400, 3), dtype=np.uint8)

        #Display the Count
        cv2.putText(overlay_img, f"Count: {count[0]}", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

        #Display the True Count
        cv2.putText(overlay_img, f"True Count: {count[0]/3:.2f}", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

        #Display the Cards Remaining
        cv2.putText(overlay_img, f"Cards Remaining: {cards_remaining[0]}", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

        #Display Player hand 
        cv2.putText(overlay_img, f"Player Hand: {player_hand}", (30, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(overlay_img, f"Player Amount: {player_amount[0]}", (30, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

        #Display Dealer hand
        cv2.putText(overlay_img, f"Dealer Hand: {dealer_hand}", (30, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(overlay_img, f"Dealer Amount: {dealer_amount[0]}", (30, 330), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

        #Display Win, Loss, Tie Count
        total_games = win_count[0] + loss_count[0] + tie_count[0]
        win_percentage = (win_count[0] / total_games) * 100 if total_games > 0 else 0
        loss_percentage = (loss_count[0] / total_games) * 100 if total_games > 0 else 0
        tie_percentage = (tie_count[0] / total_games) * 100 if total_games > 0 else 0

        cv2.putText(overlay_img, f"Win Percentage: {win_percentage:.2f}%", (30, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(overlay_img, f"Loss Percentage: {loss_percentage:.2f}%", (30, 430), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(overlay_img, f"Tie Percentage: {tie_percentage:.2f}%", (30, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow("Count Overlay", overlay_img)
        cv2.moveWindow("Count Overlay", -200, 0)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        time.sleep(0.1)
