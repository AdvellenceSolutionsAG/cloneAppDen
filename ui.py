import streamlit as st
import os
import json
import subprocess
import requests

# --- Mapping für Anzeige ---
ENTITY_LABELS = {
    "exartikel": "Artikel",
    "extradeitem": "Trade Item",
    "exlieferantenartikel": "Lieferantenartikel",
    "exverkaufskond": "Verkaufskondition",
    "exeinkaufskond": "Einkaufskondition"
}

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

# --- Lieferantensuche per API ---
def search_suppliers(query, env_config):
    url = env_config["url_get"]
    headers = env_config["headers_get"]
    payload = {
        "params": {
            "query": {
                "filters": {
                    "typesCriterion": ["exlieferant"],
                    "attributesCriterion": [
                        {
                            "axmdmname": {
                                "contains": f"*{query}*",
                                "type": "_STRING"
                            }
                        }
                    ]
                }
            },
            "fields": {
                "attributes": ["axmdmname"]
            }
        }
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return [
            e.get("data", {}).get("attributes", {}).get("axmdmname", {}).get("values", [{}])[0].get("value")
            for e in data.get("response", {}).get("entities", [])
        ]
    except Exception as e:
        st.error(f"Fehler beim Abrufen der Lieferanten: {e}")
        return []

# --- URL-Parameter lesen ---
params = st.query_params
identifier = params.get("identifier", "")
entity_type = params.get("entity_type", "")

# --- Titel & Logo ---
st.image("assets/logo.png", width=200)
st.title("🔁 MDM Clone App")

# --- Entität & Identifier anzeigen ---
st.text_input("🧬 Entitätstyp", value=ENTITY_LABELS.get(entity_type, entity_type), disabled=True)
st.text_input("🆔 Identifier", value=identifier, disabled=True)

# --- Konfigs laden ---
available_configs = get_matching_clone_configs(entity_type) if entity_type else []
config_display_names = ["Bitte Klon-Konfiguration wählen..."] + [c["display_name"] for c in available_configs]
config_filename_map = {c["display_name"]: c["filename"] for c in available_configs}

# --- Auswahl Konfiguration ---
selected_display = st.selectbox("🧩 Klon-Konfiguration wählen", config_display_names, index=0)
selected_config = config_filename_map.get(selected_display)

# --- Lieferantensuche (nur bei Lieferantenwechsel) ---
supplier_nr = None
suchtext = ""
lieferant_ausgewaehlt = False

if selected_display and "Lieferanten Wechsel" in selected_display:
    env_config = {
        "url_get": os.getenv("API_URL_GET"),
        "headers_get": {
            "x-rdp-version": "8.1",
            "x-rdp-clientId": os.getenv("RDP_CLIENT_ID"),
            "x-rdp-userId": os.getenv("RDP_USER_ID"),
            "x-rdp-useremail": os.getenv("RDP_USER_EMAIL"),
            "auth-client-id": os.getenv("RDP_CLIENT_ID"),
            "auth-client-secret": os.getenv("RDP_CLIENT_SECRET"),
            "Content-Type": "application/json"
        }
    }

    suchtext = st.text_input("🔍 Lieferant suchen")
    if len(suchtext) >= 3:
        vorschlaege = search_suppliers(suchtext, env_config)
        if vorschlaege:
            supplier_nr = st.selectbox("📦 Lieferant auswählen", vorschlaege)
            lieferant_ausgewaehlt = supplier_nr is not None
        else:
            st.info("Keine Treffer gefunden.")

# --- Bedingungen für Button prüfen ---
config_ausgewaehlt = selected_config is not None
ist_lieferantenwechsel = selected_display and "Lieferanten Wechsel" in selected_display
alle_bedingungen_ok = (
    config_ausgewaehlt
    and identifier
    and entity_type
    and (not ist_lieferantenwechsel or lieferant_ausgewaehlt)
)

# --- Button nur anzeigen, wenn Bedingungen erfüllt ---
if alle_bedingungen_ok:
    if st.button("🚀 Klonen starten"):
        command = f"python main.py --clone {selected_config} --articlenr {identifier}"
        if supplier_nr:
            command += f" --supplier {supplier_nr}"

        st.text(f"Führe aus: {command}")

        with st.spinner("Bitte warten – Klonvorgang läuft..."):
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            st.code(result.stdout)
            if result.stderr:
                st.error(result.stderr)

# --- Footer ---
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'>Made with ❤️ by <strong>Advellence Solutions AG</strong></div>", unsafe_allow_html=True)
