import pyautogui
import numpy as np
from PIL import ImageGrab
import cv2

from Config import config, parse_value
from Objects import Player
from WindowMgmt import get_nostale_window

import time
import math
import random


class MainInterface:
    def __init__(self):
        self.window = None
        self.player = Player(self)

        self.action_delay = sorted(parse_value(config.get('delays', 'post-action'), (int, int), '-'))
        self.buff_delay = config.getint('delays', 'buff')

        self.pixel_recognition_time = config.getint('general', 'pixel-recognition-time')

        self.show_window = config.get('general', 'show-watched-pixel') == 'true'
        self.show_mouse = config.get('general', 'show-mouse-position') == 'true'

        self.pixel_pos = parse_value(config.get('general', 'pixel-position'), (int, int), 'x')
        self.window_res = parse_value(config.get('screenshots', 'window-resolution'), (int, int), 'x')
        self.mark_res = parse_value(config.get('screenshots', 'mark-resolution'), (int, int), 'x')

        self.width_win_offset, self.height_win_offset = [math.floor(x / 2) for x in self.window_res]

        self.log_start = time.perf_counter()

    def initialize(self):
        self.window = get_nostale_window()

    def log_message(self, msg: str):
        timer = format(time.perf_counter() - self.log_start, '.3f')
        print(f'{" " * (8 - len(timer))}{timer}:  {msg}')

    def wait_time(self, additional: int = 0, constant: bool = False):
        fps = 5

        sleep_time = additional / 1000
        if not constant:
            sleep_time += random.randrange(self.action_delay[0], self.action_delay[1]) / 1000

        if self.show_window or self.show_mouse:
            while sleep_time > 0:
                start = time.perf_counter()
                self.draw_window()
                self.mouse_position()
                sleep_time = max(sleep_time - time.perf_counter() + start, 0)

                sleep_interval = 1 / fps if sleep_time - (1 / fps) > 0 else sleep_time
                time.sleep(sleep_interval)
                sleep_time -= sleep_interval
        else:
            time.sleep(sleep_time)

    def mouse_position(self):
        if not self.show_mouse:
            return

        mouse_pos = pyautogui.position()
        bounds = self.window.get_bounds()

        self.log_message(f'Mouse position x={mouse_pos.x - bounds[0]}, y={mouse_pos.y - bounds[1]}')

    def calculate_bounds(self, width_win_offset: int = 0, height_win_offset: int = 0):
        """
        return list[int, int, int, int]
        that correspond to left, upper, right, bottom (respectively) bounds of the box
        middle of the box is on the self.pixel_pos
        width and height of the box are equal to 2*width_win_offset and 2*height_win_offset
        """
        if width_win_offset == 0:
            width_win_offset, height_win_offset = self.width_win_offset, self.height_win_offset

        abs_x, abs_y = [z1 + z2 for z1, z2 in zip(self.window.get_bounds(), self.pixel_pos)]

        return abs_x - width_win_offset, abs_y - height_win_offset, abs_x + width_win_offset, abs_y + height_win_offset

    def get_screenshot(self, bounds):
        screenshot = ImageGrab.grab(bounds, all_screens=True)
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        return screenshot

    def draw_window(self):
        if not self.show_window:
            return

        mark_x, mark_y = self.mark_res

        bounds = self.calculate_bounds()
        screenshot = self.get_screenshot(bounds)

        for x in range(-mark_x, mark_x + 1):
            for y in range(-mark_y, mark_y + 1):
                color = [0, 0, 255] if self.player.to_pull else [0, 255, 0]
                screenshot[self.height_win_offset + y][self.width_win_offset + x] = color

        cv2.imshow("NosFish", screenshot)
        key = cv2.waitKey(1)

    def run(self):
        if self.window is None:
            print('Uninitialized Interface')
            return

        recognized_pixels = set()

        self.draw_window()
        self.mouse_position()

        self.log_message('Fishing started')
        self.wait_time(2, constant=True)

        self.player.all_actions()

        start = time.perf_counter()
        while True:
            self.draw_window()
            self.mouse_position()

            screenshot = self.get_screenshot(self.calculate_bounds(1, 1))

            pixel_check = tuple(screenshot[0][0])

            if time.perf_counter() - start < self.pixel_recognition_time:
                recognized_pixels.add(pixel_check)

            self.player.to_pull = pixel_check not in recognized_pixels

            if self.player.to_pull or time.perf_counter() - start > 20:
                if time.perf_counter() - start > 20:
                    self.log_message('Waiting too long, reseting recognized pixels')
                    recognized_pixels = set()

                self.player.all_actions()

                start = time.perf_counter()
