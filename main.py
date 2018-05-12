import bs4
import os
import json
from pprint import pprint

WEBPAGES_PATH = "WEBPAGES_RAW"
BOOK_KEEPING_PATH = "WEBPAGES_RAW/bookkeeping.json"
INDEX_PATH = "index.json"

class database():
    def __init__(self, bookkeeping_path:str, index_path: str):
        self.bookkeeping_path = bookkeeping_path
        self.index_path = index_path
        self.index = self.create_index()

    def create_index(self):
        return json.load(open(self.index_path, 'r'))

    def update_index(self, json_data:dict):
        self.index = json_data
        file = open(self.index_path, 'w')
        json.dump(json_data, file, sort_keys=True, indent=4)
        file.close()

    def clear_index(self):
        self.index = {}
        file = open(self.index_path, "w")
        file.write("{}")
        file.close()

    def add_token(self, token:str):
        if token not in self.index:
            self.index[token] = {}
        self.update_index(self.index)

    def add_file(self, token:str, file:str):
        if token not in self.index:
            self.add_token(token)
        self.index[token][file] = {}
        self.update_index(self.index)

    def add_score(self, token:str, file:str, scoreField:str, score:float):
        if token not in self.index:
            self.add_token(token)
        if file not in self.index[token]:
            self.add_file(token, file)
        self.index[token][file][scoreField] = score
        self.update_index(self.index)


def all_webpage_paths():
    result = []
    for root, dirs, files in os.walk(WEBPAGES_PATH):
        for file in files:
            if "bookkeeping" not in os.path.join(root,file):
                result.append(os.path.join(root,file).replace('\\', '/'))

    return result

def main():
    webpage_paths = all_webpage_paths()
    print(webpage_paths)

def test_database():
    db = database(BOOK_KEEPING_PATH, INDEX_PATH)
    db.add_file('hello', '0/0')
    db.add_score('world', '1/1', 'idf', 5)

if __name__ == '__main__':
    main()
    # test_database()
