import bs4
import re
import os
import json
from pprint import pprint

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


class Parser():
    def __init__(self, html:str):
        self.soup = bs4.BeautifulSoup(html, 'html.parser')

    def process_text(self, text:str) -> str:
        items = ['\n', '\t', '|', '.', ',']
        for i in items:
            text = text.replace(i, ' ')
        text = re.sub(' +',' ',text) #removes multiple spaces
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

    def all_paragraph_text(self) -> str:
        result = ""
        for paragraph in self.soup.find_all('p'):
            print(type(paragraph))
            print(paragraph)
            # result += paragraph.string
        print(self.soup.get_text())
        return result

    def all_div_text(self):
        print('=================================')
        # result = ""
        # for div in self.soup.find_all('BR'):
        #     if div.string != None:
        #         result += div.string + ' '
        # return result
        return self.soup.get_text()

class Tokenizer():
    def __init__(self):
        pass

    def tokenize_text(self, text:str):
        pass

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
    webpage_paths = all_webpage_paths()
    print(webpage_paths)

    for path in webpage_paths[:5]:
        file = open(path, 'r', encoding='utf-8')
        print('PATH:', path)
        # html_text = file.read()
        # soup = bs4.BeautifulSoup(html_text, 'html.parser')
        # titles = soup.find_all('title')
        # print(titles)
        # paragraphs = soup.get_text().replace('\n'," ")
        # print(paragraphs)
        parser = Parser(file.read())
        file.close()

        print(parser.all_title_text())
        print(parser.all_header_text())
        print(parser.process_text(parser.all_div_text()))
        # print(text)

    print("end")

def test_database():
    db = Database(BOOK_KEEPING_PATH, INDEX_PATH)
    db.add_file('hello', '0/0')
    db.add_score('world', '1/1', 'idf', 5)

if __name__ == '__main__':
    main()
    # test_database()
