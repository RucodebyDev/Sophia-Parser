import lib.io as io
import lib.general as general
import lib.game_files as game_files
from lib.constants import FINDINGS_WIKI_ICONS
from lib.constants import INPUT_DIR
import re

paths = game_files.build_paths(INPUT_DIR)

all_text = io.load_languages(INPUT_DIR)["en"]
files_scr = io.load_json(paths["finding_text_table"])
audios_scr = io.load_json(paths["radio_table"])
prts_all_scr = io.load_json(paths["finding_single"])
prts_scr = io.load_json(paths["finding_group"])
category_scr = io.load_json(paths["finding_category"])

def get_type(s, category="Manuscripts"):
    if category in ("Peculiars", "Audio Records", "Reports"):
        return category
    return FINDINGS_WIKI_ICONS.get(s, s).replace("Finding_", "").replace("_", " ")

def get_category(s, text):
    category_map = {
        "collection": "Peculiars",
        "digital": "E-Files",
        "document": "Nexus Files",
        "media": "Audio Records",
        "paper": "Manuscripts",
        "report": "Reports"
    }
    if s in category_map:
        return category_map[s]
    return general.resolve_text(text, category_scr.get(s))

# Implement a polymorphism to use this func in other places if it would be needed
def create_single_finding(all_text, item_id, group=None):
    if group:
        return __create_single_finding_main(all_text, item_id, group)
    else:
        return __create_single_finding_by_id(all_text, item_id)

# Creating a finding to return
def __create_single_finding_main(all_text, item_id, group):
    item = prts_all_scr.get(item_id)
    
    if item is None:
        return None

    if group["category"] == "Audio Records":
        text = audios_scr.get(item["contentId"])
        if text:
            content = [ f'{re.sub(r" ?{.+?}", "", general.resolve_text(all_text, d["actorName"]["id"]))}: {general.resolve_text(all_text, d["radioText"]["id"])}' for d in text.get("radioSingleDataList") ]
    else:
        text = files_scr.get(item["contentId"])
        if text:
            content = [ general.resolve_text(all_text, d["content"]["id"]) for d in text.get("contentList") ]
    
    return  {
                "title": general.resolve_text(all_text, item["name"]),
                "internalID": item_id,
                "groupID": item["firstLvId"],
                "group_title": group["title"],
                "group_type": group["type"],
                "content": content
            }

# Getting a group of finding for main function
def __create_single_finding_by_id(all_text, item_id):
    if prts_all_scr.get(item_id) is None:
        return None

    tmp = prts_scr.get(prts_all_scr.get(item_id)["firstLvId"])
    group = {
        "title": general.resolve_text(all_text, tmp["name"]),
        "type": get_type( tmp["icon"], category=get_category(tmp["categoryId"], all_text) ),
    }

    return __create_single_finding_main(all_text, item_id, group=group)