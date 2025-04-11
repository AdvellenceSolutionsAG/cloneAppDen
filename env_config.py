import os
from dotenv import load_dotenv
load_dotenv()

def get_env_config():
    return {
        "url_get": os.getenv("API_URL_GET"),
        "headers_get": {
            "x-rdp-version": "8.1",
            "x-rdp-clientId": "rdpclient",
            "x-rdp-userId": os.getenv("RDP_USER_ID"),
            "x-rdp-useremail": os.getenv("RDP_USER_EMAIL"),
            "x-rdp-userRoles": "[\"systemadmin\"]",
            "auth-client-id": os.getenv("RDP_CLIENT_ID"),
            "auth-client-secret": os.getenv("RDP_CLIENT_SECRET"),
            "Content-Type": "application/json"
        },
        "url": os.getenv("API_URL_UPLOAD"),
        "headers": {
            "x-ms-blob-type": "BlockBlob"
        }
    }
