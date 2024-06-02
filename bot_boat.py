import pyautogui
import time


time.sleep(10)
def type_and_enter(text, interval):
    while True:
        for char in text:
            if char == '?':
                pyautogui.keyDown('shift')
                pyautogui.press('/')
                pyautogui.keyUp('shift')
            else:
                pyautogui.write(char)
        pyautogui.press('enter')
        time.sleep(interval)

# The text to type
text_to_type = '?work'

# Interval in seconds (5 minutes)
interval_seconds = 5 * 61

# Start the typing loop
type_and_enter(text_to_type, interval_seconds)
