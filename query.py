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
				


