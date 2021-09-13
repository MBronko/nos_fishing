import numpy as np
from PIL import ImageGrab
import cv2

from WindowMgmt import *
from Config import config, get_section

window = ''
try:
    window = get_nostale_window()
except NosWindowNotFound as e:
    print(e.message)
    exit()

player = Player(window)


def mouse_position():
    print(pyautogui.position())


def get_screenshot(bounds):
    screenshot = ImageGrab.grab(bounds, all_screens=True)
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    return screenshot


def draw_screen(screenshot, to_pull, screenshot_res_offsets):
    mark_x, mark_y = [int(x) for x in config.get('screenshots', 'mark-resolution').split(';')]
    width_offset, height_offset = screenshot_res_offsets

    for x in range(-mark_x, mark_x + 1):
        for y in range(-mark_y, mark_y + 1):
            color = [0, 255, 0] if to_pull else [0, 0, 225]
            screenshot[height_offset + y][width_offset + x] = color

    cv2.imshow("NosTale Capture", screenshot)
    key = cv2.waitKey(25)


def calculate_bounds(window_bounds, pixel_pos, screenshot_res_offsets):
    abs_x, abs_y = [x1 + x2 for x1, x2 in zip(window_bounds, pixel_pos)]
    width_offset, height_offset = screenshot_res_offsets

    return abs_x - width_offset, abs_y - height_offset, abs_x + width_offset, abs_y + height_offset


def main_loop():
    recognized_pixels = set()
    screenshot_res_offsets = [math.floor(int(x) / 2) for x in config.get('screenshots', 'window-resolution').split(';')]
    pixel_pos = [int(x) for x in config.get('pixel', 'position').split(';')]
    show_screenshots = config.get('screenshots', 'show') == '1'
    pixel_recognition_time = 2

    log_message('Fishing started')
    time.sleep(3)

    player.all_actions()

    start = time.perf_counter()
    while True:
        bounds = calculate_bounds(window.get_bounds(), pixel_pos, screenshot_res_offsets)

        screenshot = get_screenshot(bounds)

        pixel_check = tuple(screenshot[screenshot_res_offsets[1]][screenshot_res_offsets[0]])

        if time.perf_counter() - start < pixel_recognition_time:
            recognized_pixels.add(pixel_check)

        to_pull = pixel_check not in recognized_pixels

        if to_pull or time.perf_counter() - start > 20:
            if time.perf_counter() - start > 20:
                recognized_pixels = set()

            # player.all_actions()

            start = time.perf_counter()

        if show_screenshots:
            draw_screen(screenshot, to_pull, screenshot_res_offsets)

# if __name__ == '__main__':
#     main_loop()
