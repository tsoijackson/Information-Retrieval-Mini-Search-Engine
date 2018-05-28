import bs4
from nltk.tokenize import RegexpTokenizer
import re
import os
import json
from pprint import pprint
import math
from time import time
from collections import defaultdict

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

    def add_occurences(self, token:str, file:str, indices_text:list):
        # iterating through the list of lines
        line_count = 0
        offset_count = 0
        for line in indices_text:
            line_count += 1
            line = line.lower()
            if token in line:
                offset_count = 0
                stripped_line = line.strip(' \n')
                for word in stripped_line.split():
                    offset_count += 1
                    if token == word:
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

class IndexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, dict):
            return json.dumps('')
        else:
            return json.dumps(obj)


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

def tf(token_frequency:int) -> float:
    return 1+math.log(token_frequency)

def documents_containing_token(token:str, database: Database.index) -> int:
    return len(database[token])

def idf(total_documents:int, documents_containing_token:int) -> float:
    return math.log(total_documents / (1 + documents_containing_token))

def tfidf(token_frequency:int, total_documents:int, documents_containing_token:int) -> float:
    return tf(token_frequency) * idf(total_documents,documents_containing_token)

# EC: calculate the average tf-idf of a term
def qterm_avg(current_term,google_dict):
    print("------------- avg function is called -------------")
    current_avg = 0
    for doc, values in google_dict[current_term].items():
        current_avg += values['tf-idf']
        print(current_avg)
    return current_avg/len(google_dict[current_term])

# EC: extract the docs related with
def qterm_docextract1(query_list, google_dict):
    # list of all the document that contains one or more of the query term
    document_dic = dict([])
    for term in query_list:
        for doc in google_dict[term]:
            if doc not in document_dic:
                document_dic[doc] = []
                document_dic[doc].append([term,google_dict[term][doc]["position"]])

            else:
                # lists of list that contains the term and the position
                document_dic[doc].append([term,google_dict[term][doc]["position"]])
    return document_dic
def qterm_docextract2(query_list, google_dict):
    # list of all the document that contains one or more of the query term
    document_dic = dict([])
    for term in query_list:
        for doc in google_dict[term]:
            if doc not in document_dic:
                document_dic[doc] = []
                document_dic[doc].append(term)
            else:
                document_dic[doc].append(term)
    return document_dic
# EC: check to see the type and if a query term is within a header within
# the documentation
def qterm_withindocument(query_term, current_doc):
    ans_list = []
    with open(current_doc) as current_file:
        current_soup = bs4.BeautifulSoup(current_file, "lxml")
    possible_tags = ["title", "h1", "b", "i"]
    for tag in possible_tags:
        tag_list = current_soup.select(tag)
        for individual_tag in tag_list:
            # print(individual_tag)
            if query_term in str(individual_tag):
                ans_list.append(tag)
    return ans_list

def tfidf_reset(query_term, google_dict):
    for query in query_term:
        for docs in google_dict[query]:
            google_dict[query][docs]["tf-idf"] = google_dict[query][docs]["tf-idf-temp"]

# EC: calculate and manipulate the weight based on a tokens positional location
def qterm_positional_weight(query_list,google_dict):
    print("------ qterm_positional_ec ------")
    if(len(query_list) < 2):
        return None
    # list of all the document that contains one or more of the query term
    document_dic = qterm_docextract1(query_list,google_dict)
    line_result = 0
    column_result = 0
    prev_item = None
    # go through each term within the query to calculate the line and row result
    # key: document, value: [ [term, position], ... ]
    # we are moving through each document
    for key, values in document_dic.items():
        # this list will collect the terms that has been scanned through
        current_terms = set()
        # moves through one document at a time
        if len(values) == 1:
            return None
        for queries_info in values:
            if prev_item != None:
                # moving through each query term, its position within the document
                line_result += math.fabs(queries_info[1][0]-prev_item[1][0])
                column_result += math.fabs(queries_info[1][1]-prev_item[1][1])
                current_terms.add(queries_info[0])
            prev_item = queries_info
        # update the positional_weight and modify the tf_idf of the document
        # with a term key of an inverse index
        if (line_result > 0 and column_result > 0):
            # the smaller the value the more accurate that it is; therefore we need
            # to use the inverse
            line_result = 1/line_result
            column_result = 1/column_result
            for term in current_terms:
                print(term)
                print(key)
                print("prior: ", google_dict[term][key]['tf-idf'])
                # print("current avg: ", current_avg)
                # print("line_result", line_result)
                # print("column_result", column_result)
                updated_score = 1 + math.log((2*line_result + column_result) * 10) # use of 10 as the base tf-idf val
                print("updated score", updated_score)
                # temporarily placed into the tf-idf-temp section
                google_dict[term][key]['tf-idf-temp'] = google_dict[term][key]['tf-idf']
                google_dict[term][key]['tf-idf'] += updated_score
                print("later: ", google_dict[term][key]['tf-idf'])

# EC: calculate the weight based on the type of header it is contained within
def qterm_header_weight(query_list,google_dict):
    print("------ qterm_header_ec ------")
    if(len(query_list) == 0):
        return None
    # list of all the document that contains one or more of the query term
    document_dic = qterm_docextract2(query_list,google_dict)
    header_weight = 0
    # key: document, value: [term, ...]
    for key, values in document_dic.items():
        # print(key, values)
        header_weight = 0
        for term in values:
            # this is the output of all the tags that contains a query term
            # within a document
            qterm_list = qterm_withindocument(term, key)
            # print("qterm_list", qterm_list)
            if ("title" in qterm_list):
                header_weight += 10
            elif ("h1" in qterm_list):
                header_weight += 5
            elif ("b" in qterm_list or "i" in qterm_list):
                header_weight += 3
        # update the tf_idf value of this particular document within each
        # of the qterm in the inverted index
        if (header_weight > 0):
            for term in values:
                print("prior: ", google_dict[term][key]['tf-idf'])
                current_term_frequency = google_dict[term][key]['frequency']
                updated_term_frequency = current_term_frequency + header_weight
                idf_value = google_dict[term][key]['idf']
                tf_idf_update = tf(updated_term_frequency) * idf_value
                # temporarily placed into the tf-idf-temp section
                google_dict[term][key]['tf-idf-temp'] = google_dict[term][key]['tf-idf']
                google_dict[term][key]['tf-idf'] = tf_idf_update
                print("later: ", google_dict[term][key]['tf-idf'])

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
    webpage_paths = webpage_paths[0:500] #EDIT HOW MANY PATHS WANTED/COMMENT OUT IF RUNNING ALL FILES
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
        title_text = parser.process_text(parser.all_title_text())

        # print(parser.all_text())

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
            index.add_occurences(token, path, indices_info)

        title_text = parser.process_text(parser.all_title_text())

        # print(parser.all_text())
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
