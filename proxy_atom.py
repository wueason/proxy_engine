#!/usr/bin/env python

class ProxyAtom(object):
    """docstring for ProxyAtom"""
    def __init__(self, ips, ports):
        super(ProxyAtom, self).__init__()
        result = dict(zip(ips, ports))
        self.items = set([':'.join((host, port)) for host, port in result.items()])
