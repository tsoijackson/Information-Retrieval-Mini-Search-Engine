#Search Engine

import json
from pprint import pprint

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

    def create_token_schema(self, token:str, file:str, score:float) -> str:
        tf_idf_string = '"tf-idf" : {score}'.format(score=score)
        score_attributes = [tf_idf_string]

        score_attribute_string = "{"
        for attribute in score_attributes:
            score_attribute_string += attribute + ','
        score_attribute_string += "}"

        file_string = '{' + '"file": {score_attribute_string}'.format(
            score_attribute_string=score_attribute_string) + '}'

        token_string = '"token": {file_string}'.format(file_string=file_string)

        return token_string

    def add_token(self, token:str):
        if token not in self.index:
            self.index[token] = {}
        self.update_index(self.index)

    def add_file(self, token:str, file:str):
        if token not in self.index:
            self.add_token(token)
        self.index[token][file] = {}
        self.update_index(self.index)



def main():
    with open(BOOK_KEEPING_PATH) as json_file:
        data =  json.load(json_file)

    pprint(data['9/99'])


def test_schema():
    db = database(BOOK_KEEPING_PATH, INDEX_PATH)
    print(db.create_token_schema('hello', '0/0', 50))

def test_create_index_database():
    db = database(BOOK_KEEPING_PATH, INDEX_PATH)
    schema = db.create_token_schema('hello', '0/0', 50)
    print(schema)
    f = open("index.json", "w")
    f.write(schema)

def test_add_token():
    db = database(BOOK_KEEPING_PATH, INDEX_PATH)
    db.add_token('hello')
    db.add_token('world')

def test_add_file():
    db = database(BOOK_KEEPING_PATH, INDEX_PATH)
    db.add_file('hello', '0/0')
    db.add_file('fish', '0/0')

def test_contains_token():
    db = database(BOOK_KEEPING_PATH, INDEX_PATH)
    print(db.contains_token('hello'))
    print(db.contains_token('hello world'))

if __name__ == '__main__':
    # main()
    # test_create_index_database()
    test_add_token()
    test_add_file()
    # test_contains_token()
