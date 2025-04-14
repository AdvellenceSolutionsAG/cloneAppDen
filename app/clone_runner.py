# Importiere Funktionen für Entity-Export, ID-Vergabe & Relationen, Upload und JSON-Speicherung
from app.entity_exporter import fetch_entities
from app.id_mapper import assign_new_ids_and_update_relations
from app.entity_uploader import upload_entities
from app.supplier_switch import handle_supplier_switch
from utils.helpers import save_json


def run_clone_process(identifier, sync_config, env_config, template_path, data_dir, supplier_nr=None):
    """
    Führt den gesamten Klon-Prozess aus:
    - Lädt Entitäten anhand der Konfiguration und Identifier
    - Führt optional das Klonen mit neuen IDs durch
    - Optional: Lieferantenwechsel-Prozess
    - Speichert die Daten lokal
    - Lädt die Daten hoch (sofern kein Debug-Modus aktiv ist)

    Parameter:
        identifier (str): Identifier (z.B. Artikelnummer) der zu klonenden Entität
        sync_config (dict): Enthält die Clone-Konfiguration (welche Entitäten, Attribute, etc.)
        env_config (dict): Umgebungskonfiguration (URLs, Header)
        template_path (str): Pfad zur Payload-Vorlage
        data_dir (str): Ordner für Zwischenspeicher (JSON-Dateien)
        supplier_nr (str, optional): Neue Lieferantennummer für Lieferantenwechsel-Prozess

    Rückgabe:
        Tuple (new_sap_id, entity_type): Neue SAP-ID (falls erzeugt), Entitätstyp
    """

    # Konfigurationswerte auslesen
    entity_type = sync_config["entity_type"]
    identifier_attribute = sync_config["identifier_attribute"]
    entity_configs = sync_config["entity_configs"]
    debug_mode = sync_config.get("debug", False)
    clone_mode = sync_config.get("clone", False)

    print(f"\n[INFO] Starte Verarbeitung für: {identifier}")

    # Daten aus MDM abrufen (gemäss Konfiguration)
    alle_entities = fetch_entities(identifier, entity_configs, env_config, template_path)

    new_sap_id = None

    # Sonderfall: Lieferantenwechsel-Prozess
    if sync_config.get("process_type") == "lieferantenwechsel" and supplier_nr:
        print("[INFO] Lieferantenwechsel-Prozess erkannt – führe Verarbeitung aus...")
        alle_entities = handle_supplier_switch(
            alle_entities,
            identifier,
            supplier_nr,
            env_config
        )

    # Falls Klon-Modus aktiv, neue IDs zuweisen und Relationen aktualisieren
    elif clone_mode:
        alle_entities, id_map, new_sap_id = assign_new_ids_and_update_relations(alle_entities, identifier)
        save_json(id_map, f"{data_dir}/id_mapping.json")  # Speichert Mapping alte→neue IDs

    # Entitäten lokal speichern (unabhängig von Debug- oder Klonmodus)
    save_json(alle_entities, f"{data_dir}/get_entities.json")

    # Nur Debug: keine Übertragung, JSON-Datei im Ziel-Format schreiben
    if debug_mode:
        print("\n[DEBUG] Debug-Modus aktiv – keine Daten werden gesendet.")
        save_json({
            "request": {"returnRequest": False, "requestId": "debug", "taskId": "debug"},
            "response": {
                "status": "success",
                "totalRecords": len(alle_entities),
                "entities": alle_entities
            }
        }, f"{data_dir}/send_entities.json")
    else:
        # Übertrage Daten per PUT auf Zielsystem
        upload_entities(alle_entities, env_config, sync_config)

    # Gebe neue SAP-ID (falls vorhanden) und Entitätstyp zurück
    return new_sap_id, entity_type
