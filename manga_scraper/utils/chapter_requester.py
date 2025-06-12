# utils/chapter_requester.py

import scrapy

def request_next_chapter(spider):
    """
    Issue a Scrapy request for the next chapter.
    
    Parameters:
    - spider: an instance of BaseMangaSpider or its subclass, containing chapter state and request logic
    """
    spider.chapter_index += 1

    if spider.chapter_index < len(spider.chapter_list):
        next_chapter = spider.chapter_list[spider.chapter_index]
        yield scrapy.Request(
            url=spider.url_template.format(chapter=next_chapter),
            callback=spider.parse_chapter,
            meta={'chapter': next_chapter},
            errback=spider.handle_error
        )
    else:
        print("\n🎉 All chapters downloaded and converted!\n")
