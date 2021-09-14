import sys
import subprocess
import time


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

    else:
        raise OSError('Unsupported operating system')

    return Window()
