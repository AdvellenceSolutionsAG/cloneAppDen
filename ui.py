import streamlit as st
import os
import json
import subprocess
import requests
import utils.env_config as env_config
import utils.helpers as helpers

# --- URL-Parameter lesen ---
params = st.query_params
identifier = params.get("identifier", "")
entity_type = params.get("entity_type", "")

# --- Template für API-Requests ---
TEMPLATE_PATH_EXISTING_SUPPLIERS = "payloads/template_get_existing_suppliers.json"
TEMPLATE_PATH_EXISTING_SUPPLIERS_DATA = "payloads/template_get_existing_suppliers_data.json"

# --- Mapping für Anzeige ---
ENTITY_LABELS = {
    "exartikel": "Artikel",
    "extradeitem": "Trade Item",
    "exlieferantenartikel": "Lieferantenartikel",
    "exverkaufskond": "Verkaufskondition",
    "exeinkaufskond": "Einkaufskondition"
}

# --- Bestehende Lieferanten per API abrufen ---
def get_existing_suppliers(env_config):
    url = env_config["url_get"]
    headers = env_config["headers_get"]
    payload = helpers.load_and_customize_payload_existing_suppliers(TEMPLATE_PATH_EXISTING_SUPPLIERS, identifier)
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        supplier_infos = []

        for entity in data.get("response", {}).get("entities", []):
            rels = entity.get("data", {}).get("relationships", {}).get("relxliefzuart", [])
            for rel in rels:
                supplier_id = rel.get("relTo", {}).get("id")
                is_default = rel.get("attributes", {}).get("arelxregellieferant", {}).get("values", [{}])[0].get("value") is True
                if supplier_id:
                    supplier_infos.append({
                        "id": supplier_id,
                        "is_default": is_default
                    })

    except Exception as e:
        st.error(f"Keine Lieferantenbeziehungen gefunden: {e}")
        return [], None

    # Namen auflösen
    supplier_names = []
    default_index = 0
    for idx, sup in enumerate(supplier_infos):
        try:
            payload_data = helpers.load_and_customize_payload_existing_suppliers_data(TEMPLATE_PATH_EXISTING_SUPPLIERS_DATA, sup["id"])
            response_data = requests.post(url, json=payload_data, headers=headers)
            response_data.raise_for_status()
            entity = response_data.json().get("response", {}).get("entities", [{}])[0]
            name = entity.get("data", {}).get("attributes", {}).get("axmdmname", {}).get("values", [{}])[0].get("value")
            if name:
                supplier_names.append(name)
                if sup["is_default"]:
                    default_index = idx
        except Exception as e:
            st.warning(f"Name für Lieferant {sup['id']} konnte nicht geladen werden: {e}")

    return supplier_names, default_index

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

# --- Titel & Logo ---
st.image("assets/logo.png", width=200)
st.title("🔁 MDM Clone App")

# --- Entität & Identifier anzeigen ---
st.text_input("🧬 Entitätstyp", value=ENTITY_LABELS.get(entity_type, entity_type), disabled=True)
st.text_input("🆔 Identifier", value=identifier, disabled=True)

# --- Konfigs laden ---
available_configs = helpers.get_matching_clone_configs(entity_type) if entity_type else []
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
    env_config = env_config.get_env_config()

    # Bestehende Lieferanten laden
    lieferanten_namen, default_index = get_existing_suppliers(env_config)

    if lieferanten_namen:
        existing_supplier = st.selectbox(
            "Von welchem Lieferant soll geklont werden?",
            lieferanten_namen,
            index=default_index
        )

    # Freitextsuche nach Ziel-Lieferant
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
