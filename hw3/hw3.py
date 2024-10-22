# homework 4
# goal: ranked retrieval, PageRank, crawling
# exports:
#   student - a populated and instantiated cs547.Student object
#   PageRankIndex - a class which encapsulates the necessary logic for
#     indexing and searching a corpus of text documents and providing a
#     ranked result set

# ########################################
# first, create a student object
# ########################################

import cs547
MY_NAME = "Shreya Boyane"
MY_ANUM  = 901029106 # put your UID here
MY_EMAIL = "ssboyane@wpi.edu"

# the COLLABORATORS list contains tuples of 2 items, the name of the helper
# and their contribution to your homework
COLLABORATORS = [ 
    ('none', 'none')
    ]

# Set the I_AGREE_HONOR_CODE to True if you agree with the following statement
# "An Aggie does not lie, cheat or steal, or tolerate those who do."
I_AGREE_HONOR_CODE = True

# this defines the student object
student = cs547.Student(
    MY_NAME,
    MY_ANUM,
    MY_EMAIL,
    COLLABORATORS,
    I_AGREE_HONOR_CODE
    )


# ########################################
# now, write some code
# ########################################

import bs4 as BeautifulSoup  # you will want this for parsing html documents
import urllib.request
from bs4 import BeautifulSoup
from collections import defaultdict
import urllib.parse

# our index class definition will hold all logic necessary to create and search
# an index created from a web directory
#
# NOTE - if you would like to subclass your original Index class from homework
# 1 or 2, feel free, but it's not required.  The grading criteria will be to
# call the index_url(...) and ranked_search(...) functions and to examine their
# output.  The index_url(...) function will also be examined to ensure you are
# building the index sanely.

class PageRankIndex(object):
    def __init__(self):
        # you'll want to create something here to hold your index, and other
        # necessary data members

        self.index = defaultdict(list)  # Dictionary to store inverted index
        self.urls = set()  # Store all unique URLs
        self.outlinks = defaultdict(set)  # Store outlinks for each URL



    # index_url( url )
    # purpose: crawl through a web directory of html files and generate an
    #   index of the contents
    # preconditions: none
    # returns: num of documents indexed
    # hint: use BeautifulSoup and urllib
    # parameters:
    #   url - a string containing a url to begin indexing at

    def index_url(self, url):
        # Retrieve and parse the content of the URL
        try:
            response = urllib.request.urlopen(url)
            soup = BeautifulSoup(response, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return

        # Tokenize the visible text in the HTML content
        text = soup.get_text()
        tokens = self.tokenize(text)

        # DEBUG: Print tokens
        print(f"Tokens extracted from {url}: {tokens}")

        # Store tokens in the inverted index
        for token in tokens:
            self.index[token].append(url)

        # Find and store outlinks (href links to other URLs)
        for link in soup.find_all('a', href=True):
            full_url = urllib.parse.urljoin(url, link['href'])
            self.outlinks[url].add(full_url)
            self.urls.add(full_url)

        # DEBUG: Print inverted index after processing
        print(f"Inverted index after indexing {url}: {dict(self.index)}")

        return len(tokens)


    # tokenize( text )
    # purpose: convert a string of terms into a list of terms 
    # preconditions: none
    # returns: list of terms contained within the text
    # parameters:
    #   text - a string of terms
    def tokenize(self, text):

        tokens = []
        current_token = []

        for char in text.lower():
            if char.isalnum():
                current_token.append(char)
            elif current_token:
                tokens.append("".join(current_token))
                current_token = []

        if current_token:
            tokens.append("".join(current_token))

        return tokens


    # ranked_search( text )
    # purpose: searches for the terms in "text" in our index and returns
    #   AND results for highest 10 ranked results
    # preconditions: .index_url(...) has been called on our corpus
    # returns: list of tuples of (url,PageRank) containing relevant
    #   search results
    # parameters:
    #   text - a string of query terms
    def ranked_search(self, text):

        # Tokenize the search query using the same function
        query_tokens = self.tokenize(text)

        # DEBUG: Print query tokens
        print(f"Tokens for query '{text}': {query_tokens}")

        # Check if tokens are in the index and collect matching URLs
        if not query_tokens:
            return []

        results = set(self.index.get(query_tokens[0], []))  # Start with first token's results
        for token in query_tokens[1:]:
            results.intersection_update(self.index.get(token, []))  # Filter URLs matching all tokens

        return list(results)





# now, we'll define our main function which actually starts the indexer and
# does a few queries
def main(args):
    print(student)
    index = PageRankIndex()
    url = 'http://web.cs.wpi.edu/~kmlee/cs547/new10/index.html'
    num_files = index.index_url(url)
    search_queries = (
       'palatial', 'college ', 'palatial college', 'college supermarket', 'famous aggie supermarket'
        )
    for q in search_queries:
        results = index.ranked_search(q)
        print("searching: %s -- results: %s" % (q, results))


# this little helper will call main() if this file is executed from the command
# line but not call main() if this file is included as a module
if __name__ == "__main__":
    import sys
    main(sys.argv)

