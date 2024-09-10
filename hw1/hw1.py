# homework 1
# goal: tokenize, index, boolean query
# exports: 
#   student - a populated and instantiated ir4320.Student object
#   Index - a class which encapsulates the necessary logic for
#     indexing and searching a corpus of text documents


# ########################################
# first, create a student object
# ########################################

import cs547
import PorterStemmer
import re
import glob
#import tokenize

import io

MY_NAME = "Shreya Boyane"
MY_ANUM  = 901029106 # put your WPI numerical ID here
MY_EMAIL = "ssboyane@wpi.edu"

# the COLLABORATORS list contains tuples of 2 items, the name of the helper
# and their contribution to your homework
COLLABORATORS = [ 
    ('Ankit Gole', 'helped me in code testing'),
    ]

# Set the I_AGREE_HONOR_CODE to True if you agree with the following statement
# "I do not lie, cheat or steal, or tolerate those who do."
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

# our index class definition will hold all logic necessary to create and search
# an index created from a directory of text files 
class Index(object):
    def __init__(self):
        # _inverted_index contains terms as keys, with the values as a list of
        # document indexes containing that term
        self._inverted_index = {}
        # _documents contains file names of documents
        self._documents = []
        # example:
        #   given the following documents:
        #     doc1 = "the dog ran"
        #     doc2 = "the cat slept"
        #   _documents = ['doc1', 'doc2']
        #   _inverted_index = {
        #      'the': [0,1],
        #      'dog': [0],
        #      'ran': [0],
        #      'cat': [1],
        #      'slept': [1]
        #      }


    #index_dir( base_path ):
    # purpose: crawl through a nested directory of text files and generate an
    #   inverted index of the contents
    # preconditions: none
    # returns: num of documents indexed
    # hint: glob.glob()
    # parameters:
    #   base_path - a string containing a relative or direct path to a
    #     directory of text files to be indexed




    def index_dir(self, base_path):
        num_files_indexed = 0
        # PUT YOUR CODE HERE
       # txt_files = glob.glob(base_path + '/**/*.txt', recursive=True)

        for filepath in glob.glob(f'{base_path}/*.txt'):
            self._documents.append(filepath)
            with open(filepath, 'r', encoding='utf-8') as file:
                text = file.read()

                tokens = self.tokenize(text)
                stemmed_tokens = self.stemming(tokens)
                print(stemmed_tokens)
                for token in stemmed_tokens:
                    if token not in self._inverted_index:
                        self._inverted_index[token] = set()
                    self._inverted_index[token].add(len(self._documents)-1)

                num_files_indexed += 1
        print(self._inverted_index)
        return num_files_indexed

    # tokenize( text )
    # purpose: convert a string of terms into a list of tokens.        
    # convert the string of terms in text to lower case and replace each character in text, 
    # which is not an English alphabet (a-z) and a numerical digit (0-9), with whitespace.
    # preconditions: none
    # returns: list of tokens contained within the text
    # parameters:
    #   text - a string of terms
    def tokenize(self, text):
        return re.findall(r'\b\w+\b', text.lower())

    # purpose: convert a string of terms into a list of tokens.        
    # convert a list of tokens to a list of stemmed tokens,     
    # preconditions: tokenize a string of terms
    # returns: list of stemmed tokens
    # parameters:
    #   tokens - a list of tokens
    def stemming(self, tokens):
        return [PorterStemmer.PorterStemmer().stem(token, 0, len(token) - 1) for token in tokens]

    # boolean_search( text )
    # purpose: searches for the terms in "text" in our corpus using logical OR or logical AND. 
    # If "text" contains only single term, search it from the inverted index. If "text" contains three terms including "or" or "and", 
    # do OR or AND search depending on the second term ("or" or "and") in the "text".  
    # preconditions: _inverted_index and _documents have been populated from
    #   the corpus.
    # returns: list of document names containing relevant search results
    # parameters:
    #   text - a string of terms
    def boolean_search(self, text):
        # PUT YOUR CODE HERE
        tokens = self.tokenize(text)
        stemmed_tokens = self.stemming(tokens)

        if len(stemmed_tokens) == 1:
            return self.single_term(stemmed_tokens[0])
        elif len(stemmed_tokens) == 3:
            if stemmed_tokens[1] == 'and':
                return self.single_term(stemmed_tokens[0])
            elif stemmed_tokens[1] == 'or':
                return self.OR(stemmed_tokens[0], stemmed_tokens[2])
        else:
            return []

    def single_term(self, word):
        if word in self._inverted_index:
            return [self._documents[doc_id] for doc_id in self._inverted_index[word]]


    def AND(self, word1, word2):
        if word1 in self._inverted_index and word2 in self._inverted_index:
            # Convert the lists to sets before intersecting
            return [self._documents[doc_id] for doc_id in (set(self._inverted_index[word1]) & set(self._inverted_index[word2]))]
        else:
            return []

    def OR(self, word1, word2):

        docs = set()
        if word1 in self._inverted_index:
            docs.update(self._inverted_index[word1])
        if word2 in self._inverted_index:
            docs.update(self._inverted_index[word2])
        return [self._documents[doc_id] for doc_id in docs]


    

# now, we'll define our main function which actually starts the indexer and
# does a few queries
def main(args):
    print(student)
    index = Index()
    print("starting indexer")
    num_files = index.index_dir('data/')
    print("indexed %d files" % num_files)
    for term in ('football', 'mike', 'sherman', 'mike OR sherman', 'mike AND sherman'):
        results = index.boolean_search(term)
        print("searching: %s -- results: %s" % (term, ", ".join(results)))

# this little helper will call main() if this file is executed from the command
# line but not call main() if this file is included as a module
if __name__ == "__main__":
    import sys
    main(sys.argv)

