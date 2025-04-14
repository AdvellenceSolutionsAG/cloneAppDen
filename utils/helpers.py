import json
import requests

def load_json(path):
    """
    Lädt eine JSON-Datei von einem gegebenen Pfad.

    Args:
        path (str): Der Pfad zur Datei.

    Returns:
        dict: Der geladene JSON-Inhalt als Python-Dictionary.
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(data, path):
    """
    Speichert ein Dictionary als JSON-Datei an einem gegebenen Pfad.

    Args:
        data (dict): Die zu speichernden Daten.
        path (str): Der Pfad, an dem die Datei gespeichert werden soll.
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_and_customize_payload(template_path, entity_type, artikelnummer, attributes, relationships, relationship_attributes):
    """
    Lädt ein JSON-Template und ersetzt Platzhalter durch echte Werte.

    Args:
        template_path (str): Pfad zur Template-Datei.
        entity_type (str): Der Entitätstyp, z. B. "exartikel".
        artikelnummer (str): Der Identifier bzw. Artikelnummer.
        attributes (list): Liste der gewünschten Attribute.
        relationships (list): Liste der gewünschten Relationen.
        relationship_attributes (list): Liste der gewünschten Beziehungsattribute.

    Returns:
        dict: Das angepasste Payload als Dictionary.
    """
    with open(template_path, "r", encoding="utf-8") as f:
        template = json.load(f)

    # Ersetze Platzhalter im JSON-Template
    json_str = json.dumps(template)
    json_str = json_str.replace("REPLACE_ENTITY", entity_type)
    json_str = json_str.replace("REPLACE_ARTNR", artikelnummer)
    json_str = json_str.replace('"REPLACE_ATTRIBUTES"', json.dumps(attributes))
    json_str = json_str.replace('"REPLACE_RELATIONSHIPS"', json.dumps(relationships))
    json_str = json_str.replace('"REPLACE_RELATIONSHIPATTR"', json.dumps(relationship_attributes))

    return json.loads(json_str)

def post_request(url, payload, headers):
    """
    Führt einen POST-Request an die angegebene URL mit Payload und Headern durch.

    Args:
        url (str): Die Ziel-URL.
        payload (dict): Der JSON-Body für den Request.
        headers (dict): HTTP-Header, inkl. Authentifizierung etc.

    Returns:
        dict: Die JSON-Antwort vom Server.
    """
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()
