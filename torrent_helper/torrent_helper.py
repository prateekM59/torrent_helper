import sys
import urllib2
import urllib
import cookielib
import re
import requests
from bs4 import BeautifulSoup
isDebug = 0


def get_torrent_name():
	print "\nEnter the name of torrent to be searched: "
	sys.stdout.flush()
	torrent = str(raw_input())
	
	# Perform an URL encoding for searching TPB
	torrent = urllib.pathname2url(torrent)
	return torrent 
	


def call_tpb(torrent):

	if(isDebug):
		file = open("D:\Workspace\Test\Output\\torrent1.html",'r')
		return parse_response(file)


	# Make a query_string = 'https://pirateproxy.one/search/game%20of%20thrones'
	query_string = 'https://pirateproxy.one/search/' + torrent
	
	# Take care of cookies handing 
	cj = cookielib.CookieJar()

	# Prepare a GET Request for TPB
	req = urllib2.Request(url= query_string, origin_req_host= cj)

	# Imposter as a browser by changing user agent
	req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36')

	# Make the GET call and obtain response
	try:
		response = urllib2.urlopen(req)
		return parse_response(response)
	except IOError as e:
		print "Error in connecting to TPB because: "
		print e
		return None



def parse_response(response):
	soup = BeautifulSoup(response.read(), 'html.parser')
	
	# TPB has a div with id 'searchResult' to show all the torrent search
	search = soup.find(id='searchResult')
	rows = search.findAll('tr')
	return rows


def show_results(rows, n):
	resp, start = None, 1
	end = start + 5
	while(start < n):
		show_header()
		
		if(end > n):
			end = n

		display_list(rows, start, end)
		print "\nEnter torrent no. to select or Return to see more: ",
		sys.stdout.flush()
		resp = str(raw_input())

		# Enter is pressed for new rows
		if(resp is ""):
			start, end = end, end + 5
		else:
			resp = int(resp)
			if(not(resp < end and resp >= start)):
				print "Wrong Choice!!!"
			return resp
	else:
		print "\nNo more torrents to show!!!"
		return


def show_header():
	print "\n\n"
	line_new = '{:<6} {:^70.70} {:>6} {:<0} {:<6} {:>10}'.format("S.No", "Name", "S", "/", "L", "Size")
	print line_new



def display_list(rows, start, end):
	for row in range(start, end):
		cols = rows[row].findAll('td')
		name = str(cols[1].a.string)
		seed = int(cols[2].string)
		leech = int(cols[3].string)
		size = find_size(cols[1])
		
		print "\n"
		line_new = '{:<6} {:<70.70} {:>6} {:<0} {:<6} {:>10}'.format(row, name, seed, "/", leech, size)
		print line_new


# Function to extract size of torrent, looks hacky. TODO: Should be corrected later.
def find_size(col):
	b = col.font.contents
	u = (b[0].string).encode('utf-8')
	m = u.find('Size')
	u = u[m+5:]  # To skip "Size "
	n = u.index(',')
	size = u[:n]
	return size


def start_download(rows, row_no):
	row = rows[row_no]
	mag_link = get_magnet_link(row)

	if(mag_link is not None):
		add_to_utorrent(mag_link)
	else:
		print "Error in Magnetic link"
		return



def add_to_utorrent(mag_link):

	# TODO: Hardcoded to localhost:8080 now, change later to be generic and should be able to be read automatically by settings file
	ip = get_ip()
	port = get_port()

	base_url = "http://" + ip + ":" + port + "/gui/"

	token, cookie = get_token_and_cookie(base_url)

	# Form add url
	add_url = base_url + "?token=" + token + "&action=add-url&s=" + mag_link
	
	auth = get_utorrent_credentials()

	headers = get_headers()

	if(isDebug):
		print "add_url: ", add_url
		#add_url = 'http://localhost:8080/gui/?token=eN7edUlfWDMVWEz4ITOTGGTZ7JIH0rS26WqPXQ6E2NJwmn4kdeRRrHBxdlcAAAAA&action=add-url&s=magnet:?xt=urn:btih:fc27caac7dee5b15e234cbe5a24d85da498f6933&dn=Game+Of+Thrones+%5BRepack+By+P-G+Studio%5D&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Fopen.demonii.com%3A1337&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'
	try: 
		r = requests.get(add_url, auth = auth, cookies = cookie, headers = headers)
		if(isDebug):
			print r
		if(r.ok):
			print "Successfully added torrent"
	except requests.exceptions.RequestException as e:
		print "Could not add because"
		print e


# HARDCODE
def get_ip():
	return 'localhost'

# HARDCODE
def get_port():
	return '8080'

# HARDCODE
def get_utorrent_credentials():
	return 'prateek', 'prateek'


def get_headers():
	headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}
	return headers


def get_token_and_cookie(base_url):
	token_url = base_url + "token.html"
	regex_token = r'<div[^>]*id=[\"\']token[\"\'][^>]*>([^<]*)</div>'  # could use BeautifulSoup but this works as well

	# Hardcoded again. TODO: Either use CLI to get from user or read from settings
	auth = get_utorrent_credentials()

	# I tried with urllib2.HTTPBasicAuthHandler() as mentioned on https://docs.python.org/2/library/urllib2.html 
	# but that was not working. Anyway, this looks much easier than that
	# Added TODO: Replace all urllib2 with Requests
	r = requests.get(token_url, auth = auth)

	# We need to extract both token and cookie GUID value
	token = re.search(regex_token, r.text).group(1)
	
	guid = r.cookies['GUID']
	cookie = {"GUID" : guid}

	return token, cookie



def get_magnet_link(row):
	cols = row.findAll('td')
	torrent_description = cols[1]

	# find all <a> tags and extract magnet link from list item at index 1 
	anchors = torrent_description.findChildren('a')
	return anchors[1].attrs['href']



def main():
	torrent = get_torrent_name()
	rows = call_tpb(torrent)

	if(rows is not None):
		total_rows = len(rows)
		torrent_no = show_results(rows, total_rows)

		if(torrent_no is not None):
			start_download(rows, torrent_no)


main()