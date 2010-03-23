# -*- coding: utf-8 -*-

def pretty_name(name):
    "Converts 'foo_bar' to 'Foo bar'"
    name = name[0].upper() + name[1:]
    return name.replace('_', ' ')