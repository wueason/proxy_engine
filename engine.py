#!/usr/bin/env python
import gevent
from gevent import monkey; monkey.patch_all()
import requests
import re
import platform
import os
import sys
import logging
from storage import JsonLocalStorage
from sites import Site, ua
import argparse
from settings import TEST_URI, INTERVAL, VALIDATE_INTERVAL

logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')


parser = argparse.ArgumentParser()
parser.add_argument("--validate", help="with validate", action="store_true")
parser.add_argument("--nocollect", help="without collect", action="store_true")
args = parser.parse_args()

validate_on, collect_on = False, True
if args.validate:
    validate_on = True
    validate_logger = logging.getLogger('validate')
if args.nocollect:
    collect_on = False

logger = logging.getLogger('validate')

sysstr = platform.system()
abs_file = os.path.abspath(sys.argv[0])
if sysstr == 'Windows':
    seprator = "\\"
    abs_dir = abs_file[:abs_file.rfind("\\")]
else:
    seprator = "/"
    abs_dir = abs_file[:abs_file.rfind("/")]

storage = JsonLocalStorage()
cf = configparser.ConfigParser()
cf.read(abs_dir + seprator + 'config.ini')

def validate():
    errors = {}
    start = int(time.time())
    while True:
        try:
            proxy_raw = storage.get_random()
            r=requests.get(TEST_URI, proxies={'http': proxy_raw,
                'https': proxy_raw}, headers={'user-agent': ua.random}, timeout=10)
            validate_logger.info("StatusCode: ## {} ## {}".format(proxy_raw, r.status_code))
            if r.status_code != 200:
                raise Exception('status code is not 200')
        except Exception as e:
            if proxy_raw in errors:
                errors[proxy_raw] += 1
            else:
                errors[proxy_raw] = 1
        if proxy_raw in errors and errors[proxy_raw] > 10:
            validate_logger.info("Remove: ## {} ## {}".format(proxy_raw, errors[proxy_raw]))
            storage.remove(proxy_raw)
        gevent.sleep(VALIDATE_INTERVAL)
        if (int(time.time()) - start) > VALIDATE_INTERVAL*100:
            errors = {}

def collect():
    url = 'http://www.xicidaili.com/wt/{page}'
    ip = re.compile(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>', re.I)
    port = re.compile(r'<td>(\d{1,5})</td>', re.I)

    site = Site(storage, url, ip, port, 1817, headers)
    while True:
        logger.info("Collecting...")
        try:
            site.collect()
        except Exception as e:
            logger.error("Error: {}".format(e))
        logger.info("Waiting {} seconds".format(INTERVAL))
        gevent.sleep(INTERVAL)

if __name__ == '__main__':
    try:
        if not collect_on and not validate_on:
            logger.info("No feature selected!!!")
            sys.exit(0)
        if collect_on:
            collect_process = gevent.spawn(collect)
        if validate_on:
            validate_process = gevent.spawn(validate)
        if collect_on:
            collect_process.join()
        if validate_on:
            validate_process.join()
    except KeyboardInterrupt:
        logger.info("Good bye!!!")
        sys.exit(0)