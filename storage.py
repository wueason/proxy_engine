#!/usr/bin/env python
import os
import random
try:
    import cPickle as pickle
except Exception as e:
    import pickle
try:
    import ujson as json
except Exception as e:
    import json

class Storage(object):
    def insert():
        raise NotImplementedError('funciont insert must be implements')

    def update():
        raise NotImplementedError('funciont update must be implements')

    def purge():
        raise NotImplementedError('funciont purge must be implements')

    def remove(ip, port):
        raise NotImplementedError('funciont remove must be implements')

    def get_random():
        raise NotImplementedError('funciont get_random must be implements')

class LocalStorage(Storage):
    """docstring for LocalStorage"""
    def __init__(self, file_path = '.proxy_engine_local_storage.pkl'):
        super(Storage, self).__init__()
        self.file = file_path
        if not os.path.exists(self.file):
            pickle.dump(set(()),open(self.file,"wb"))

    def insert(self, item):
        try:
            data = pickle.load(open(self.file,"rb"))
            data.add(item)
            pickle.dump(data,open(self.file,"wb"))
        except Exception as e:
            return False
        return True

    def update(self, items):
        try:
            data = pickle.load(open(self.file,"rb"))
            data.update(items)
            pickle.dump(data,open(self.file,"wb"))
        except Exception as e:
            return False
        return True

    def purge(self):
        try:
            os.remove(self.file)
        except Exception as e:
            return False
        return True

    def remove(self, item):
        try:
            data = pickle.load(open(self.file,"rb"))
            data.remove(item)
            pickle.dump(data,open(self.file,"wb"))
        except Exception as e:
            return False
        return True

    def get_random(self):
        try:
            data = pickle.load(open(self.file,"rb"))
            length = len(data)
            if length:
                rand = random.randint(0, length - 1)
                i = 0
                for item in data:
                    if i == rand:
                        return item
                    i += 1
        except Exception as e:
            pass
        return None

class JsonLocalStorage(Storage):
    """docstring for JsonLocalStorage"""
    def __init__(self, file_path = '.proxy_engine_local_storage.json'):
        super(Storage, self).__init__()
        self.file = file_path
        if not os.path.exists(self.file):
            with open(self.file, 'w') as f:
                json.dump([], f)

    def insert(self, item):
        try:
            with open(self.file, 'r') as f:
                data = set(json.load(f))
                data.add(item)
                with open(self.file, 'w') as f:
                    json.dump(list(data), f)
        except Exception as e:
            return False
        return True

    def update(self, items):
        try:
            with open(self.file, 'r') as f:
                data = set(json.load(f))
                data.update(items)
                with open(self.file, 'w') as f:
                    json.dump(list(data), f)
        except Exception as e:
            print(e)
            return False
        return True

    def purge(self):
        try:
            os.remove(self.file)
        except Exception as e:
            return False
        return True

    def remove(self, item):
        try:
            with open(self.file, 'r') as f:
                data = set(json.load(f))
                data.remove(item)
                with open(self.file, 'w') as f:
                    json.dump(list(data), f)
        except Exception as e:
            return False
        return True

    def get_random(self):
        try:
            with open(self.file, 'r') as f:
                data = set(json.load(f))
                length = len(data)
                if length:
                    rand = random.randint(0, length - 1)
                    i = 0
                    for item in data:
                        if i == rand:
                            return item
                        i += 1
        except Exception as e:
            pass
        return None
