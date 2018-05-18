import bs4
from nltk.tokenize import RegexpTokenizer
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
    __slots__ = ('bookkeeping_path', 'index_path', 'index')
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

    def update_index(self):
        file = open(self.index_path, 'w')
        json.dump(self.index, file, sort_keys=True, indent=4)
        file.close()

    def add_token(self, token:str):
        if token not in self.index:
            self.index[token] = {}

    def add_file(self, token:str, file:str):
        if token not in self.index:
            self.add_token(token)
        self.index[token][file] = {}

    def add_frequency(self, token:str, file:str, frequency:int):
        if token not in self.index:
            self.add_token(token)
        if file not in self.index[token]:
            self.add_file(token, file)
        self.index[token][file]['frequency'] = frequency

    def add_title_frequency(self, token:str, file:str, frequency:int):
        if token not in self.index:
            self.add_token(token)
        if file not in self.index[token]:
            self.add_file(token, file)
        self.index[token][file]['title_frequency'] = frequency

    def add_title_length(self, token:str, file:str, length: int):
        if token not in self.index:
            self.add_token(token)
        if file not in self.index[token]:
            self.add_file(token, file)
        self.index[token][file]['title_length'] = length

    def add_length(self, token:str, file:str, length:int):
        if token not in self.index:
            self.add_token(token)
        if file not in self.index[token]:
            self.add_file(token, file)
        self.index[token][file]['length'] = length

    def add_score(self, token:str, file:str, scoreField:str, score:float):
        if token not in self.index:
            self.add_token(token)
        if file not in self.index[token]:
            self.add_file(token, file)
        self.index[token][file][scoreField] = score


class Parser():
    __slots__ = ('soup')
    def __init__(self, html:str):
        self.soup = bs4.BeautifulSoup(html, 'lxml') #lxml, html.parser

        #removes tags from the parser
        for tag in self.soup(['script', 'style']):
            tag.decompose()

    def process_text(self, text:str) -> str:
        items = ['\n', '\t', '|', '.', ',', ':', ';']
        for i in items:
            text = text.replace(i, ' ')
        text = re.sub(' +', ' ', text)  # removes multiple spaces
        text = self.remove_html_code(text)
        return text

    # Some of the unstructure html will contain coding segments which
    # need to be removed as much as possible from the text
    def remove_html_code(self, text:str) -> str:
        # text = re.sub('#[^{]*{[^}]*}', ' ', text)  # removes css header
        # text = re.sub('if[ ]?[(][^)]*[)]', ' ', text)  # removes code if ()
        # text = re.sub('[^ ]* = function[(][)] {.*}', ' ', text)  # removes code function = ()
        # text = re.sub('function[ ][^(]*[(][)][ ]?{[^}]*}', ' ', text) # removes code function () { }
        # text = re.sub('var [^ ]* = [^(]*[(][^)]*[)]', ' ', text)  # removes code var = ()
        # text = re.sub('[\\].*[\\]["]', ' ', text) # removes code \  \"
        # text = re.sub('catch[(]e[)][ ]?{[^}]*}', ' ', text) # remvoes code catch(e) {}
        return text

    def all_title_text(self) -> str:
        result = ""
        for title in self.soup.find_all('title'):
            if title.string != None:
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
    __slots__ = ('text', 'text_list', 'text_list_lower', 'text_set', 'text_set_lower')
    def __init__(self, text:str):
        self.text = text
        self.text_list = self.tokenize()
        self.text_list_lower = self.tokenize_lower()
        self.text_set = set(self.text_list)
        self.text_set_lower = set(self.text_list_lower)

    def tokenize(self) -> [str]:
        return RegexpTokenizer(r'\w+').tokenize(self.text)

    def tokenize_lower(self) -> [str]:
        return [token.lower() for token in RegexpTokenizer(r'\w+').tokenize(self.text)]



def token_frequency_in_document(token:str, text_list: [str]) -> int:
    frequency = 0
    for text in text_list:
        if token == text:
            frequency += 1
    return frequency

def tf(token_frequency:int, text_list_length:int) -> float:
    return token_frequency / text_list_length

def documents_containing_token(token:str, database: Database.index) -> int:
    return len(database[token])

def idf(total_documents:int, documents_containing_token:int) -> float:
    return math.log(total_documents / (1 + documents_containing_token))

def tfidf(token_frequency:int, text_list_length: int, total_docments:int, documents_containing_token:int) -> float:
    return tf(token_frequency,text_list_length) * idf(total_docments,documents_containing_token)


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

def pages_to_ignore() -> set:
    result = set()
    ignore = ['0/0', '0/438', '39/373']
    for page in ignore:
        page = "WEBPAGES_RAW/" + page
        result.add(page)
    return result

def main():
    clear_index()

    index = Database(BOOK_KEEPING_PATH, INDEX_PATH) #initialize inversed index

    webpage_paths = all_webpage_paths()
    print(webpage_paths)

    #webpage_paths = webpage_paths[:400] #EDIT HOW MANY PATHS WANTED/COMMENT OUT IF RUNNING ALL FILES
    TOTAL_DOCUMENTS = len(webpage_paths)
    for path in webpage_paths[:500]: #6:15

        if path in pages_to_ignore():
            continue

        print('PATH:', path)
        file = open(path, 'r', encoding='utf-8')
        file_text = file.read()
        parser = Parser(file_text)
        file.close()

        webpage_text = parser.process_text(parser.all_text())
        title_text = parser.process_text(parser.all_title_text())

        print(parser.all_text())

        tokenizer = Tokenizer(webpage_text)
        title_tokenizer = Tokenizer(title_text)

        for token in tokenizer.text_set_lower:
            index.add_file(token, path)
            text_frequency = token_frequency_in_document(token, tokenizer.text_list_lower)
            title_frequency = token_frequency_in_document(token, title_tokenizer.text_list_lower)

            index.add_frequency(token, path, text_frequency)
            index.add_title_frequency(token, path, title_frequency)

            index.add_length(token, path, len(tokenizer.text_list_lower))
            index.add_title_length(token, path, len(title_tokenizer.text_list_lower))

    start = time()
    for token in index.index:
        for file in index.index[token]:
            tf_idf = tfidf(index.index[token][file]['frequency'], index.index[token][file]['length'],
                           total_docments=len(webpage_paths),
                           documents_containing_token=documents_containing_token(token, index.index))
            index.add_score(token, file, 'tf-idf', tf_idf)
    print('adding score :', time() - start)

    index.update_index()
    print('total documents:', TOTAL_DOCUMENTS)
    print(len(index.index))


#Use this to MANUALLY CLEAR INDEX.JSON when experimenting
def clear_index():
    db = Database(BOOK_KEEPING_PATH, INDEX_PATH)
    db.clear_index()

if __name__ == '__main__':
    start  = time()
    main()
    print("Total Runtime:", time() - start)
