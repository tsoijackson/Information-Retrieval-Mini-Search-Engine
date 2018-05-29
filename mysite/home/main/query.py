import json
from .linguisticprocessor import LinguisticProcessor

def tf(token_frequency:int) -> float:
    return 1+math.log(token_frequency)

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
        if query not in google_dict:
            continue
        else:
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

# Separate the query and normalize (lowercase all) it
def processQuery(query:str) -> [str]:
	queryList = []
	split_query = query.split(" ")
	return LinguisticProcessor(split_query).process()

### returns 10 highest tf-idf scores of all the query words
def highest_scores(index: dict, split_words):
	scores = []
	for user_word in split_words:
		if user_word in index:
		    for terms in index[user_word].values():
		        scores.append(terms["tf-idf"])
		scores = [float(x) for x in scores]
		scores.sort(key = int, reverse = True)
	return scores[0:10]

# Takes in query and returns the top 10 links
def searchQuery(query:str, index:dict, bookkeeping:dict, maxlinks:int) -> [str]:
	results = []
	split_words = processQuery(query); print(split_words)
	# qterm_header_weight(split_words,index)
	# qterm_positional_weight(split_words,index)
	high_scores = highest_scores(index, split_words)
	files = []
	for user_word in split_words:
	    for score in high_scores:
	        for word, value in index.items():
	            if user_word == word:
	                for file, terms in value.items():
	                    if terms["tf-idf"] == score:
	                        if file not in files and maxlinks != 0:
	                            files.append(file)
	                            maxlinks -= 1
	for file in files:
	    for url_file in bookkeeping:
	        if file[13:] == url_file:
	            if bookkeeping[url_file] not in results:
	                results.append("https://" + bookkeeping[url_file])

	# tfidf_reset(split_words,index)
	return results
