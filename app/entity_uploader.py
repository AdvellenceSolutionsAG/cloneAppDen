import requests
import uuid
import os


def upload_entities(entities, env_config, sync_config):
    filename = f"{sync_config['clone_config']}-{uuid.uuid4()}.json"
    path = os.path.join("data", "get_entities.json")

    with open(path, "rb") as f:
        url = env_config["url"].replace("Filename", filename)
        print(f"[INFO] Upload-URL: {url}")
        response = requests.put(url, headers=env_config["headers"], data=f)
        response.raise_for_status()
        print("[SUCCESS] Upload erfolgreich abgeschlossen.")