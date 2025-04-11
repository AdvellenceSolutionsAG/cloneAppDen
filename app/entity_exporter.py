import requests
from utils.helpers import load_and_customize_payload


def fetch_entities(identifier, entity_configs, env_config, template_path):
    all_entities = []
    for cfg in entity_configs:
        payload = load_and_customize_payload(
            template_path=template_path,
            entity_type=cfg["typ"],
            artikelnummer=identifier,
            attributes=cfg["attributes"],
            relationships=cfg["relationships"],
            relationship_attributes=cfg["relationship_attributes"]
        )

        response = requests.post(env_config["url_get"], json=payload, headers=env_config["headers_get"])
        response.raise_for_status()
        result = response.json()
        entities = result.get("response", {}).get("entities", [])

        if entities:
            print(f"[OK] {cfg['typ']}: {len(entities)} Eintrag(e) gefunden.")
            all_entities.extend(entities)
        else:
            print(f"[HINWEIS] {cfg['typ']}: Kein Eintrag gefunden.")

    return all_entities