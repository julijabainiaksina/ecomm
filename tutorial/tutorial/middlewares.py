import os
import random,time
from scrapy.conf import settings
# class RandomUserAgentMiddleware(object):
#     def process_request(self, request, spider):
#         ua  = random.choice(settings.get('USER_AGENT_LIST'))
#         if ua:
#             request.headers.setdefault('User-Agent', ua)
#
#
# class ProxyMiddleware(object):
#     def process_request(self, request, spider):
#         proxy = self.get_random_proxy()
#         print("this is request ip:" + proxy)
#         request.meta['proxy'] = proxy
#
#     def process_response(self, request, response, spider):
#         if response.status != 200:
#             proxy = self.get_random_proxy()
#             print("this is response ip:" + proxy)
#             request.meta['proxy'] = proxy
#             return request
#         return response
#
#     def get_random_proxy(self):
#         while 1:
#             with open('/Users/ashelyliu/Documents/GitHub/ecomm/tutorial/tutorial/spiders/proxies.txt', 'r') as f:
#
#                 proxies = f.readlines()
#             if proxies:
#                 break
#             else:
#                 time.sleep(1)
#         proxy = random.choice(proxies).strip()
#         return proxy