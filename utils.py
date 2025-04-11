import json
import requests

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_and_customize_payload(template_path, entity_type, artikelnummer, attributes, relationships, relationship_attributes):
    with open(template_path, "r", encoding="utf-8") as f:
        template = json.load(f)

    json_str = json.dumps(template)
    json_str = json_str.replace("REPLACE_ENTITY", entity_type)
    json_str = json_str.replace("REPLACE_ARTNR", artikelnummer)
    json_str = json_str.replace('"REPLACE_ATTRIBUTES"', json.dumps(attributes))
    json_str = json_str.replace('"REPLACE_RELATIONSHIPS"', json.dumps(relationships))
    json_str = json_str.replace('"REPLACE_RELATIONSHIPATTR"', json.dumps(relationship_attributes))

    return json.loads(json_str)

def call_api(url, payload, headers):
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()
