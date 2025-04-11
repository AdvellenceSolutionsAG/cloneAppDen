from app.entity_exporter import fetch_entities
from app.id_mapper import assign_new_ids_and_update_relations
from app.entity_uploader import upload_entities
from utils.helpers import save_json


def run_clone_process(identifier, sync_config, env_config, template_path, data_dir):
    entity_type = sync_config["entity_type"]
    identifier_attribute = sync_config["identifier_attribute"]
    entity_configs = sync_config["entity_configs"]
    debug_mode = sync_config.get("debug", False)
    clone_mode = sync_config.get("clone", False)

    print(f"\n[INFO] Starte Verarbeitung für: {identifier}")

    alle_entities = fetch_entities(identifier, entity_configs, env_config, template_path)

    new_sap_id = None
    if clone_mode:
        alle_entities, id_map, new_sap_id = assign_new_ids_and_update_relations(alle_entities, identifier)
        save_json(id_map, f"{data_dir}/id_mapping.json")

    save_json(alle_entities, f"{data_dir}/get_entities.json")

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
        upload_entities(alle_entities, env_config, sync_config)

    return new_sap_id, entity_type