from bs4 import BeautifulSoup
import requests
import requests.exceptions
from urllib.parse import urlsplit
from collections import deque
import re

import csv
import argparse
import sys
import time


def main(argv):
    # parsing to get keywords and base urls
    argParser = argparse.ArgumentParser(description='Process some keywords.')
    keywords_csv = None
    urls_csv = None
    output_csv = None

    argParser.add_argument(
        '-k', '--keywords', help='the filepath for keyword.csv')
    argParser.add_argument(
        '-u', '--urls', help='the filepath for urls.csv')
    argParser.add_argument(
        '-o', '--output', help='Output file')

    if 'crawler.py' in argv[0]:
        parsed_args = argParser.parse_args()
    else:
        parsed_args = argParser.parse_args(argv)

    keywords_csv = parsed_args.keywords
    urls_csv = parsed_args.urls
    output_csv = parsed_args.output
    print('Arguments: keywords {}, urls {}, output {}'.format(
        parsed_args.keywords,
        parsed_args.urls, parsed_args.output))
    if keywords_csv == None:
        print('missing keywords')
        return
    if '.csv' not in keywords_csv:
        print('wrong file format for keywords')
        return
    if urls_csv == None:
        print('missing urls')
        return
    if '.csv' not in urls_csv:
        print('wrong file format for urls')
        return
    if output_csv is None:
        print('''Output file not specified, and the default was somehow
			replaced. Please try specifying a proper output file.''')
        return

    keywords_list = []
    urls = []

    with open(keywords_csv, 'r') as kCsv:
        reader = csv.reader(kCsv, delimiter="\t")
        for word in reader:
            #get first column elements
            keywords_list.append(word[0])
    with open(urls_csv, 'r') as uCsv:
        reader = csv.reader(uCsv, delimiter="\t")
        for url in reader:
            urls.append(url[0])

    # insert the initial urls for the websites you want to search, these are example urls
    new_urls = deque(urls)

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
        
        #print(url)
        processed_urls.add(url)

        # extract base url to resolve relative links
        parts = urlsplit(url)
        base_url = "{0.scheme}://{0.netloc}".format(parts)
        path = url[:url.rfind('/')+1] if '/' in parts.path else url
        linecounter += 1
        print(linecounter)
        try:
            response = requests.get(url)
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
            # ignore pages with errors
            print("error detected, continueing")
            continue
        for key in keywords_list:
            print(key)
            if key in response.text:
                print("adding email")
                # extract all email addresses and add them into the resulting set
                new_emails = set(re.findall(
                    r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I))
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
        soup = BeautifulSoup(response.text, features="lxml")

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


if __name__ == "__main__":
    # Benchmark timer start.
    time.clock()
    print('----------')

    # When importing groupre, you can provide arguments by calling it as such:
    #   groupre.main('groupre.py', ARGS)

    main(sys.argv)

    # Benchmark timer end.
    print(time.clock(), 'seconds elapsed.')
    print('----------')
