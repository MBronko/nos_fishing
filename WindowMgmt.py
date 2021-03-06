import numpy as np
import cv2
import time

import win32api
import win32con
import win32gui
import win32ui
import ctypes


class NosWindowNotFound(BaseException):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class NonAdminUser(BaseException):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class Window:
    def __init__(self, hwnd, _id=1, show_id=False):
        self.hwnd = hwnd
        self.last_focused = 0
        self.id = _id
        self.show_id = show_id

    def get_bounds(self):
        return win32gui.GetWindowRect(self.hwnd)

    def press(self, key, urgent=False):
        mod_keys = [
            win32con.VK_LSHIFT,
            win32con.VK_RSHIFT,
            win32con.VK_LCONTROL,
            win32con.VK_RCONTROL,
            win32con.VK_LMENU,
            win32con.VK_RMENU,
            # win32con.VK_SHIFT,
            # win32con.VK_CONTROL,
            # win32con.VK_MENU
        ]
        char = ord(key[0].upper())

        keys_to_escape = [(key, win32api.MapVirtualKey(key, 0)) for key in mod_keys if win32api.GetAsyncKeyState(key) < 0]

        if not urgent and keys_to_escape:
            while len([key for key in mod_keys if win32api.GetAsyncKeyState(key) < 0]) > 0:
                time.sleep(0.1)
            keys_to_escape = []

        for key, code in keys_to_escape:
            win32api.keybd_event(key, code, win32con.KEYEVENTF_EXTENDEDKEY |win32con.KEYEVENTF_KEYUP)

        win32api.SendMessage(self.hwnd, win32con.WM_KEYDOWN, char, 0)

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


def get_nos_hwnds():
    res = []

    def enum_win(hwnd, result):
        win_text = win32gui.GetWindowText(hwnd)
        if win_text.startswith('NosTale'):
            res.append(hwnd)

    win32gui.EnumWindows(enum_win, res)

    return res


def parse_user_choice(text):
    res = []
    for x in text.split(','):
        if '-' not in x:
            res += [int(x)]
        else:
            start, end = x.split('-')
            res += list(range(int(start), int(end) + 1))
    return res


def get_nostale_windows():
    if ctypes.windll.shell32.IsUserAnAdmin() == 0:
        raise NonAdminUser('You have to start program as administrator')

    hwnds = get_nos_hwnds()

    if not hwnds:
        raise NosWindowNotFound('NosTale window not found')

    if len(hwnds) == 1:
        return [Window(hwnds[0])]

    for idx, hwnd in enumerate(hwnds, 1):
        win32gui.SetWindowText(hwnd, f'NosTale {idx}')

    choice = input('Input NosTale id\'s (You can see them inside window titles) i.e. 1,2,3 or 1-3,5: ')

    choice = parse_user_choice(choice)

    return [Window(hwnd, idx, show_id=True) for idx, hwnd in enumerate(hwnds, 1) if idx in choice]
