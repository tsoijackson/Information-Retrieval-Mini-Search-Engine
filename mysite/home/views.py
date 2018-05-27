from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

import sys, json, os
#importing mini search engine project folder
import home.main.query as query

INDEX_DICT = json.load(open('home/main/index.json', 'r', encoding='utf-8'))
BOOKKEEPING_DICT = json.load(open('home/main/bookkeeping.json', 'r'))
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


