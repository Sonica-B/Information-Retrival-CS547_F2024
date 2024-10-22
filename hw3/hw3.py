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
from bs4 import BeautifulSoup
import urllib.request
import numpy as np
from collections import defaultdict

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

        self.index = defaultdict(list)  # Maps terms to URLs containing them
        self.outlinks = defaultdict(list)  # Maps URLs to outgoing links
        self.inlinks = defaultdict(list)  # Maps URLs to incoming links
        self.pagerank = {}  # Store PageRank of URLs
        self.urls = set()  # Set of all URLs crawled (initialize here)


    # index_url( url )
    # purpose: crawl through a web directory of html files and generate an
    #   index of the contents
    # preconditions: none
    # returns: num of documents indexed
    # hint: use BeautifulSoup and urllib
    # parameters:
    #   url - a string containing a url to begin indexing at

    def index_url(self, url):
        # Crawl starting from given URL
        num_files = 0
        to_crawl = [url]  # Queue of URLs to crawl
        crawled = set()  # Keep track of crawled URLs

        while to_crawl:
            current_url = to_crawl.pop(0)
            if current_url in crawled:
                continue
            crawled.add(current_url)

            # Fetch and parse the HTML of the current URL
            try:
                response = urllib.request.urlopen(current_url)
                html = response.read().decode('utf-8')

                # Make sure BeautifulSoup is used correctly
                soup = BeautifulSoup(html, 'html.parser')

                num_files += 1
                self.urls.add(current_url)

                # Extract tokens and index them
                tokens = self.tokenize(soup.get_text())
                for token in tokens:
                    self.index[token].append(current_url)

                # Find all outgoing links (anchor tags)
                for anchor in soup.find_all('a', href=True):
                    link = anchor['href']
                    if link.startswith('http') and link not in self.outlinks[current_url]:
                        self.outlinks[current_url].append(link)
                        self.inlinks[link].append(current_url)
                        if link not in crawled and link not in to_crawl:
                            to_crawl.append(link)

            except Exception as e:
                print(f"Error crawling {current_url}: {e}")
                continue

        # After crawling, compute PageRank
        self._compute_pagerank()

        return num_files

    # tokenize( text )
    # purpose: convert a string of terms into a list of terms 
    # preconditions: none
    # returns: list of terms contained within the text
    # parameters:
    #   text - a string of terms
    def tokenize(self, text):
        # Convert text to lowercase and split on non-alphanumeric characters
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
        # Tokenize the query
        query_tokens = self.tokenize(text)

        # Find URLs that contain all query terms
        result_urls = set(self.index.get(query_tokens[0], []))
        for token in query_tokens[1:]:
            result_urls &= set(self.index.get(token, []))

        # Convert results into a NumPy array for efficient sorting
        if result_urls:
            results = np.array([(url, self.pagerank.get(url, 0)) for url in result_urls])
            # Sort by PageRank (descending)
            sorted_results = results[results[:, 1].argsort()[::-1]]
            return sorted_results[:10].tolist()

        return []

    def _compute_pagerank(self, d=0.1, max_iterations=100, tol=1e-6):
        N = len(self.urls)
        if N == 0:
            return

        # Initialize PageRank array
        pagerank = np.ones(N) / N  # Start with equal probability
        url_list = list(self.urls)
        url_index = {url: i for i, url in enumerate(url_list)}

        # Create adjacency matrix A (stochastic matrix)
        A = np.zeros((N, N))
        for i, url in enumerate(url_list):
            if self.outlinks[url]:
                out_deg = len(self.outlinks[url])
                for outlink in self.outlinks[url]:
                    if outlink in url_index:
                        j = url_index[outlink]
                        A[j, i] = 1 / out_deg

        # Power iteration: PageRank computation
        teleport = np.ones(N) / N  # Teleportation array
        for _ in range(max_iterations):
            new_pagerank = d * teleport + (1 - d) * A.dot(pagerank)

            # Check for convergence (L1 norm difference)
            if np.linalg.norm(new_pagerank - pagerank, 1) < tol:
                break
            pagerank = new_pagerank

        # Assign the computed PageRank back to URLs
        self.pagerank = {url_list[i]: pagerank[i] for i in range(N)}



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

