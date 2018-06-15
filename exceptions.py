#!/usr/bin/env python

class EmptyListException(Exception):
    """EmptyListException"""
    def __init__(self):
        Exception.__init__(self)

    def __str__(self):
        return repr('Empty list')

class ListNotMatchException(Exception):
    """ListNotMatchException"""
    def __init__(self):
        Exception.__init__(self)

    def __str__(self):
        return repr('List not match')
