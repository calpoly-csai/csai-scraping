import pinject
from firebase.firebase_module import FirebaseModule
from firebase.firebase_proxy import FirebaseProxy

import unittest

from typing import Dict


class FirebaseProxyTest(unittest.TestCase):
    def setUp(self) -> None:
        obj_graph = pinject.new_object_graph(modules=None,
                                             binding_specs=[FirebaseModule()])
        self.firebase_proxy: FirebaseProxy = obj_graph.provide(FirebaseProxy)

    def test_put(self):
        test_doc: Dict = {
            u'first': u'Ada',
            u'last': u'Lovelace',
            u'born': 1815
        }

        test_collection = 'test'

        self.firebase_proxy.put_document(test_collection, test_doc)


if __name__ == '__main__':
    unittest.main()
