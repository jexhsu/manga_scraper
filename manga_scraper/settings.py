# -*- coding: utf-8 -*-

# =============================================
# Basic Scrapy Project Configuration
# =============================================

# Project name
BOT_NAME = "manga_scraper"

# Spider modules location
SPIDER_MODULES = ["manga_scraper.spiders"]
NEWSPIDER_MODULE = "manga_scraper.spiders"

# Custom addons dictionary
ADDONS = {}

# Default encoding for feed exports
FEED_EXPORT_ENCODING = "utf-8"

# Database configuration
DATABASE_NAME = "manga_park"


# =============================================
# Crawler Behavior Settings
# =============================================

# Robots.txt compliance (disabled for scraping)
ROBOTSTXT_OBEY = False

# Crawling strategy (BFO = Breadth First Order)
DEPTH_PRIORITY = 1
SCHEDULER_ORDER = "BFO"

# Logging level (DEBUG for detailed output)
LOG_LEVEL = "DEBUG"


# =============================================
# Concurrency & Download Settings
# =============================================

# Global concurrent requests
CONCURRENT_REQUESTS = 16

# Domain-specific concurrency
CONCURRENT_REQUESTS_PER_DOMAIN = 5

# Download delay between requests (seconds)
DOWNLOAD_DELAY = 0

# Media download settings
MEDIA_ALLOW_REDIRECTS = True


# =============================================
# Playwright Configuration
# =============================================

# Playwright download handlers
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

# Browser type (chromium, firefox, webkit)
PLAYWRIGHT_BROWSER_TYPE = "chromium"

# Navigation timeout (milliseconds)
PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 600000

# Browser launch options
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,
    "timeout": 600000,
}

# Resource management
PLAYWRIGHT_MAX_PAGES_PER_CONTEXT = 8
PLAYWRIGHT_MAX_CONTEXTS = 4

# Request filtering (abort certain resource types)
PLAYWRIGHT_ABORT_REQUEST = lambda req: req.resource_type in {
    "font",
    "stylesheet",
    "image",
}


# =============================================
# Item Pipelines Configuration
# =============================================

from manga_scraper.spiders.manga_park import MangaParkSpider

# Image storage location
IMAGES_STORE = f"./downloads/{MangaParkSpider.name}/"
# Pipeline execution order
ITEM_PIPELINES = {
    "manga_scraper.pipelines.data_cleaning.MangaDataCleaningPipeline": 100,
    "manga_scraper.pipelines.download_img_2pdf.MangaDownloadPipeline": 200,
}


# =============================================
# Disabled/Commented Settings (For Reference)
# =============================================

# User agent configuration
# USER_AGENT = "manga_scraper (+http://www.yourdomain.com)"

# Cookie handling
# COOKIES_ENABLED = False

# Telnet console
# TELNETCONSOLE_ENABLED = False

# Default request headers
# DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
# }

# Spider middlewares
# SPIDER_MIDDLEWARES = {
#    "manga_scraper.middlewares.manga_scraperSpiderMiddleware": 543,
# }

# Downloader middlewares
# DOWNLOADER_MIDDLEWARES = {
#    "manga_scraper.middlewares.manga_scraperDownloaderMiddleware": 543,
# }

# Extensions
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# AutoThrottle settings
# AUTOTHROTTLE_ENABLED = True
# AUTOTHROTTLE_START_DELAY = 5
# AUTOTHROTTLE_MAX_DELAY = 60
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# AUTOTHROTTLE_DEBUG = False

# HTTP caching
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = "httpcache"
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"
