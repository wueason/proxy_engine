#!/usr/bin/env python
import gevent
from gevent import monkey; monkey.patch_all()
import requests
import re
import sys
import logging
from storage import JsonLocalStorage
from sites import Site
import configparser

logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

storage = JsonLocalStorage()
cf = configparser.ConfigParser()
cf.read('config.ini')

UA = ''
check_interval, interval = 10, 10
try:
    UA = cf.get('config', 'user-agent')
    interval = int(cf.get('config', 'interval'))
    check_interval = int(cf.get('config', 'check_interval'))
except Exception as e:
    logger.warning('Error read config: {}'.format(e))

headers = {'user-agent': UA} if UA else {}

logger = logging.getLogger('collect')
validate_logger = logging.getLogger('validate')

def validate():
    check_url = 'https://www.baidu.com'
    while True:
        try:
            proxy_raw = storage.get_random()
            r=requests.get(check_url, proxies={'http': proxy_raw,
                'https': proxy_raw}, headers=headers, timeout=10)
            validate_logger.info("StatusCode: ## {} ## {}".format(proxy_raw, r.status_code))
            if r.status_code != 200:
                storage.remove(proxy_raw)
        except Exception as e:
            storage.remove(proxy_raw)
            validate_logger.error("Error: ## {} ## {}".format(proxy_raw, e))
        gevent.sleep(check_interval)

def collect():
    url = 'http://www.xicidaili.com/wt/{page}'
    ip = re.compile(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>', re.I)
    port = re.compile(r'<td>(\d{1,5})</td>', re.I)

    site = Site(storage, url, ip, port, 5, headers)
    while True:
        logger.info("Collecting...")
        try:
            site.collect()
        except Exception as e:
            logger.error("Error: {}".format(e))
        logger.info("Waiting {} seconds".format(interval))
        gevent.sleep(interval)

if __name__ == '__main__':
    try:
        g1 = gevent.spawn(collect)
        g2 = gevent.spawn(validate)
        g1.join()
        g2.join()
    except KeyboardInterrupt:
        logger.info("Good bye!!!")
        sys.exit()
