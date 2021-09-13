import numpy as np
from PIL import ImageGrab
import cv2

from WindowMgmt import *

pixel = (591, 593)
buffs = [
    # ['Covert Fishing' '3', 200],
    # ['Fish-Fish Dance', '', 200],
    # ['Maintain Fishing Line', '', 120],
    ['Bait Fishing', '7', 120],
]


window = ''
try:
    window = get_nostale_window()
except NosWindowNotFound as e:
    print(e.message)
    exit()

off_x, off_y = window.get_pixel_offset()
pixel_pos = (pixel[0] + off_x, pixel[1] + off_y)

player = Player(window, buffs)


def mouse_position():
    print(pyautogui.position())


def get_screenshot():
    position = window.get_bounds()

    screenshot = ImageGrab.grab(position, all_screens=True)
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    return screenshot


def draw_screen(screenshot, to_pull):
    for x in range(-2, 3):
        for y in range(-2, 3):
            color = [255, 0, 0] if to_pull else [0, 0, 225]
            screenshot[pixel_pos[1] + x][pixel_pos[0] + y] = color

    cv2.imshow("Screen", screenshot)
    key = cv2.waitKey(25)


def main_loop():
    recognized_pixels = set()

    pixel_recognition_time = 2

    time.sleep(3)

    player.all_actions()

    start = time.perf_counter()
    while True:
        screenshot = get_screenshot()

        pixel_check = tuple(screenshot[pixel_pos[1]][pixel_pos[0]])

        if time.perf_counter() - start < pixel_recognition_time:
            recognized_pixels.add(pixel_check)

        to_pull = pixel_check not in recognized_pixels

        if to_pull or time.perf_counter() - start > 20:
            if time.perf_counter() - start > 20:
                recognized_pixels = set()

            player.all_actions()

            start = time.perf_counter()


if __name__ == '__main__':
    main_loop()

# while True:
#     mouse_position()
#     screenshot = get_screenshot()
#     draw_screen(screenshot, True)
