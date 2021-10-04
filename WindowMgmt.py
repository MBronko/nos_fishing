import subprocess
import sys

import pyautogui
import numpy as np
import cv2


class NosWindowNotFound(BaseException):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class NonAdminUser(BaseException):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


def get_nostale_window():
    if sys.platform == 'win32':
        import win32api
        import win32con
        import win32gui
        import win32ui
        import ctypes

        if ctypes.windll.shell32.IsUserAnAdmin() == 0:
            raise NonAdminUser('You have to start program as administrator')

        class Window:
            def __init__(self):
                self.hwnd = win32gui.FindWindowEx(0, 0, None, 'NosTale')

                if not self.hwnd:
                    raise NosWindowNotFound('NosTale window not found')

                self.last_focused = 0

            def get_bounds(self):
                return win32gui.GetWindowRect(self.hwnd)

            def press(self, key):
                char = ord(key[0].upper())

                win32api.SendMessage(self.hwnd, win32con.WM_KEYDOWN, char, 0)
                win32api.SendMessage(self.hwnd, win32con.WM_KEYUP, char, 0)

            def get_screenshot(self, relative_bounds):
                left, upper, right, bottom = relative_bounds
                width = right - left
                height = bottom - upper

                wDC = win32gui.GetWindowDC(self.hwnd)
                dcObj = win32ui.CreateDCFromHandle(wDC)
                cDC = dcObj.CreateCompatibleDC()
                dataBitMap = win32ui.CreateBitmap()
                dataBitMap.CreateCompatibleBitmap(dcObj, width, height)
                cDC.SelectObject(dataBitMap)
                cDC.BitBlt((0, 0), (width, height), dcObj, (left, upper), win32con.SRCCOPY)

                signedIntsArray = dataBitMap.GetBitmapBits(True)
                img = np.fromstring(signedIntsArray, dtype='uint8')
                img.shape = (height, width, 4)

                dcObj.DeleteDC()
                cDC.DeleteDC()
                win32gui.ReleaseDC(self.hwnd, wDC)
                win32gui.DeleteObject(dataBitMap.GetHandle())

                return cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)

    elif sys.platform == 'linux' or sys.platform == 'linux2':
        from ewmh import EWMH
        from PIL import ImageGrab

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

            def press(self, char):
                self.focus_window()
                pyautogui.press(char)
                self.restore_focus()

            def get_screenshot(self, bounds):
                abs_left, abs_upper, _, _ = self.get_bounds()
                bounds = bounds[0] + abs_left, bounds[1] + abs_upper, bounds[2] + abs_left, bounds[3] + abs_upper

                screenshot = ImageGrab.grab(bounds, all_screens=True)
                screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

                return screenshot

    else:
        raise OSError('Unsupported operating system')

    return Window()
