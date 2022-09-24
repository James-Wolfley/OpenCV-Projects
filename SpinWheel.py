import keyboard
import cv2
import numpy
import mss
import pyautogui as pgui
import time
from PIL import Image, ImageOps
from pytesseract import pytesseract
from enum import Enum
import io
import os


scrap_x = 1580
scrap_y = 819
split_x= 1587
split_y= 666
bet1_x = 1749
bet1_y = 886
setNumber_x = 1342
setNumber_y = 680


class GameStates(Enum):
    PreBet = 1
    PreSpin = 2
    Spinning = 3
    PostSpinWon = 4

path_to_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.tesseract_cmd = path_to_tesseract

clear = lambda: os.system('cls')

win_box_dimensions = {
        'left': 1665,
        'top': 965,
        'width': 462,
        'height': 160
    }

scrap_stack_dimensions = {
        'left': 1519,
        'top': 847,
        'width': 120,
        'height': 40
    }

bet1_box_dimensions = {
        'left': 1690,
        'top': 830,
        'width': 120,
        'height': 120
    }


def setAmount(amount):
    pgui.moveTo(scrap_x, scrap_y)
    pgui.click()
    time.sleep(1)
    pgui.click()
    pgui.moveTo(setNumber_x, setNumber_y)
    pgui.click(button='right')
    pgui.press(list(str(amount)))
    
def dragToBet():
    pgui.moveTo(split_x, split_y)
    time.sleep(.2)
    pgui.dragTo(1749, 886, .25, button='left') 
    
def getScrapStackNumber():    
    sct = mss.mss()
    num_scr = sct.grab(scrap_stack_dimensions)
    temp_img = mss.tools.to_png(num_scr.rgb, num_scr.size)
    img = Image.open(io.BytesIO(temp_img))
    gray_image = ImageOps.grayscale(img)
    text = pytesseract.image_to_string(gray_image)
    #print the text line by line
    return text.translate({ord('«'): None, ord('\n'): None, ord(','): None, ord('x'): None})

def getState():
    
    sct = mss.mss()

    #spinning background
    sb_img = cv2.imread("SpinningBackground.png")
    #What a bet placed looks like
    won_img = cv2.imread("WinBoxWon.png")
    #What it looks like when bet is empty
    be_img = cv2.imread("BetEmpty.png")
    
    win_box_scr = numpy.array(sct.grab(win_box_dimensions))
    bet_box_scr = numpy.array(sct.grab(bet1_box_dimensions))
    
    win_box_remove = win_box_scr[:,:,:3]
    bet_box_remove = bet_box_scr[:,:,:3]
    
    win_box_result = cv2.matchTemplate(win_box_remove, sb_img, cv2.TM_CCOEFF_NORMED)
    bet_box_result = cv2.matchTemplate(bet_box_remove, be_img, cv2.TM_CCOEFF_NORMED)
    win_box_win_result = cv2.matchTemplate(win_box_remove, won_img, cv2.TM_CCOEFF_NORMED)
    
    _, win_box_max_val, _, win_box_max_loc = cv2.minMaxLoc(win_box_result)
    _, bet_box_max_val, _, bet_box_max_loc = cv2.minMaxLoc(bet_box_result)
    _, win_box_win_max_val, _, win_box_win_max_loc = cv2.minMaxLoc(win_box_win_result)
    
    print(f"Win Box - Max Val: {win_box_max_val} Max Loc: {win_box_max_loc}")
    print(f"Bet Box - Max Val: {bet_box_max_val} Max Loc: {bet_box_max_loc}")
    print(f"Win Box Win - Max Val: {win_box_win_max_val} Max Loc: {win_box_win_max_loc}")
    
    if win_box_max_val > .95:
        #its spinning
        state = GameStates.Spinning
    elif win_box_win_max_val > .95:
        #we won and need to remove winnings
        state = GameStates.PostSpinWon
    elif win_box_max_val < .95 and bet_box_max_val > .95:
        #pre bet and need to bet
        state = GameStates.PreBet
    elif win_box_max_val < .95 and bet_box_max_val < .95:
        #post bet and waiting for spin
        state = GameStates.PreSpin
    
    
    return state
    

sct = mss.mss()


totalScrap = int(getScrapStackNumber())
startBetPercentage = .01
currentBet = totalScrap / startBetPercentage

#setAmount(currentBet)
#dragToBet()

while True:
    clear()
    print(getState())
    time.sleep(5)

