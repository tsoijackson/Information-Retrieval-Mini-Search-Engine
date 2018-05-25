from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

import sys
#importing mini search engine project folder
sys.path.insert(0, sys.path[0].replace('\\mysite',''))
import query


# Create your views here.

def index(request):
	if len(request.GET) == 0:
		return render(request, 'home/index.html', {})
	if len(request.GET['searchBar']) > 0:
		print('searching...')
		queryString = request.GET['searchBar']
		print(queryString)

		#INSERT QUERY SEARCHING CODE HERE

		searchResults = ['link1', 'link2', 'link3']
		linklist = write_html_link_anchors(searchResults)

		return render(request, 'home/index.html', {'links': linklist})

	return render(request, 'home/index.html', {})

def write_html_link_anchors(searchResults: [str]):
	html = ''
	for link in searchResults:
		html += '<li class="pt-2 pb-2"><a href="{}">{}</a></li>'.format(link, link)
	return html


def request_page(request):
	print((request.GET.get('mybtn')))
	if(request.GET.get('mybtn')):
		print(True)
		print(request.GET.get('searchbar'))