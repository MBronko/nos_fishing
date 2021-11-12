from Config import config, get_section, parse_name, parse_value
from enum import Enum, auto

import time
import random


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

            self.interface.window.press(self.key)

            self.interface.wait_time(self.interface.buff_delay)
            self.last_used = time.perf_counter()


class Player:
    def __init__(self, interface):
        self.interface = interface

        buff_data = get_section(config, 'buffs')

        self.player_state = self.State.IDLE

        self.buffs = [Buff(self.interface, parse_name(name), *parse_value(values, (str, int))) for name, values in
                      buff_data.items()]
        self.activated = config.get('general', 'activate') == 'true'

        self.cast_line_key = config.get('skills', 'cast-line')
        self.reel_in_key = config.get('skills', 'reel-in')
        self.cast_pro_key, self.cast_pro_cd = parse_value(config.get('skills', 'cast-line-pro'), (str, int))
        self.use_pro = config.get('skills', 'use-pro-cast') == 'true'

        self.reeling_delay = sorted(parse_value(config.get('delays', 'reeling'), (int, int), '-'))
        self.post_reeling_delay = config.getint('delays', 'post-reeling')
        self.cast_delay = config.getint('delays', 'cast')

        self.last_pro_cast = None

        self.to_pull = False

    class State(Enum):
        IDLE = auto()
        FISHING = auto()

    def use_buffs(self):
        if not self.activated:
            return

        for effect in self.buffs:
            effect.use()

    def cast_line(self):
        if not self.activated:
            return

        self.player_state = self.State.FISHING

        if self.use_pro and (self.last_pro_cast is None or time.perf_counter() - self.last_pro_cast > self.cast_pro_cd):
            self.interface.log_message('Casting a line (Pro)')
            self.interface.window.press(self.cast_pro_key)
            self.last_pro_cast = time.perf_counter()
            time.sleep(0.2)
        else:
            self.interface.log_message('Casting a line')
        self.interface.window.press(self.cast_line_key)

        self.interface.wait_time(self.cast_delay, constant=True)

    def reel_in(self):
        if not self.activated:
            return

        self.interface.log_message('Noticed to reel in')

        res = self.interface.wait_time(random.randrange(*self.reeling_delay), constant=True, check_pixel=True)

        if not res:
            if self.interface.false_positive_counter <= 3:
                self.interface.log_message('False positive detected')
                return False
            else:
                self.interface.log_message('Reached limit of false positive detections')

        self.player_state = self.State.IDLE

        self.interface.log_message('Reeling in')

        self.interface.window.press(self.reel_in_key, urgent=True)

        self.interface.wait_time(self.post_reeling_delay)

        return True

    def all_actions(self):
        if not self.activated:
            return

        res = self.reel_in()

        self.to_pull = False

        if res:
            if not self.interface.pause:
                self.use_buffs()
                self.cast_line()
            return True
        return False
