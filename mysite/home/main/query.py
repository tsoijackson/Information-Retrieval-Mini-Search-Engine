import json


##with open("index.json", 'r') as f:
##        google_dict = json.load(f)
##
##with open("bookkeeping.json", 'r') as f:
##        url_dict = json.load(f)
##
##user_input = input("PLease enter your search: ")


# Separate the query and normalize (lowercase all) it
def processQuery(query:str) -> [str]:
        queryList = []
        split_query = query.split(" ")
        for word in split_query:
                queryList.append(word.lower())
        return queryList

### returns 10 highest tf-idf scores of all the query words
def highest_scores(index: dict, split_words):
        scores = []
        for user_word in split_words:
                for terms in index[user_word].values():
                        scores.append(terms["tf-idf"])
        scores = [float(x) for x in scores]
        scores.sort(key = int, reverse = True)
        return scores[0:10]




# Takes in query and returns the top 10 links
def searchQuery(query:str, index:dict, bookkeeping:dict, maxlinks:int) -> [str]:
        results = []
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
                for url_file in bookkeeping:
                        if file[13:] == url_file:
                                if bookkeeping[url_file] not in results:
                                        results.append(bookkeeping[url_file])
                                                                                
                        
                                
        return results

#print(searchQuery(user_input, google_dict, url_dict, 10))
