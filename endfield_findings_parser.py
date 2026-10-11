import lib.io as io
import lib.general as general
import lib.game_files as game_files
import lib.constants as const
import lib.helpers.findings as findings_helper
import os

# Output files
INVESTIGATIONS_PAGE_OUTPUT = os.path.join(const.OUTPUT_DIR, "investigations_page_data.txt")
NEXUS_PAGE_OUTPUT = os.path.join(const.OUTPUT_DIR, "nexus_files_page_data.txt")
AUDIO_PAGE_OUTPUT = os.path.join(const.OUTPUT_DIR, "audio_records_page_data.txt")
FINDINGS_PAGE_OUTPUT = os.path.join(const.OUTPUT_DIR, "findings_page_data.txt")

os.makedirs(const.OUTPUT_DIR, exist_ok=True)

paths = game_files.build_paths(const.INPUT_DIR)

all_text = io.load_languages(const.INPUT_DIR)["en"]
files_scr = io.load_json(paths["finding_text_table"])
audios_scr = io.load_json(paths["radio_table"])
prts_all_scr = io.load_json(paths["finding_single"])
prts_scr = io.load_json(paths["finding_group"])
category_scr = io.load_json(paths["finding_category"])
investig_scr = io.load_json(paths["investigate_table"])
comments_scr = io.load_json(paths["investigate_comment_table"])

all_singles_list = {}
all_groups_list = []

for value in prts_scr.values():
	item_category = findings_helper.get_category(value["categoryId"], all_text)
	item_title = general.resolve_text(all_text, value["name"]["id"])
	item_icon = const.FINDINGS_WIKI_ICONS.get(value["icon"], value["icon"]) + ".png"
	if not item_icon.startswith("Finding_") and item_category == "Peculiars":
		item_icon = "Peculiar_" + general.sanitize_image_name(item_title) + ".png"

	item = {
		"title": item_title,
		"category": item_category,
		"type": findings_helper.get_type(value["icon"], category=item_category),
		"icon": item_icon,
		"internalID": value["firstLvId"],
		"internalIconID": value["icon"],
		"content": []
	}

	if not value["itemIds"]:
		print(f'Item "{item_title}"({value["firstLvId"]}) haven\'t any notes. Probably broken or outdated data')
		item["content"].append("!!!BROKEN!!!")

	for item_id in value["itemIds"]:
		note = findings_helper.create_single_finding(all_text, item_id, group=item)

		item["content"].append(note)
		all_singles_list[note.get("internalID")] = note

	if item["category"] == "Reports": continue
	else: all_groups_list.append(item) 

with open(AUDIO_PAGE_OUTPUT, "w", encoding="utf-8") as out:
	for f in filter(lambda d: d["category"] == "Audio Records", all_groups_list):
		clear_text = ""
		for line in f["content"][0]["content"]:
			split = line.split(":", 1)
			clear_text += f"{{{{Audio Record cell|{split[0]}|{split[1]}}}}}" + "\n"
		out.write(f"""{{{{-start-}}}}
'''{f['title']}'''
{{{{Audio Record Head}}}}
{clear_text}
{{{{-stop-}}}}

""")

with open(NEXUS_PAGE_OUTPUT, "w", encoding="utf-8") as out:
	for f in filter(lambda d: d["category"] == "Nexus Files", all_groups_list):
		desc = '\n\n'.join(f["content"][0]["content"])
		out.write(f"""{{{{-start-}}}}
'''{f['title']}'''
{{{{Nexus Files
| title = {f['title']}
| desc = {desc}
}}}}
{{{{-stop-}}}}

""")

with open(FINDINGS_PAGE_OUTPUT, "w", encoding="utf-8") as out:
	for f in filter(lambda d: not d["category"] in ("Audio Records", "Nexus Files"), all_groups_list):		
		out.write(f"""{{{{-start-}}}}
'''{f['title']}'''

{{{{-stop-}}}}

""")


with open(INVESTIGATIONS_PAGE_OUTPUT, "w", encoding="utf-8") as out:

	for value in investig_scr.values():
		title = general.resolve_text(all_text, value["name"]),
		desc = general.resolve_text(all_text, value["desc"]),
		icon = const.INVESTIGATION_ICONS.get(value["type"], "Invalid"),
		internalID = value["id"],
		unlockReport = all_singles_list[value["unlockPrts"]]
		sections = []

		for section in value["categoryDataList"]:
			sections.append({
				"name": general.resolve_text(all_text, section["name"]),
				"commentList": [
					{
						"text": general.resolve_text(all_text, comments_scr.get(c).get("desc")),
						"ID": c
					} for c in section["noteIdList"]
				],
				"findings": list(all_singles_list[f] for f in section["collectionIdList"])
			})

	out.write(f"""{{{{-start-}}}}
'''{title}'''

{{{{-stop-}}}}

""")