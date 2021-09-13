import pyautogui
import numpy as np
from PIL import ImageGrab
import cv2

from Config import config, get_section, parse_name

import sys
import subprocess
import time
import math
import random

log_start = time.perf_counter()


class NosWindowNotFound(BaseException):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


def get_nostale_window():
    if sys.platform == 'win32':
        import win32gui

        class Window:
            def __init__(self):
                def enum_win(hwnd, result):
                    win_text = win32gui.GetWindowText(hwnd)
                    if win_text == 'NosTale':
                        res.append(hwnd)

                res = []
                win32gui.EnumWindows(enum_win, res)

                if not res:
                    raise NosWindowNotFound('NosTale window not found')

                self.hwnd = res[0]
                self.last_focused = 0

            def get_bounds(self):
                return win32gui.GetWindowRect(self.hwnd)

            def focus_window(self):
                self.last_focused = win32gui.GetForegroundWindow()

                if self.last_focused != self.hwnd:
                    win32gui.SetForegroundWindow(self.hwnd)
                    time.sleep(0.05)

            def restore_focus(self):
                if self.last_focused != self.hwnd:
                    win32gui.SetForegroundWindow(self.last_focused)

            def get_pixel_offset(self):
                return 0, 0

    elif sys.platform == 'linux' or sys.platform == 'linux2':
        from ewmh import EWMH

        class Window:
            def __init__(self):
                self.ewmh = EWMH()

                try:
                    self.window = next(
                        filter(lambda w: w.get_wm_class()[0] == 'nostaleclientx.exe', self.ewmh.getClientList()))
                except StopIteration:
                    raise NosWindowNotFound('NosTale window not found')

                self.last_focused = None

            def get_bounds(self):
                out = subprocess.Popen(['xwininfo', '-name', 'NosTale', '-int'], stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)

                stdout, stderr = out.communicate()
                res = stdout.decode('utf-8').split('\n')

                x = int(next(filter(lambda w: 'Absolute upper-left X:  ' in w, res)).split()[-1])
                y = int(next(filter(lambda w: 'Absolute upper-left Y:  ' in w, res)).split()[-1])

                width = int(next(filter(lambda w: 'Width' in w, res)).split()[-1])
                height = int(next(filter(lambda w: 'Height' in w, res)).split()[-1])

                return x, y, x + width, y + height

            def focus_window(self):
                self.last_focused = self.ewmh.getActiveWindow()

                if self.ewmh.getWmPid(self.last_focused) != self.ewmh.getWmPid(self.window):
                    self.ewmh.setActiveWindow(self.window)
                    self.ewmh.display.flush()

            def restore_focus(self):
                if self.ewmh.getWmPid(self.last_focused) != self.ewmh.getWmPid(self.window):
                    self.ewmh.setActiveWindow(self.last_focused)
                    self.ewmh.display.flush()

            def get_pixel_offset(self):
                return -5, -30

    else:
        raise OSError('Unsupported operating system')

    return Window()


class Buff:
    def __init__(self, window, name, key, cooldown):
        self.last_used = None
        self.name = name
        self.key = key
        self.cooldown = int(cooldown)
        self.window = window

    def use(self):
        if self.last_used is None or time.perf_counter() - self.last_used > self.cooldown:
            log_message(f'Using "{self.name}" skill')
            self.window.focus_window()
            pyautogui.press(self.key)
            self.window.restore_focus()
            wait_time(1)
            self.last_used = time.perf_counter()


