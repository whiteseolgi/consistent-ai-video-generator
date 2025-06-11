import re


def parse_characters(text_block):
    characters = []
    if "기타:" in text_block:
        main_part, etc_part = text_block.split("기타:", 1)
    else:
        main_part, etc_part = text_block, ""

    entries = re.split(r"\n\d+\.\s", main_part)

    for entry in entries:
        if not entry.strip():
            continue

        lines = entry.strip().split("\n")
        attributes = {}
        name = ""

        for line in lines:
            if line.startswith("이름:"):
                name = line.split(":", 1)[1].strip()
            elif ":" in line:
                key, value = line.split(":", 1)
                attributes[key.strip()] = value.strip()

        if not name and lines:
            name = re.sub(r"^\d+\.\s*", "", lines[0]).strip()

        characters.append({
            "type": "character",
            "name": name,
            "attributes": attributes
        })

    if etc_part.strip():
        lines = [line.strip() for line in etc_part.strip().splitlines() if line.strip()]
        characters.append({
            "type": "character",
            "name": "기타",
            "attributes": {"기타 목록": lines}
        })

    return characters


def parse_locations(text_block):
    results = []
    if "기타:" in text_block:
        main_part, etc_part = text_block.split("기타:", 1)
    else:
        main_part, etc_part = text_block, ""

    entries = re.split(r"\n\s*장소\s*\d+\s*\n", main_part)

    for entry in entries:
        if "장소명:" not in entry:
            continue
        attributes = {}
        name = ""
        for line in entry.strip().split("\n"):
            if line.startswith("장소명:"):
                name = line.split(":", 1)[1].strip()
            elif ":" in line:
                key, value = line.split(":", 1)
                attributes[key.strip()] = value.strip()
        results.append({"type": "location", "name": name, "attributes": attributes})

    if etc_part.strip():
        items = [item.strip(" ,") for item in etc_part.strip().split(",") if item.strip()]
        results.append({
            "type": "location",
            "name": "기타",
            "attributes": {"기타 목록": items}
        })

    return results


def parse_objects(text_block):
    results = []
    if "기타:" in text_block:
        main_part, etc_part = text_block.split("기타:", 1)
    else:
        main_part, etc_part = text_block, ""

    entries = re.split(r"\n\d+\.\s", main_part)

    for entry in entries:
        if not entry.strip():
            continue

        lines = entry.strip().split("\n")
        name = re.sub(r"^\d+\.\s*", "", lines[0].strip()) if lines else ""
        attributes = {}

        for line in lines[1:]:
            if ":" in line:
                key, value = line.split(":", 1)
                attributes[key.strip()] = value.strip()

        results.append({
            "type": "object",
            "name": name,
            "attributes": attributes
        })

    if etc_part.strip():
        raw = etc_part.strip().replace("기타:", "")
        items = [item.strip() + ")" for item in raw.split("), ") if item.strip()]
        results.append({
            "type": "object",
            "name": "기타",
            "attributes": {"기타 목록": items}
        })

    return results
