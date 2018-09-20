from bs4 import BeautifulSoup
import requests
import requests.exceptions
from urllib.parse import urlsplit
from collections import deque
import re
import csv

keywords = ["example1","example2"] #insert keyword here

new_urls = deque(['https://www.unc.edu/'
,'http://www.duke.edu/'
]) #insert the initial urls for the websites you want to search

counter = 0
linecounter = 0

# a set of urls that we have already crawled
processed_urls = set()

# a set of crawled emails
emails = set()

# process urls one by one until we exhaust the queue
while len(new_urls):
    
    counter += 1
    # move next url from the queue to the set of processed urls
    url = new_urls.popleft()
    processed_urls.add(url)

    # extract base url to resolve relative links
    parts = urlsplit(url)
    base_url = "{0.scheme}://{0.netloc}".format(parts)
    path = url[:url.rfind('/')+1] if '/' in parts.path else url
    
    linecounter += 1
    print(linecounter)
    try:
        response = requests.get(url)
    except (requests.exceptions.InvalidSchema,requests.exceptions.MissingSchema, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,requests.exceptions.TooManyRedirects, AttributeError):
        # ignore pages with errors
        continue
    for key in keywords:
        if key in response.text:
            print("adding email")
            # extract all email addresses and add them into the resulting set
            new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I))
            emails.update(new_emails)
            break
        

# Write emails to txt file for every 10 emails;
    if counter >= 10:
        print("writing csv -------------------------\n")
        with open("./output.txt", 'a') as f:
            for x in emails:
                print(x)
                f.write(x + "\n")
        emails = set()
        counter = 0

        print("finished writing--------------------\n")


    # create a beutiful soup for the html document
    soup = BeautifulSoup(response.text,features="lxml")

    # find and process all the anchors in the document
    for anchor in soup.find_all("a"):
        # extract link url from the anchor
        link = anchor.attrs["href"] if "href" in anchor.attrs else ''
        
        # resolve relative links
        if link.startswith('/'):
            link = base_url + link
        elif not link.startswith('http'):
            link = path + link
        # add the new url to the queue if it was not enqueued nor processed yet
        if not link in new_urls and not link in processed_urls:
            new_urls.append(link)
            


print("Search complete")
