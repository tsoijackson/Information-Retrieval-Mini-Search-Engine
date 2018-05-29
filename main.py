import bs4
from nltk.tokenize import RegexpTokenizer
import re
import os
import json
import math
from time import time
from mysite.home.main.linguisticprocessor import LinguisticProcessor

WEBPAGES_PATH = "WEBPAGES_RAW"
BOOK_KEEPING_PATH = "WEBPAGES_RAW/bookkeeping.json"
INDEX_PATH = "mysite/home/main/index.json"

# class that defines the json "db" and its functions
class Database():
    __slots__ = ('bookkeeping_path', 'index_path', 'index')
    def __init__(self, bookkeeping_path:str, index_path: str):
        self.bookkeeping_path = bookkeeping_path
        self.index_path = index_path
        self.index = self.create_index()

    def create_index(self):
        return json.load(open(self.index_path, 'r', encoding='utf-8'))

    def clear_index(self):
        self.index = {}
        file = open(self.index_path, "w")
        file.write("{}")
        file.close()

    def update_index(self):
        file = open(self.index_path, 'w', encoding='utf-8')
        file.write(IndexFormatter(self.index).dumps())
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

    def add_occurences(self, token:str, og_token:str, file:str, indices_text:list):
        # iterating through the list of lines
        line_count = 0
        offset_count = 0
        for line in indices_text:
            line_count += 1
            line = line.lower()
            if og_token in line:
                offset_count = 0
                stripped_line = line.strip(' \n')
                for word in stripped_line.split():
                    offset_count += 1
                    if og_token == word:
                        break
        if token not in self.index:
            self.add_token(token)
        if file not in self.index[token]:
            self.add_file(token, file)
        self.index[token][file]['position'] = [line_count, offset_count]

#Code that Formats the Index into a String Form
class IndexFormatter():
    def __init__(self, object: dict):
        self.object = object

    def dumps(self):
        result = "{\n"
        token_dict = sorted(self.object)
        for token in token_dict:
            result += '\t"' + token + '": {\n'
            path_dict = sorted(self.object[token], key=webpage_paths_sorting_key)
            for path in path_dict:
                result += '\t\t"' + path + '": { '
                attribute_dict = sorted(self.object[token][path])
                for attribute in attribute_dict:
                    result += '"' + attribute + '": ' + str(self.object[token][path][attribute])
                    if attribute != attribute_dict[-1]: result += ', '
                if path != path_dict[-1]: result += ' },\n'
                else: result += ' }\n'
            if token != token_dict[-1]: result += '\t},\n'
            else: result += '\t}\n'
        result += "}"
        return result

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
        return text

    def all_title_text(self) -> str:
        result = ""
        for title in self.soup.find_all('title'):
            if title.string != None:
                result += title.string + ' '
        return result

    def all_text(self):
        return self.soup.get_text()

class Tokenizer():
    __slots__ = ('text', 'text_list_lower', 'text_set_lower', 'original_token')
    def __init__(self, text:str):
        self.text = text
        self.original_token = []
        self.text_list_lower = self.tokenize() # lowered and stemmed
        self.text_set_lower = set(self.text_list_lower) # lowered and stemmed

    def tokenize(self) -> [str]:
        tokens = RegexpTokenizer(r'\w+').tokenize(self.text)
        self.original_token = tokens
        return LinguisticProcessor(tokens).process()

    def combine_lists(self):
        final_list = []
        for num in range(len(self.text_list_lower)):
            # modified, original version
            final_list.append([self.text_list_lower[num], self.original_token[num].lower()])
        return final_list

def token_frequency_in_document(token:str, text_list: [str]) -> int:
    frequency = 0
    for text in text_list:
        if token == text:
            frequency += 1
    return frequency

def tf(token_frequency:int) -> float:
    return 1+math.log(token_frequency)

def documents_containing_token(token:str, database: Database.index) -> int:
    return len(database[token])

def idf(total_documents:int, documents_containing_token:int) -> float:
    return math.log(total_documents / (1 + documents_containing_token))

def tfidf(token_frequency:int, total_documents:int, documents_containing_token:int) -> float:
    return tf(token_frequency) * idf(total_documents,documents_containing_token)

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
    ignore = ['0/0', '0/438', '39/373', '35/269', '19/336', '55/433']
    for page in ignore:
        page = "WEBPAGES_RAW/" + page
        result.add(page)
    return result

def main():
    clear_index()

    index = Database(BOOK_KEEPING_PATH, INDEX_PATH) #initialize inversed index

    webpage_paths = all_webpage_paths()
    webpage_paths = webpage_paths[0:50] #EDIT HOW MANY PATHS WANTED/COMMENT OUT IF RUNNING ALL FILES
    TOTAL_DOCUMENTS = len(webpage_paths)
    for path in webpage_paths:

        if path in pages_to_ignore():
            continue

        print('PATH:', path)
        file = open(path, 'r', encoding='utf-8')
        file_text = file.read()
        file.seek(0)
        indices_info = file.readlines()

        # check to see if the files is an image
        first_line = indices_info[0]
        incorrect_types =['\x89PNG\n']
        if first_line in incorrect_types:
            continue
        parser = Parser(file_text)
        file.close()

        webpage_text = parser.process_text(parser.all_text())
        tokenizer = Tokenizer(webpage_text)
        combined_list = tokenizer.combine_lists()

        # modified, original version
        for token in combined_list:
            index.add_file(token[0], path)
            text_frequency = token_frequency_in_document(token[0], tokenizer.text_list_lower)
            index.add_frequency(token[0], path, text_frequency)
            index.add_length(token[0], path, len(tokenizer.text_list_lower))
            index.add_occurences(token[0], token[1], path, indices_info)

        start = time()
        for token in index.index:
            for file in index.index[token]:
                current_idf = idf(total_documents=len(webpage_paths),
                documents_containing_token=documents_containing_token(token, index.index))
                current_tf_idf = tfidf(index.index[token][file]['frequency'],
                               total_documents=len(webpage_paths),
                               documents_containing_token=documents_containing_token(token, index.index))
                index.add_score(token, file, 'tf-idf', current_tf_idf)
                index.add_score(token, file, 'tf-idf-temp', 0)
                index.add_score(token, file, 'idf', current_idf)
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
    clear_index()
    main()
    print("Total Runtime:", time() - start)
