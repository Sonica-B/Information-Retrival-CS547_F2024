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

        self.index = defaultdict(list)  # Store tokens and their corresponding URLs
        self.pagerank_scores = defaultdict(float)  # Store PageRank scores
        self.outgoing_links = defaultdict(set)  # Store outgoing links for each URL
        self.incoming_links = defaultdict(set)  # Store incoming links for each URL
        self.urls = set()  # Keep track of all URLs indexed


    # index_url( url )
    # purpose: crawl through a web directory of html files and generate an
    #   index of the contents
    # preconditions: none
    # returns: num of documents indexed
    # hint: use BeautifulSoup and urllib
    # parameters:
    #   url - a string containing a url to begin indexing at

    def index_url(self, url):
        """Parse the index page and find all valid anchor tags (links)"""
        # Fetch and parse the URL
        try:
            response = urllib.request.urlopen(url)
            html = response.read().decode('utf-8')
            soup = BeautifulSoup(html, 'html.parser')

            # Tokenize the content and update index
            text = soup.get_text()
            tokens = self.tokenize(text)
            for token in tokens:
                self.index[token].append(url)

            # Extract <a> tags only
            for link in soup.find_all('a', href=True):
                full_url = urljoin(url, link['href'])
                if full_url not in self.urls:
                    self.index_url(full_url)  # Recursively index linked URLs
                    print(self.index)
                self.outgoing_links[url].add(full_url)
                self.incoming_links[full_url].add(url)
                print(self.outgoing_links)
                print(self.incoming_links)
            self.urls.add(url)

        except Exception as e:
            print(f"Error indexing URL {url}: {e}")


# def build_graph(self, index_url):
#         """Build the web graph starting from the index page"""
#         print(f"Indexing root page: {index_url}")
#         links = self.index_url(index_url)
#
#         # Add the root as a node and link it to the extracted links
#         self.graph[index_url].extend(links)
#
#         # Now visit each link and extract further links if they are part of the corpus
#         for link in links:
#             if link not in self.graph:  # Only process if not already visited
#                 if link in self.corpus:  # Check if it exists in our web corpus
#                     print(f"Indexing linked page: {link}")
#                     sub_links = self.index_url(link)
#                     self.graph[link].extend(sub_links)
#                 else:
#                     print(f"Treating {link} as a leaf node (outside corpus)")
#
#         # DEBUG: Print web graph
#         print("\nWeb Graph:")
#         for page, links in self.graph.items():
#             print(f"{page} -> {links}")

    # tokenize( text )
    # purpose: convert a string of terms into a list of terms 
    # preconditions: none
    # returns: list of terms contained within the text
    # parameters:
    #   text - a string of terms
    def tokenize(self, text):
        return re.findall(r'[a-z0-9]+', text.lower())
        # tokens = []
        # current_token = []
        #
        # for char in text:
        #     if char.isalnum():  # Accept alphanumeric characters
        #         current_token.append(char)
        #     elif current_token:
        #         tokens.append("".join(current_token).lower())  # Convert token to lowercase
        #         current_token = []
        #
        # if current_token:
        #     tokens.append("".join(current_token).lower())  # Add last token
        #
        # return tokens



    def compute_pagerank(self, d=0.9, max_iterations=100, tol=1.0e-6):
            # Initialize PageRank scores
            N = len(self.urls)
            for url in self.urls:
                self.pagerank_scores[url] = 1.0 / N

            for i in range(max_iterations):
                new_pagerank_scores = defaultdict(float)

                # Compute PageRank for each URL
                for url in self.urls:
                    rank_sum = sum(self.pagerank_scores[link] / len(self.outgoing_links[link]) for link in
                                   self.incoming_links[url])
                    new_pagerank_scores[url] = (1 - d) / N + d * rank_sum

                # Check for convergence
                if all(abs(new_pagerank_scores[url] - self.pagerank_scores[url]) < tol for url in self.urls):
                    break

                self.pagerank_scores = new_pagerank_scores


    # ranked_search( text )
    # purpose: searches for the terms in "text" in our index and returns
    #   AND results for highest 10 ranked results
    # preconditions: .index_url(...) has been called on our corpus
    # returns: list of tuples of (url,PageRank) containing relevant
    #   search results
    # parameters:
    #   text - a string of query terms
    def ranked_search(self, text):
        # Tokenize search text
        tokens = self.tokenize(text)
        results = defaultdict(float)

        # Find documents containing all tokens
        for token in tokens:
            if token in self.index:
                for url in self.index[token]:
                    results[url] += self.pagerank_scores[url]

        # Sort results by PageRank score (descending)
        ranked_results = sorted(results.items(), key=lambda x: x[1], reverse=True)

        # Return top 10 results
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

