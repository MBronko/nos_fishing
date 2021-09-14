import configparser
import os

config_file = 'config.ini'

default_values = {
    'buffs': {
        ';covert-fishing': '3;200',
        ';fish-fish-dance': 'r;200',
        ';bait-fishing': '7;120',
        ';maintain-fishing-line': '4;120',
    },
    'skills': {
        'cast-line-(pro)': '1;60',
        'cast-line': '2',
        'reel-in': '6',
        'use-pro-cast': 'false'
    },
    'screenshots': {
        'window-resolution': '200x200',
        'mark-resolution': '2x2',
    },
    'general': {
        'pixel-position': '591x593',
        'show-mouse-position': 'true',
        'show-watched-pixel': 'true',
        'min-action-delay': '900',
        'max-action-delay': '1800',
        'pixel-recognition-time': '3',
        'activate': 'false',
    }
}


def create_config_file():
    new_config = configparser.ConfigParser()

    for section_name, section in default_values.items():
        new_config.add_section(section_name)
        for variable, value in section.items():
            new_config.set(section_name, variable, value)

    with open(config_file, 'w') as file:
        new_config.write(file)


def get_section(conf: configparser.ConfigParser, section: str):
    return dict(conf.items(section))


def parse_name(name: str):
    return ' '.join(name.split('-')).title()


def parse_value(value: str, types=(str, str), delimeter: str = ';'):
    return [conv(val) for conv, val in zip(types, value.split(delimeter))]


if not os.path.exists(config_file):
    create_config_file()

config = configparser.ConfigParser()
config.read('config.ini')
