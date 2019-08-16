###########################
#Rotating proxies settings#
###########################
# https://github.com/TeamHG-Memex/scrapy-rotating-proxies

DOWNLOADER_MIDDLEWARES = {
'scrapy_generator.RotatingProxyMiddleware': 610,
'scrapy_generator.middlewares.BanDetectionMiddleware': 620
}
"ROTATING_PROXY_LIST_PATH = 'proxy_list.txt'"

"ROTATING_PROXY_PAGE_RETRY_TIMES = 1"
"ROTATING_PROXY_BACKOFF_BASE = 3000000"
"ROTATING_PROXY_BACKOFF_CAP = 3000000"
