import json

# Load your original JSON
with open("en.json", "r", encoding="utf-8") as f:
    data = json.load(f)

result = {"achievement": {}}


def extract_ids(item, output_dict):
    """Recursively extract achievement ids."""
    if isinstance(item, dict):
        if "id" in item:
            output_dict[str(item["id"])] = False
    elif isinstance(item, list):
        for sub in item:
            extract_ids(sub, output_dict)


for category_index, category in data.items():
    category_dict = {}

    achievements = category.get("achievements", [])

    for entry in achievements:
        extract_ids(entry, category_dict)

    result["achievement"][str(category_index)] = category_dict


# Save converted JSON
with open("raw.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=4)

print("Conversion complete.")