def parse_manga_groups(response, chapter_xpath, volume_xpath, extra_xpath):
    def extract_group(xpath_query, group_id, group_name):
        container = response.xpath(xpath_query)
        if not container:
            return None

        elements = container.css("ul li a")
        chapters = []
        for a in elements:
            href = a.attrib.get("href", "")
            title = a.attrib.get("title", "")
            if not href or not title:
                continue
            chap_id = href.split("/")[-1].split(".")[-2]
            chapters.append({"type": group_id, "name": title, "id": chap_id})

        return {"count": len(chapters), "name": group_name, "chapters": chapters}

    groups_config = [
        {"key": "chapters", "id": 1, "name": "单话", "xpath": chapter_xpath},
        {"key": "volumes", "id": 2, "name": "单行本", "xpath": volume_xpath},
        {"key": "extras", "id": 3, "name": "番外篇", "xpath": extra_xpath},
    ]

    result = {"build": {"type": []}, "groups": {}}

    for group in groups_config:
        data = extract_group(group["xpath"], group["id"], group["name"])
        if data:
            result["build"]["type"].append({"id": group["id"], "name": group["name"]})
            result["groups"][group["key"]] = data

    return result
