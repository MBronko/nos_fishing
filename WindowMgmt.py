import pyautogui

import sys
import subprocess
import os
import time
import random


class NosWindowNotFound(BaseException):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


def random_wait_time():
    return random.randrange(10000, 22000) / 10000


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
                    self.window = next(filter(lambda w: w.get_wm_class()[0] == 'nostaleclientx.exe', self.ewmh.getClientList()))
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
            time.sleep(1 + random_wait_time())
            self.last_used = time.perf_counter()


class Player:
    def __init__(self, window, buffs):
        self.buffs = [Buff(window, *stats) for stats in buffs]
        self.window = window
        self.last_mega_cast = time.perf_counter()

    def use_buffs(self):
        for effect in self.buffs:
            effect.use()

    def cast_a_rod(self):
        self.window.focus_window()
        # if time.perf_counter() - self.last_mega_cast > 60:
        #     print('Pro casting a rod')
        #     pyautogui.press('1')
        #     self.last_mega_cast = time.perf_counter()
        # else:
        print('Casting a rod')
        pyautogui.press('2')
        self.window.restore_focus()

        time.sleep(3)

    def pull_up(self):
        print('Noticed to pull up')
        time.sleep(random_wait_time())

        print('Pulling up')
        self.window.focus_window()
        pyautogui.press('6')
        self.window.restore_focus()

        time.sleep(4 + random_wait_time())

    def all_actions(self):
        self.pull_up()
        self.use_buffs()
        self.cast_a_rod()
