import json

def test():
	with open("index.json", 'r') as f:
		google_dict = json.load(f)

	with open("WEBPAGES_RAW/bookkeeping.json", 'r') as f:
		url_dict = json.load(f)

	count = [10, 10, 10]
	for word in google_dict:
		for x in google_dict[word]:
			if word == "informatics":
				if count[0] != 0:
					count[0] -= 1
					for url in url_dict:
						if x[13:] == url:
							print("URLs for informatics: " + url_dict[url] + '\n')
							print("---------------------------------")
			elif word == "mondego":
				if count[1] != 0:
					count[1] -= 1
					for url in url_dict:
						if x[13:] == url:
							print("URL for mondego: " + url_dict[url] + '\n')
							print("---------------------------------")
			elif word == "irvine":
				if count[2] != 0:
					count[2] -= 1
					for url in url_dict:
						if x[13:] == url:
							print("URL for irvine: " + url_dict[url] + '\n')
							print("---------------------------------")
				


# Separate the query and normalize (lowercase all) it
def processQuery(query:str) -> [str]:
        queryList = []
        split_query = query.split(" ")
        for word in split_query:
                queryList.append(word.lower())
        return queryList

### returns highest tf-idf score of all the query words
def highest_scores(index: dict, split_words):
        scores = []
        for word in index:
                for user_word in split_words:
                        if user_word == word:
                                for terms in index[word].values():
                                        scores.append(terms["tf-idf"])
        scores = [float(x) for x in scores]
        scores.sort(key = int, reverse = True)
        return scores[0:10]




# Takes in query and returns the top 10 links
def searchQuery(query:str, index:dict, bookkeeping:dict, maxlinks:int) -> [str]:
        result = []
        split_words = processQuery(query)
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
                for url in bookkeeping:
                        if file[13:] == url:
                                if bookkeeping[url] not in result:
                                        result.append(bookkeeping[url])
                                                                                
                        
                                
        return result

