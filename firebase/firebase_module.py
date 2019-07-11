import sys

from pinject import BindingSpec

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from google.cloud.client import Client


class FirebaseModule(BindingSpec):
    def provide_db(self) -> Client:
        with open(sys.path[0] + "/cred_path", 'r') as f:
            cred_path = f.read()

        creds = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(creds)
        return firestore.client()
