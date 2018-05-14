import bs4
import re
import os
import json
from pprint import pprint
import math
from time import time

WEBPAGES_PATH = "WEBPAGES_RAW"
BOOK_KEEPING_PATH = "WEBPAGES_RAW/bookkeeping.json"
INDEX_PATH = "index.json"

class Database():
    def __init__(self, bookkeeping_path:str, index_path: str):
        self.bookkeeping_path = bookkeeping_path
        self.index_path = index_path
        self.index = self.create_index()

    def create_index(self):
        return json.load(open(self.index_path, 'r'))

    def clear_index(self):
        self.index = {}
        file = open(self.index_path, "w")
        file.write("{}")
        file.close()

    def update_index(self, json_data:dict):
        self.index = json_data
        file = open(self.index_path, 'w')
        json.dump(json_data, file, sort_keys=True, indent=4)
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

    def add_all_files_from_text(self, file:str, text_set:{str}):
        print(file, text_set)
        for token in text_set:
            self.add_file(token, file)

    def add_all_scores_from_text(self, token:str, file:str, scoreField:str, score:float, text_set:{str}):
        pass


class Parser():
    def __init__(self, html:str):
        self.soup = bs4.BeautifulSoup(html, 'lxml') #lxml, html.parser

    def process_text(self, text:str) -> str:
        items = ['\n', '\t', '|', '.', ',', ':', ';']
        for i in items:
            text = text.replace(i, ' ')
        text = self.remove_html_code(text)
        text = text.lower() #lowercase all text
        return text

    # Some of the unstructure html will contain coding segments which
    # need to be removed as much as possible from the text
    def remove_html_code(self, text:str) -> str:
        text = re.sub('#.*{.*}', '', text)  # removes css header
        text = re.sub('if[ ]?[(][^)]*[)]', '', text)  # removes code if ()
        text = re.sub('[^ ]* = function[(][)] {.*}', '', text)  # removes code function = ()
        text = re.sub('var [^ ]* = [^(]*[(][^)]*[)]', '', text)  # removes code car = ()
        text = re.sub(' +', ' ', text)  # removes multiple spaces
        return text

    def all_title_text(self) -> str:
        print('---title----')
        result = ""
        for title in self.soup.find_all('title'):
            result += title.string + ' '
        return result

    def all_header_text(self) -> str:
        print('---header----')
        result = ""
        for header in self.soup.find_all(re.compile('^h[1-6]$')):
            if header.string != None:
                result += header.string + ' '
        return result

    def all_text(self):
        return self.soup.get_text()

class Tokenizer():
    def __init__(self, text:str):
        self.text = text
        self.text_list = self.tokenize()
        self.text_set = set(self.text_list)

    def tokenize(self) -> [str]:
        text_list = self.text.split(' ')
        for text in text_list:
            if not text.isalnum():
                text_list.remove(text)
        return text_list



def tf(token: str, text_list: [str]) -> float:
    frequency = 0
    for text in text_list:
        if token == text:
            frequency += 1
    return frequency / len(text_list)

def documents_containing_token(token:str, database: Database) -> int:
    return len(database[token])

def idf(total_documents:int, documents_containing_token:int) -> float:
    return math.log(total_documents / (1 + documents_containing_token))

def tfidf(token:str, text_list: [str], total_docments:int, documents_containing_token:int) -> float:
    return tf(token,text_list) * idf(total_docments,documents_containing_token)


def all_webpage_paths() -> [str]:
    result = []
    for root, dirs, files in os.walk(WEBPAGES_PATH):
        for file in files:
            if "bookkeeping" not in os.path.join(root,file):
                result.append(os.path.join(root,file).replace('\\', '/'))

    return sorted(result, key=webpage_paths_sorting_key)

def webpage_paths_sorting_key(s: str):
    file = s.split('/')
    return (int(file[1]), int(file[2]))

def main():
    index = Database(BOOK_KEEPING_PATH, INDEX_PATH) #initialize inversed index

    webpage_paths = all_webpage_paths()
    print(webpage_paths)

    webpage_paths = webpage_paths[:5] #EDIT HOW MANY PATHS WANTED/COMMENT OUT IF RUNNING ALL FILES
    for path in webpage_paths:
        print('PATH:', path)
        file = open(path, 'r', encoding='utf-8')
        parser = Parser(file.read())
        file.close()

        webpage_text = parser.process_text(parser.all_text())
        # print(webpage_text)
        tokenizer = Tokenizer(webpage_text)
        # print(tokenizer.text_list)
        # print(len(tokenizer.text_list), len(tokenizer.text_set))

        index.add_all_files_from_text(path, tokenizer.text_set)

    for path in webpage_paths:
        file = open(path, 'r', encoding='utf-8')
        parser = Parser(file.read())
        file.close()

        webpage_text = parser.process_text(parser.all_text())
        tokenizer = Tokenizer(webpage_text)

        for token in tokenizer.text_set:
            tf_idf = tfidf(token, tokenizer.text_list, len(webpage_paths), documents_containing_token(token, index.index))
            index.add_score(token, path, 'tf-idf', tf_idf)



def test_database():
    db = Database(BOOK_KEEPING_PATH, INDEX_PATH)
    db.add_file('hello', '0/0')
    db.add_score('world', '1/1', 'idf', 5)

#Use this to MANUALLY CLEAR INDEX.JSON when experimenting
def clear_index():
    db = Database(BOOK_KEEPING_PATH, INDEX_PATH)
    db.clear_index()

if __name__ == '__main__':
    start  = time()
    # main()
    clear_index()
    print("Total Runtime:", time() - start)
