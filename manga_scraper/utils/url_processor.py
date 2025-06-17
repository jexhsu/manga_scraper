def process_chapter_url(spider, chapter_map, chapter_list, chapter_index):
    """
    Process chapter URL and metadata based on spider configuration.
    
    Args:
        spider (scrapy.Spider): The spider instance.
        chapter_map (dict): Mapping of chapter keys to values.
        chapter_list (list): List of chapter values.
        chapter_index (int): Current chapter index.
    
    Returns:
        tuple: (chapter_url, metadata_dict)
    """
    if chapter_map:
        chapter_map_key = list(chapter_map.keys())[chapter_index]
        chapter_map_val = list(chapter_map.values())[chapter_index]
    else:
        chapter_list_val = chapter_list[chapter_index]

    chapter = chapter_map_val if chapter_map else chapter_list_val
    chapter_url = spider.url_template.format(chapter=chapter)
    meta = {
        'chapter': chapter_map_key if chapter_map else chapter_list_val
    }
    
    return chapter_url, meta