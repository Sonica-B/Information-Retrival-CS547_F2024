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
import numpy as np
import bs4 as BeautifulSoup  # you will want this for parsing html documents
import re
from collections import defaultdict
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import urllib.request

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

        self.index = defaultdict(set)  # Inverted index
        self.urls = set()              # All indexed URLs
        self.links = defaultdict(set)  # Outgoing links per URL
        self.pagerank_scores = {}      # PageRank scores
        self.max_depth = 5
        self.depth = 0


    # index_url( url )
    # purpose: crawl through a web directory of html files and generate an
    #   index of the contents
    # preconditions: none
    # returns: num of documents indexed
    # hint: use BeautifulSoup and urllib
    # parameters:
    #   url - a string containing a url to begin indexing at

    def index_url(self, url):
        """Crawl and index the given URL, with a max recursion depth to prevent infinite recursion."""
        # Base case: stop if the depth exceeds the maximum allowed depth
        if self.depth > self.max_depth:
            return

        try:
            # Fetch the URL content
            response = urllib.request.urlopen(url)
            html = response.read().decode('utf-8')
            soup = BeautifulSoup(html, 'html.parser')

            # Add URL to the set of indexed URLs
            self.urls.add(url)

            # Tokenize and index the content
            content = soup.get_text()
            tokens = self.tokenize(content)
            for token in tokens:
                self.index[token].add(url)

            # Extract hyperlinks
            for link in soup.find_all('a', href=True):
                href = urljoin(url, link['href'])
                if href not in self.urls:  # Only follow new links
                    self.links[url].add(href)
                    # Increment the recursion depth before calling recursively
                    self.depth += 1
                    self.index_url(href)
                    # Decrement depth when returning from recursion
                    self.depth -= 1

            print(f"Indexed {url} with {len(self.links[url])} outgoing links.")

            # Once done indexing root URL (depth == 0), calculate PageRank
            if self.depth == 0:
                print("Finished indexing, calculating PageRank...")
                self.calculate_pagerank()

        except Exception as e:
            print(f"Error indexing {url}: {e}")



    # tokenize( text )
    # purpose: convert a string of terms into a list of terms 
    # preconditions: none
    # returns: list of terms contained within the text
    # parameters:
    #   text - a string of terms
    def tokenize(self, text):
        """Convert input text into a list of lowercase alphanumeric tokens."""
        return re.findall(r'[a-zA-Z0-9]+', text.lower())

    def calculate_pagerank(self, d=0.1, tol=1.0e-6, max_iter=100):
        """Calculate PageRank scores using Numpy for matrix operations, handling dangling pages."""
        N = len(self.urls)
        if N == 0:
            return

        url_list = list(self.urls)
        url_index = {url: i for i, url in enumerate(url_list)}
        M = np.zeros((N, N))

        # Build the adjacency matrix
        for url, outgoing_links in self.links.items():
            if len(outgoing_links) > 0:
                for link in outgoing_links:
                    if link in url_index:
                        M[url_index[link], url_index[url]] = 1 / len(outgoing_links)
        print(f"Adjacency matrix (M):\n{M}")
        # Handle dangling pages (those with no outgoing links)
        dangling_nodes = [url_index[url] for url in self.urls if len(self.links[url]) == 0]

        # Initialize PageRank vector
        rank = np.ones(N) / N
        teleport = np.ones(N) / N

        # PageRank iteration
        for i in range(max_iter):
            new_rank = (1 - d) * teleport + d * M @ rank

            # Add rank from dangling nodes
            if dangling_nodes:
                dangling_sum = d * sum(rank[dangling_nodes]) / N
                new_rank += dangling_sum

            if np.linalg.norm(new_rank - rank, 1) < tol:
                print(f"PageRank converged after {i} iterations.")
                break
            rank = new_rank
        print(f"Final PageRank vector:\n{rank}")
        # Store PageRank scores
        self.pagerank_scores = {url_list[i]: rank[i] for i in range(N)}


    # ranked_search( text )
    # purpose: searches for the terms in "text" in our index and returns
    #   AND results for highest 10 ranked results
    # preconditions: .index_url(...) has been called on our corpus
    # returns: list of tuples of (url,PageRank) containing relevant
    #   search results
    # parameters:
    #   text - a string of query terms
    def ranked_search(self, text):
        tokens = self.tokenize(text)
        results = defaultdict(float)

        for token in tokens:
            if token in self.index:
                for url in self.index[token]:
                    results[url] += self.pagerank_scores.get(url, 0)

        ranked_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
        print(f"Ranked search results for query '{text}':\n{ranked_results[:10]}")
        return ranked_results[:10]



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

