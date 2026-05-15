import json

with open('canonical_tags.json', 'r') as f:
    json = json.load(f)

for key, data in json.items():
    for canonical, tags in data.items():
        print(canonical)
