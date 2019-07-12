import os
import sys

import pinject

from course_scraping import CourseScraper
from firebase.firebase_module import FirebaseModule
from firebase.firebase_proxy import FirebaseProxy


class Sustainer:
    @staticmethod
    def start():
        obj_graph = pinject.new_object_graph(modules=None,
                                             classes=[FirebaseProxy],
                                             binding_specs=[FirebaseModule()])

        course_scraper: CourseScraper = obj_graph.provide(CourseScraper)
        course_scraper.parse()


if __name__ == '__main__':
    assert(len(sys.argv) == 2),\
        "\n\nUsage: python3 sustainer.py [firebase_cred_path]"

    cred_path = sys.argv[1]
    try:
        f = open(cred_path)
        f.close()
    except FileNotFoundError:
        raise FileNotFoundError("Invalid file path for firebase credentials.")

    with open(sys.path[0] + "/cred_path", 'w') as f:
        f.write(cred_path)

    sustainer = Sustainer()
    sustainer.start()
