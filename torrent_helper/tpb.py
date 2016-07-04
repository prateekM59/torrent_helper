import sys
import urllib
import cookielib
import re
import requests
from bs4 import BeautifulSoup

# This is a debug parameter, turn it 1 for printing some debug messages
isDebug = 0


# Function to take the torrent search keyword as input from user 
# parameters: None
# returns: Name of the torrent in URL encoded format for searching in The Pirate Bay
def get_torrent_name():
	print "\nEnter the name of torrent to be searched: "
	sys.stdout.flush()

	resp = ""
	while(resp == ""):
		resp = str(raw_input())
	else:
		if(len(resp)):
			# Perform an URL encoding for searching TPB
			torrent = urllib.pathname2url(resp)
			return torrent
		else:
			print "Incorrect input!!!"
			return
	

# Function to scrape the TPB with given torrent keyword and returns results pertaining to that keyword 
# parameters: URL Encoded torrent keyword e.g. game%20of%20thrones
# returns: Search results of TPB's first page with given torrent query
def call_tpb(torrent):

	# Make a query_string = 'https://pirateproxy.one/search/game%20of%20thrones'
	query_string = 'https://pirateproxy.one/search/' + torrent
	
	# Take care of cookies handing 
	cj = cookielib.CookieJar()

	# Make the GET call to TPB and obtain response
	try:
		response = requests.get(query_string, cookies = cj, headers = get_headers())
		if(isDebug):
			if(response.status_code == 200):	
				file = open("D:\Workspace\Test\Output\\torrent2.html",'a+')
				file.write((response.text).encode('utf-8'))
				file.close()
			else:
				print "Response code is not 200."
		parsed_response = parse_response(response)
		return parsed_response

	except IOError as e:
		print "Error in connecting to TPB because: "
		print e
		return None


# Utility to parse HTML response of TPB results and extracts and returns torrent search data in form of rows
# Right now it only scrapes first page of TPB search query, which is a pragmatic approach 
# parameters: HTML response obtained by running search query on TPB
# returns: Search results of TPB's first page with given torrent query
def parse_response(response):
	soup = BeautifulSoup(response.text, 'html.parser')
	
	# TPB has a div with id 'searchResult' to show all the torrent search results
	search = soup.find(id='searchResult')
	rows = search.findAll('tr')
	return rows


# Function to display search results on CLI in a tabular form and takes selected result from user as a number
# parameters: List 'rows' containing parsed HTML response. Each torrent found, is represented by a row. 
# parameters: An integer n, representing number of results on first page, it is simply len(rows)
# returns: The row number(1 index based), which user selected for download
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


# Utility to print heading for torrent search display in tabular form
# parameters: None 
# returns: None
def show_header():
	print "\n\n"
	line_new = '{:<6} {:^70.70} {:>6} {:<0} {:<6} {:>10}'.format("S.No", "Name", "S", "/", "L", "Size")
	print line_new


# Utility to print all searched torrents in tabular form
# Searched torrents are presented in batch of 5 at a time in CLI for user to select e.g. display results 6-10
# parameters: rows, a List containing searched rows  
# parameters: start, an integer indicating the start of the current batch for printing. 
# parameters: end, an integer indicating the end of the current batch for printing.
# returns: None
def display_list(rows, start, end):
	for row in range(start, end):
		cols = rows[row].findAll('td')
		name = (cols[1].a.string).encode('utf-8')
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


# Wrapper function to start a torrent selected by user from a list of rows
# parameters: List 'rows' containing parsed HTML response. Each torrent found, is represented by a row. 
# parameters: row_no, indicating the user input for torrent selection
# returns: None
def start_download(rows, row_no):
	row = rows[row_no]
	mag_link = get_magnet_link(row)

	if(mag_link is not None):
		add_to_utorrent(mag_link)
	else:
		print "Error in Magnetic link!!!"
		return


# Calls utorrent API and adds torrent to it for downloading
# parameters: mag_link, a magnetic link of the selected torrent
# returns: None
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
# Returns IP on which utorrent is runnning
# parameters: None
# returns: str(IP)
def get_ip():
	return 'localhost'


# HARDCODE
# Returns port on which utorrent is runnning
# parameters: None
# returns: str(port)
def get_port():
	return '8080'


# HARDCODE
# Returns utorrent login credentials
# parameters: None
# returns: ('username', 'password')
def get_utorrent_credentials():
	return 'prateek', 'prateek'


# HARDCODE
# Returns User Agent Headers for GET requests
# parameters: None
# returns: dict of User-Agent
def get_headers():
	headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}
	return headers


# Calls utorrent API and fetches token number and cookie associated
# parameters: base_url for utorrent API e.g. http://localhost:8080/gui/
# returns: (token, cookie)
def get_token_and_cookie(base_url):
	token_url = base_url + "token.html"
	regex_token = r'<div[^>]*id=[\"\']token[\"\'][^>]*>([^<]*)</div>'  # could use BeautifulSoup but this works as well

	# Hardcoded again. TODO: Either use CLI to get from user or read from settings
	auth = get_utorrent_credentials()

	r = requests.get(token_url, auth = auth)

	# We need to extract both token and cookie GUID value
	token = re.search(regex_token, r.text).group(1)
	
	guid = r.cookies['GUID']
	cookie = {"GUID" : guid}

	return token, cookie


# Calls utorrent API and adds torrent to it for downloading
# parameters: mag_link, a magnetic link of the selected torrent
# returns: None
def get_magnet_link(row):
	cols = row.findAll('td')
	torrent_description = cols[1]

	# find all <a> tags and extract magnet link from list item at index 1 
	anchors = torrent_description.findChildren('a')
	return anchors[1].attrs['href']


# Driver function
# parameters: None
# returns: None
def main():
	torrent = get_torrent_name()
	rows = call_tpb(torrent)

	if(rows is not None):
		total_rows = len(rows)
		torrent_no = show_results(rows, total_rows)

		if(torrent_no is not None):
			start_download(rows, torrent_no)