class Player:
    def __init__(self, window):
        buff_data = get_section(config, 'buffs')

        self.buffs = [Buff(window, parse_name(name), *values.split(';')) for name, values in buff_data.items()]
        self.activated = config.get('general', 'activate') == 'true'

        self.cast_line_key = config.get('skills', 'cast-line')
        self.reel_in_key = config.get('skills', 'reel-in')
        self.cast_pro_key, cast_pro_cd = config.get('skills', 'cast-line-(pro)').split(';')
        self.cast_pro_cd = int(cast_pro_cd)
        self.use_pro = config.get('skills', 'use-pro-cast') == 'true'

        self.window = window
        self.last_mega_cast = time.perf_counter()

        self.to_pull = False

    def use_buffs(self):
        if not self.activated:
            return

        for effect in self.buffs:
            effect.use()

    def cast_line(self):
        if not self.activated:
            return

        self.window.focus_window()
        if self.use_pro and time.perf_counter() - self.last_mega_cast > self.cast_pro_cd:
            log_message('Pro casting a line')
            pyautogui.press(self.cast_pro_key)
            self.last_mega_cast = time.perf_counter()
        else:
            log_message('Casting a line')
            pyautogui.press(self.cast_line_key)
            self.window.restore_focus()

        wait_time(3, constant=True)

    def reel_in(self):
        if not self.activated:
            return

        log_message('Noticed to reel in')
        wait_time()

        log_message('Reeling in')
        self.window.focus_window()
        pyautogui.press(self.reel_in_key)
        self.window.restore_focus()

        wait_time(4)

    def all_actions(self):
        if not self.activated:
            return

        self.reel_in()

        self.to_pull = False

        self.use_buffs()
        self.cast_line()


window = ''
try:
    window = get_nostale_window()
except NosWindowNotFound as e:
    print(e.message)
    exit()

player = Player(window)

to_pull = False


def wait_time(additional=0, constant=False):
    fps = 5

    sleep_time = additional
    if not constant:
        sleep_time += random.randrange(10000, 22000) / 10000

    while sleep_time > 0:
        start = time.perf_counter()
        draw_screen()
        mouse_position()
        sleep_time = max(sleep_time - time.perf_counter() + start, 0)

        sleep_interval = 1 / fps if sleep_time - (1 / fps) > 0 else sleep_time
        time.sleep(sleep_interval)
        sleep_time -= sleep_interval


def log_message(msg):
    timer = format(time.perf_counter() - log_start, '.3f')
    print(f'{" " * (8 - len(timer))}{timer}:  {msg}')


def mouse_position():
    if config.get('general', 'show-mouse-position') != 'true':
        return

    mouse_pos = pyautogui.position()
    bounds = window.get_bounds()

    log_message(f'Mouse position x={mouse_pos.x - bounds[0]}, y={mouse_pos.y - bounds[1]}')


def calculate_bounds(width_offset=0, height_offset=0):
    if width_offset == 0:
        width_offset, height_offset = [math.floor(int(x) / 2) for x in
                                       config.get('screenshots', 'window-resolution').split(';')]

    pixel_pos = [int(x) for x in config.get('general', 'pixel-position').split(';')]
    abs_x, abs_y = [x1 + x2 for x1, x2 in zip(window.get_bounds(), pixel_pos)]

    return abs_x - width_offset, abs_y - height_offset, abs_x + width_offset, abs_y + height_offset


def get_screenshot(bounds):
    screenshot = ImageGrab.grab(bounds, all_screens=True)
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    return screenshot


def draw_screen():
    if config.get('general', 'show-watched-pixel') != 'true':
        return

    mark_x, mark_y = [int(x) for x in config.get('screenshots', 'mark-resolution').split(';')]
    width_offset, height_offset = [math.floor(int(x) / 2) for x in
                                   config.get('screenshots', 'window-resolution').split(';')]

    bounds = calculate_bounds(width_offset, height_offset)
    screenshot = get_screenshot(bounds)

    for x in range(-mark_x, mark_x + 1):
        for y in range(-mark_y, mark_y + 1):
            color = [0, 0, 255] if player.to_pull else [0, 255, 0]
            # color = [0, 255, 0]
            screenshot[height_offset + y][width_offset + x] = color

    cv2.imshow("NosFish", screenshot)
    key = cv2.waitKey(1)
