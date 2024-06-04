import pyautogui
import time

def place_bet(amount):
    if amount < 100:
        amount = 100
    print(f"Placing a bet of {amount}")
    
    # Move the cursor to the text box position (500, 840) on the screen
    pyautogui.moveTo(500, 840, duration=0.5)
    
    # Click on the text box
    pyautogui.click()
    
    # Type the command
    pyautogui.typewrite(f"/blackjack {amount}", interval=0.1)
    
    # Press Enter to execute the command
    pyautogui.press('enter')


