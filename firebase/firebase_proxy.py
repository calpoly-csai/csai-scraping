import pinject
from google.cloud.firestore_v1 import Client

from typing import List

import copy

from transaction import Transaction


class FirebaseProxy:
    @pinject.copy_args_to_internal_fields
    def __init__(self, db: Client):
        pass

    def batched_write(self, transactions: List[Transaction]) -> None:
        """

        :param transactions: The transactions to apply to firebase
        :return:
        """
        batch = self._db.batch()

        for transaction in transactions:
            _document_name = transaction.document_name.replace("/", "_")

            _document = copy.deepcopy(transaction.document)
            _document['type'] = transaction.document_type
            doc = self._db.collection(transaction.collection).document(
                _document_name)
            batch.set(doc, _document)

        batch.commit()

