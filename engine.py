#!/usr/bin/env python

import re
import signal
import sys
import time
import logging
from storage import JsonLocalStorage
from sites import Site
import configparser
logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    cf = configparser.ConfigParser()
    cf.read('config.ini')

    try:
        UA = cf.get('config', 'user-agent')
        INTERVAl = int(cf.get('config', 'interval'))
    except Exception as e:
        UA = ''
        INTERVAl = 10
        logger.info('Error read config: {}'.format(e))

    headers = {'user-agent': UA} if UA else {}

    url = 'http://www.xicidaili.com/nn/{page}'
    ip = re.compile(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>', re.I)
    port = re.compile(r'<td>(\d{1,5})</td>', re.I)

    storage = JsonLocalStorage()
    site = Site(storage, url, ip, port, 3, headers)
    try:
        while True:
            logger.info("Collecting...")
            site.collect()
            logger.info("Waiting {} seconds".format(INTERVAl))
            time.sleep(INTERVAl)
    except KeyboardInterrupt:
        logger.info("Good bye!!!")
        sys.exit()
