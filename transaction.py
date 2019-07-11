from typing import Dict


class Transaction:
    def __init__(self, collection: str,
                 document_name: str,
                 document: Dict,
                 document_type: str):
        """
        :param collection: A collection contains multiple documents. In the
            case of scraping, the collection will be "Scraped"
        :param document_name: The document name will be the "primary key".
            This means that if there exists a document in a collection and a new
            document with the same name is added to the collection, the former
            will be overwritten. This will be advantageous in overwriting the old
            data each time the sustainer is run.
        :param document: A python dictionary containing the data to be stored
        :param document_type: A "secondary key" that will define different
            categories of data
        """
        self.collection = collection
        self.document_name = document_name
        self.document = document
        self.document_type = document_type
