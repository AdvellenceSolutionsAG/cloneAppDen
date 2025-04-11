# MDM Clone App

A streamlined tool for cloning complex MDM (Master Data Management) entities like articles, supplier articles, trade items, and purchase/sales conditions — all within the same environment.

---

## 🔧 Features

- Clone mode with automatic new ID generation and correct relation rewriting
- Entity-type-based clone configuration (e.g., for exartikel, exlieferantenartikel, etc.)
- Simple UI powered by Streamlit
- URL-based access with pre-filled identifiers
- Environment configuration via Azure App Settings or `.env`
- Debug mode (data is only exported, not uploaded)

---

## 🧱 Project Structure

```plaintext
├── main.py                 # Executes the clone process
├── ui.py                   # Streamlit UI
├── utils.py                # Helper functions (payload creation, file handling)
├── env_config.py           # Loads API settings from environment variables
├── config/
│   └── clone/              # Entity-based clone configs (e.g., exartikel_STANDARD.json)
├── payloads/
│   └── template.json       # Payload template with placeholders
├── data/                   # Stores exported and upload-ready JSON files
├── assets/
│   └── logo.png            # Company logo used in UI
└── requirements.txt        # Python dependencies
```

---

## 🚀 Usage

### 🅰️ Web UI (recommended)

Start the UI locally:

```bash
streamlit run ui.py
```

Then open in browser with a pre-filled URL like:

```
http://localhost:8501/?entity_type=exartikel&identifier=1008276
```

You’ll see:
- Read-only view of entity type + identifier
- Matching clone configurations (with display names)
- One-click clone execution

> Sample screenshot:

![Streamlit UI Screenshot](assets/streamlit_ui.png)

---

### 🅱️ CLI (optional)

```bash
python main.py --clone exartikel_STANDARD --articlenr 1008276
```

---

## ⚙️ Configuration via Environment Variables

Use either a `.env` file (local) or Azure App Settings (recommended for production):

```env
API_URL_GET=https://your.domain/api/entityappservice/get
API_URL_UPLOAD=https://your.domain/blob/container/Filename
RDP_USER_ID=user@domain.com
RDP_USER_EMAIL=user@domain.com
RDP_CLIENT_ID=abc123
RDP_CLIENT_SECRET=xyz456
```

---

## 🧪 Clone Config Format (example: `config/clone/exartikel_STANDARD.json`)

```json
{
  "display_name": "Standard Clone – Artikel",
  "clone": true,
  "debug": false,
  "identifier_attribute": "axartikelnrsap",
  "entity_type": "exartikel",
  "entity_configs": [
    {
      "typ": "exartikel",
      "attributes": [...],
      "relationships": [...],
      "relationship_attributes": [...]
    },
    {
      "typ": "exlieferantenartikel",
      "attributes": [...],
      "relationships": [...],
      "relationship_attributes": [...]
    }
  ]
}
```

---

## 💡 Tips

- Add more clone configs under `config/clone/`
- Use `debug: true` to skip upload and only export entities
- Streamlit UI only shows configs that match the `entity_type` passed in the URL

---

Made with AI magic 🪄 by Simone