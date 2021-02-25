import sys
from board import Board
import keyboard
import pyautogui
from time import sleep
from PIL import ImageGrab

if __name__ == '__main__':
    rows, cols = int(sys.argv[1]), int(sys.argv[2])
    pyautogui.PAUSE = 0

    # gets the board region's top left coordinates
    keyboard.wait('enter')
    left, top = pyautogui.position()
    left *= 2
    top *= 2

    # gets the board region's bottom right coordinate
    keyboard.wait('enter')
    right, bottom = pyautogui.position()
    right *= 2
    bottom *= 2

    # multiplies coordinates for mac display compatibility,
    # get rid of this if not on macbook

    # gets smiley coordinate
    keyboard.wait('enter')
    smileyX, smileyY = pyautogui.position()

    # gets win box coordinate
    # keyboard.wait('enter')
    # winX, winY = pyautogui.position()

    pieceWidth, pieceHeight = (right - left) / cols, (bottom - top) / rows

    while 1:
        board = Board(rows, cols, pieceWidth, pieceHeight, left, top) 
        pyautogui.click(smileyX, smileyY)
        # pyautogui.click(winX, winY)
        sleep(0.1)
        board.firstMove()
        while 1:
            img = ImageGrab.grab()
            board.updateBoard(img)
            # break if the AI is unable to find a suitable move
            if not board.move(img):
                break
        sleep(0.1)