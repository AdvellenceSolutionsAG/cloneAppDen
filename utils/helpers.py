import json
import requests
import os
import ui as ui

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

def load_and_customize_payload_existing_suppliers(template_path, artikelnummer):
    """
    Lädt ein JSON-Template für Abfrage der bestehenden Lieferanten und ersetzt Platzhalter durch echte Werte.

    Args:
        template_path (str): Pfad zur Template-Datei.
        artikelnummer (str): Der Identifier bzw. Artikelnummer.

    Returns:
        dict: Das angepasste Payload als Dictionary.
    """
    with open(template_path, "r", encoding="utf-8") as f:
        template = json.load(f)

    # Ersetze Platzhalter im JSON-Template
    json_str = json.dumps(template)
    json_str = json_str.replace("REPLACE_ARTNR", artikelnummer)

    return json.loads(json_str)


def load_and_customize_payload_existing_suppliers_data(template_path, supplier_id):
    """
    Lädt ein JSON-Template für Abfrage der bestehenden Lieferanten und ersetzt Platzhalter durch echte Werte.

    Args:
        template_path (str): Pfad zur Template-Datei.
        supplier_id (str): Der Identifier des Lieferanten.

    Returns:
        dict: Das angepasste Payload als Dictionary.
    """
    with open(template_path, "r", encoding="utf-8") as f:
        template = json.load(f)

    # Ersetze Platzhalter im JSON-Template
    json_str = json.dumps(template)
    json_str = json_str.replace("REPLACE_ID", supplier_id)

    return json.loads(json_str)

# --- Hilfsfunktion: Liste passender Konfigs für Entitätstyp ---
def get_matching_clone_configs(entity_type):
    folder = "config/clone"
    configs = []
    for fname in os.listdir(folder):
        if fname.endswith(".json") and fname.startswith(entity_type):
            path = os.path.join(folder, fname)
            with open(path, "r", encoding="utf-8") as f:
                config = json.load(f)
            display = config.get("display_name", fname.replace(".json", ""))
            configs.append({"filename": fname.replace(".json", ""), "display_name": display})
    return configs
