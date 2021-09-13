import configparser
import os
import sys

config_file = 'config.ini'

default_values = {
    'buffs': {
        ';covert-fishing': '3;200',
        ';fish-fish-dance': 'r;200',
        ';maintain-fishing-line': '4;120',
        ';bait-fishing': '7;120',
    },
    'skills': {
        'cast-line': '2',
        'cast-line-(pro)': '1;60',
        'reel-in': '6',
        'use-pro-cast': '0'
    },
    'pixel': {
        'position': '591;593',
    },
    'screenshots': {
        ';change "show" value to show/hide debug screenshots': '1/0',
        'show': '1',
        'window-resolution': '200;200',
        'mark-resolution': '3;3',
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


def get_section(conf, section):
    return dict(conf.items(section))


def parse_name(name: str):
    return ' '.join(name.split('-')).title()


if not os.path.exists(config_file):
    create_config_file()

config = configparser.ConfigParser()
config.read('config.ini')
