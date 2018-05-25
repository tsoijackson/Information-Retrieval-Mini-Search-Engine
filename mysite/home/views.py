from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

import sys, json
#importing mini search engine project folder
sys.path.insert(0, sys.path[0].replace('\\mysite','')) # sys.path[0] =  /Information-Retrieval-Mini-Search-Engine/

import query
print("HELLLOOOO")
print(sys.path[0])

INDEX_DICT = json.load(open((sys.path[0]+'\\index.json'), 'r'))
BOOKKEEPING_DICT = json.load(open((sys.path[0]+'\\WEBPAGES_RAW\\bookkeeping.json'), 'r'))
MAX_LINKS = 10

# Create your views here.

def index(request):
	if len(request.GET) == 0:
		return render(request, 'home/index.html', {})
	if len(request.GET['searchBar']) > 0:
		print('searching...')
		queryString = request.GET['searchBar']
		print('queryString:', queryString)

		# INSERT QUERY SEARCHING CODE HERE
		searchResults = query.searchQuery(query=queryString, index=INDEX_DICT, bookkeeping=BOOKKEEPING_DICT, maxlinks=MAX_LINKS)
		# END of QUERY SEARCH

		linklist = write_html_link_anchors(searchResults)

		return render(request, 'home/index.html', {'links': linklist})

	return render(request, 'home/index.html', {})

def write_html_link_anchors(searchResults: [str]):
	html = ''
	for link in searchResults:
		html += '<li class="pt-2 pb-1"><a href="{}">{}</a></li>'.format(link, link)
	return html


def request_page(request):
	print((request.GET.get('mybtn')))
	if(request.GET.get('mybtn')):
		print(True)
		print(request.GET.get('searchbar'))