import cv2
import time
import numpy as np

def display_overlay(count, cards_remaining):
    while True:
        overlay_img = np.zeros((1000, 400, 3), dtype=np.uint8)

        overlay_text = f"Count: {count[0]}  \nTrue Count: {count[0]/2:.2f} \nCards Remaining: {cards_remaining[0]}"

        #Display the Count
        cv2.putText(overlay_img, f"Count: {count[0]}", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

        #Display the True Count
        cv2.putText(overlay_img, f"True Count: {count[0]/2:.2f}", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

        #Display the Cards Remaining
        cv2.putText(overlay_img, f"Cards Remaining: {cards_remaining[0]}", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)


        
        cv2.imshow("Count Overlay", overlay_img)
        cv2.moveWindow("Count Overlay", -200, 0)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        time.sleep(0.1)
