import pinject
from firebase.firebase_module import FirebaseModule
from firebase.firebase_proxy import FirebaseProxy

import unittest

from typing import Dict

from transaction import Transaction


# Run CLI tool to generate cred_path file before running test
#
# Or write only the path of your credentials in a file called "cred_path" in
# in the base project directory
class FirebaseProxyTest(unittest.TestCase):
    def setUp(self) -> None:
        obj_graph = pinject.new_object_graph(modules=None,
                                             binding_specs=[FirebaseModule()])
        self.firebase_proxy: FirebaseProxy = obj_graph.provide(FirebaseProxy)

    def test_put(self):
        test_collection = 'test'
        test_doc_name = "Ada"
        test_doc: Dict = {
            u'first': u'Ada',
            u'last': u'Lovelace',
            u'born': 1815
        }
        test_doc_type = "person"

        transaction = Transaction(test_collection,
                                  test_doc_name,
                                  test_doc,
                                  test_doc_type)

        self.firebase_proxy.batched_write([transaction])


if __name__ == '__main__':
    unittest.main()
