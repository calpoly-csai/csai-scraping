import sys

from pinject import BindingSpec

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from google.cloud.client import Client


class FirebaseModule(BindingSpec):
    def provide_db(self) -> Client:
        for i, path in enumerate(sys.path):
            try:
                with open(path + "/cred_path", 'r') as f:
                    cred_path = f.read()
                break
            except FileNotFoundError:
                if i == len(sys.path) - 1:
                    raise FileNotFoundError("Credential file path not found")

        creds = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(creds)
        return firestore.client()
