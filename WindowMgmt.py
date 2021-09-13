import pyautogui

from Config import config, get_section, parse_name

import sys
import subprocess
import os
import time
import random

log_start = time.perf_counter()


class NosWindowNotFound(BaseException):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


def random_wait_time(additional=0):
    time.sleep(additional + random.randrange(10000, 22000) / 10000)


def log_message(msg):
    timer = format(time.perf_counter() - log_start, '.3f')
    print(f'{timer} {msg}')


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
        self.cooldown = cooldown
        self.window = window

    def use(self):
        if self.last_used is None or time.perf_counter() - self.last_used > self.cooldown:
            print(f'Using "{self.name}" skill')
            self.window.focus_window()
            pyautogui.press(self.key)
            self.window.restore_focus()
            random_wait_time(1)
            self.last_used = time.perf_counter()


class Player:
    def __init__(self, window):
        buff_data = get_section(config, 'buffs')

        self.buffs = [Buff(window, parse_name(name), *values.split(';')) for name, values in buff_data.items()]

        self.cast_line_key = config.get('skills', 'cast-line')
        self.reel_in_key = config.get('skills', 'reel-in')
        self.cast_pro_key, cast_pro_cd = config.get('skills', 'cast-line-(pro)').split(';')
        self.cast_pro_cd = int(cast_pro_cd)
        self.use_pro = config.get('skills', 'use-pro-cast') == 1

        self.window = window
        self.last_mega_cast = time.perf_counter()

    def use_buffs(self):
        for effect in self.buffs:
            effect.use()

    def cast_a_rod(self):
        self.window.focus_window()
        if self.use_pro and time.perf_counter() - self.last_mega_cast > self.reel_pro_cd:
            log_message('Pro casting a line')
            pyautogui.press(self.reel_pro_key)
            self.last_mega_cast = time.perf_counter()
        else:
            log_message('Casting a line')
            pyautogui.press(self.reel_in_key)
            self.window.restore_focus()

        time.sleep(3)

    def reel_in(self):
        log_message('Noticed to reel in')
        random_wait_time()

        log_message('Reeling in')
        self.window.focus_window()
        pyautogui.press(self.reel_in_key)
        self.window.restore_focus()

        random_wait_time(4)

    def all_actions(self):
        self.reel_in()
        self.use_buffs()
        self.cast_a_rod()
