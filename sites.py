#!/usr/bin/env python
import requests
import logging
import retrying
from exceptions import EmptyListException, ListNotMatchException
from proxy_atom import ProxyAtom
from fake_useragent import UserAgent
from settings import TEST_URI

ua = UserAgent()
logger = logging.getLogger(__name__)

class Site(object):
    def __init__(self, storage, target_url, ip_parttern, port_pattern, page_total = 5, headers = {}):
        super(Site, self).__init__()
        self._storage = storage
        self._target_url = target_url
        self._ip_parttern = ip_parttern
        self._port_pattern = port_pattern
        self._page_total = page_total
        
    def parser(self, ip_list_raw, port_list_raw):
        return ip_list_raw, port_list_raw

    @retrying.retry(stop_max_attempt_number=3)
    def fetch_proxies(self, page_num = None):
        try:
            url = self._target_url.format(page=page_num) if page_num else self._target_url
            text = self._get_content(url)
            ip_list_raw = self._ip_parttern.findall(text)
            port_list_raw = self._port_pattern.findall(text)

            if not len(ip_list_raw) or not len(port_list_raw):
                raise EmptyListException()

            if len(ip_list_raw) != len(port_list_raw):
                raise ListNotMatchException()

        except Exception as e:
            logger.error("Request error: {}".format(e))
            return ProxyAtom([], [])

        ip_list, port_list =self.parser(ip_list_raw, port_list_raw)
        return ProxyAtom(ip_list, port_list)

    def _get_content(self, url):
        response = requests.get(url, timeout=5, headers={'user-agent': ua.random})
        logger.info("response status code: {} {}".format(url, response.status_code))
        return response.text

    def collect(self):
        for page in range(1, self._page_total):
            atoms = self.fetch_proxies(page)
            for item in atoms.items:
                if self._validate(item):
                    self._storage.insert(item)
                    logger.info("item: ## {}".format(item))

    def _validate(self, proxy_raw):
        try:
            r=requests.get(TEST_URI, proxies={'http': proxy_raw,
                'https': proxy_raw}, headers={'user-agent': ua.random}, timeout=5)
            logger.info("StatusCode: ## {} ## {}".format(proxy_raw, r.status_code))
            if r.status_code == 200:
                return True
            return False
        except Exception as e:
            pass
            logger.error("Error: ## {} ## {}".format(proxy_raw, e))