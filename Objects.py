import pyautogui

from Config import config, get_section, parse_name, parse_value

import time


class Buff:
    def __init__(self, interface, name: str, key: str, cooldown: int):
        self.last_used = None
        self.interface = interface
        self.name = name
        self.key = key
        self.cooldown = cooldown

    def use(self):
        if self.last_used is None or time.perf_counter() - self.last_used > self.cooldown:
            self.interface.log_message(f'Using "{self.name}" skill')
            self.interface.window.focus_window()
            pyautogui.press(self.key)
            self.interface.window.restore_focus()
            self.interface.wait_time(1)
            self.last_used = time.perf_counter()


class Player:
    def __init__(self, interface):
        self.interface = interface

        buff_data = get_section(config, 'buffs')

        self.buffs = [Buff(self.interface, parse_name(name), *parse_value(values, (str, int))) for name, values in
                      buff_data.items()]
        self.activated = config.get('general', 'activate') == 'true'

        self.cast_line_key = config.get('skills', 'cast-line')
        self.reel_in_key = config.get('skills', 'reel-in')
        self.cast_pro_key, self.cast_pro_cd = parse_value(config.get('skills', 'cast-line-(pro)'), (str, int))
        self.use_pro = config.get('skills', 'use-pro-cast') == 'true'

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

        self.interface.window.focus_window()
        if self.use_pro and time.perf_counter() - self.last_mega_cast > self.cast_pro_cd:
            self.interface.log_message('Pro casting a line')
            pyautogui.press(self.cast_pro_key)
            self.last_mega_cast = time.perf_counter()
        else:
            self.interface.log_message('Casting a line')
            pyautogui.press(self.cast_line_key)
            self.interface.window.restore_focus()

        self.interface.wait_time(3, constant=True)

    def reel_in(self):
        if not self.activated:
            return

        self.interface.log_message('Noticed to reel in')
        self.interface.wait_time()

        self.interface.log_message('Reeling in')
        self.interface.window.focus_window()
        pyautogui.press(self.reel_in_key)
        self.interface.window.restore_focus()

        self.interface.wait_time(4)

    def all_actions(self):
        if not self.activated:
            return

        self.reel_in()

        self.to_pull = False

        self.use_buffs()
        self.cast_line()
