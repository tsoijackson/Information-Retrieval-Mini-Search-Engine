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
        for word in index:
                for file in index[word]:
                        for terms in index[word].values():
                                if maxlinks != 0:
                                        for score in high_scores:
                                                for user_word in split_words:
                                                        if user_word == word:
                                                                if terms["tf-idf"] == score:
                                                                        if file not in files:
                                                                                files.append(file)
                                                                                maxlinks -= 1
        for url in bookkeeping:
                for file in files:
                        if file[13:] == url:
                                if bookkeeping[url] not in result:
                                        result.append(bookkeeping[url])
                                                                                
                        
                                
                                        
        return result

# print(searchQuery(user_input, google_dict, url_dict, 10))
