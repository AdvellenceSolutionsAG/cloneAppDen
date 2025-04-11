import argparse
import os
import requests
import json
import uuid
from collections import defaultdict
from utils import load_json, save_json, load_and_customize_payload
from env_config import get_env_config

# --- Argumente verarbeiten ---
parser = argparse.ArgumentParser(description="Denner Clone App")
parser.add_argument("--clone", dest="clone_config", help="CloneConfig-Datei (z.B. exartikel_STANDARD)")
parser.add_argument("--articlenr", dest="articlenr", help="Artikelnummer oder Identifier")
args = parser.parse_args()

# --- Dateipfade definieren ---
CLONE_DIR = "config/clone"
DATA_DIR = "data"
TEMPLATE_PATH = "payloads/template.json"

# --- Konfigurationen laden ---
env_config = get_env_config()
clone_file = args.clone_config or "default_sync"
sync_config = load_json(os.path.join(CLONE_DIR, f"{clone_file}.json"))

# --- Identifier verarbeiten ---
identifier = args.articlenr or sync_config.get("identifier")
if not identifier:
    raise ValueError("Keine Artikelnummer bzw. kein Identifier übergeben.")

# --- Einstellungen aus Konfiguration ---
entity_type = sync_config["entity_type"]
identifier_attribute = sync_config["identifier_attribute"]
entity_configs = sync_config["entity_configs"]
debug_mode = sync_config.get("debug", False)
clone_mode = sync_config.get("clone", False)

alle_entities = []

# --- Abfrage der konfigurierten Entitäten ---
print(f"\n[INFO] Verarbeitung Identifier: {identifier}")
for cfg in entity_configs:
    payload = load_and_customize_payload(
        template_path=TEMPLATE_PATH,
        entity_type=cfg["typ"],
        artikelnummer=identifier,  # bleibt wegen Payload-Funktion
        attributes=cfg["attributes"],
        relationships=cfg["relationships"],
        relationship_attributes=cfg["relationship_attributes"]
    )

    response = requests.post(env_config["url_get"], json=payload, headers=env_config["headers_get"])
    response.raise_for_status()
    result = response.json()

    entities = result.get("response", {}).get("entities", [])
    if entities:
        print(f"[OK] {cfg['typ']}: {len(entities)} Eintrag gefunden.")
        alle_entities.extend(entities)
    else:
        print(f"[WARN] {cfg['typ']}: Kein Eintrag gefunden.")

# --- Clone Mode: Neue IDs vergeben & Relationen anpassen ---
if clone_mode:
    print("\n[CLONE] Starte Klon-Modus mit neuer ID-Vergabe...")
    cloned_ids = defaultdict(dict)

    for entity in alle_entities:
        typ = entity.get("type")
        old_id = entity.get("id")
        new_id = str(uuid.uuid4())
        cloned_ids[typ][old_id] = new_id

    cloned_entities = []
    for entity in alle_entities:
        typ = entity.get("type")
        old_id = entity.get("id")
        new_id = cloned_ids[typ][old_id]

        entity["id"] = new_id
        entity.pop("name", None)

        rels = entity.get("data", {}).get("relationships", {})
        for rel_typ, rel_list in rels.items():
            for rel in rel_list:
                if "relTo" in rel:
                    target_type = rel["relTo"].get("type")
                    target_id = rel["relTo"].get("id")
                    if target_id in cloned_ids.get(target_type, {}):
                        rel["relTo"]["id"] = cloned_ids[target_type][target_id]

        cloned_entities.append(entity)

    alle_entities = cloned_entities
    save_json(cloned_ids, os.path.join(DATA_DIR, "id_mapping.json"))

# --- Daten speichern ---
save_json(alle_entities, os.path.join(DATA_DIR, "get_entities.json"))

# --- Debug-Modus: Kein Upload, nur speichern ---
if debug_mode:
    print("\n[DEBUG] Debug-Modus aktiv – keine Daten werden gesendet.")
    save_json({
        "request": {"returnRequest": False, "requestId": "debug", "taskId": "debug"},
        "response": {
            "status": "success",
            "totalRecords": len(alle_entities),
            "entities": alle_entities
        }
    }, os.path.join(DATA_DIR, "send_entities.json"))
else:
    # --- Upload durchführen ---
    print("\n[INFO] Starte Upload zur Zielumgebung...")
    with open(os.path.join(DATA_DIR, "get_entities.json"), "rb") as f:
        filename = f"{clone_file}-{str(uuid.uuid4())}.json"
        url = env_config["url"].replace("Filename", filename)
        print(f"[INFO] URL: {url}")
        response = requests.put(url, headers=env_config["headers"], data=f)
        response.raise_for_status()
        print("[SUCCESS] Upload abgeschlossen und Antwort gespeichert.")
