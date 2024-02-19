# Environment Set Up
import requests
import sys
import string
import re

## Import itertools for permutations
from itertools import permutations

## Import the sklearn library for TF-IDF weighting and bigram generation
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

## Import the nltk library for a list of english stop-words
import nltk
from nltk.corpus import stopwords
from nltk.stem import RegexpStemmer

nltk.download('stopwords')
nltk.download('pinkt')

# Get the list of English stop words, save unique values in a set
STOP_WORDS = set(stopwords.words('english'))

def cmd_line():
    """
    Command Line Input Function
    Description: Accept and validate command line arguments for api key, engine id, precision, and query from user
    Returns: api key, engine id, precision, and query
    """
    # Check if the correct number of command line arguments is provided
    if len(sys.argv) != 5:
        print("Usage: python3 feedback.py <google api key> <google engine id> <precision> <query in quotation>")
        sys.exit(1)

    # Extract command line arguments: google api key, google engine key, precision, and query
    json_api_key = sys.argv[1]
    google_engine_id = sys.argv[2]
    
    try:
        # Validate precision
        target = float(sys.argv[3])
        if not (0 < target <= 1):
            raise ValueError("Precision must be a number greater than 0 and less than/equal to 1.")
        
        query = sys.argv[4]

        # Validate query
        if not query:
            raise ValueError("Query is empty. input a query you want to search")
  
   # catch percision and query errors
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Return command line arguments
    return json_api_key, google_engine_id, target, query

def clean_terms(text):
    """
    Clean Results
    Description: Accept as input a term. Seperate out terms that are hypenated, remove any non alpha-numeric characters from term
    Return the cleaned term
    """
    # If the characters following a hypthen are numeric, remove the numbers
    if "-" in text:
        try:
            if text.split('-')[1].isnumeric():
                text = text.split('-')[0]
        except:
            pass

    # Remove non-alphanumeric characters
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', text)

    # Initialize the Porter Stemmer to stem plural terms
    stemmer = RegexpStemmer('s$', min=4)
    cleaned_text = stemmer.stem(cleaned_text)

    return cleaned_text.lower()

def calculate_tf_idf(documents, vectorizer):
    """
    Search Function
    Description: Calculates tf-idf score for each word in the document during the relevance feedback
    Takes documents containing snippets of the api user result
    Returns term vector as a dictionary containing the tf-idf score for each word in the document ((word:tf-idf score))
    credit: https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html
    credit: https://stackoverflow.com/questions/53294482/how-to-get-tf-idf-scores-for-the-words
    """
     
    # # create tf-idf vectorizer to calculate tf-idf score
    # vectorizer = TfidfVectorizer()

    # calculate tf-idf score for each word in the document (non-relevant, relevant, and original query)
    tfidf_vectors = vectorizer.transform(documents)

    # get term words
    document_word = vectorizer.get_feature_names_out()

    # create term vector for all terms in the document containing the tf-idf score and the word
    term_vector = dict(zip(document_word, tfidf_vectors.toarray().sum(axis=0)))

    # return the term vector
    return term_vector

def reorder_query(query,relevant_document):
    """
    Reorder Query Function
    Description: Generate new query by creating bigrams from all permutations of the query and finding the tf-idf score for each bigram vs all relevant documents
    Takes  query, the current query passed to api and updated query,  results from Rocchio's algorithm 
    Returns best ordered permutation of the query, based on highest tf-idf score
     credit: https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.CountVectorizer.html
    """

    # join all relevant documents into one string
    combined_relevant_docs = ' '.join(relevant_document)

    # create count vectorizer for creating bigrams 
    count_vectorizer = CountVectorizer(ngram_range=(2, 2))

    # Generate all permutations of the query
    query_perm = dict((' '.join(word), None) for word in permutations(query))

    # create tf-idf vectorizer to calculate tf-idf score in bigrams
    tfidf_vectorizer = TfidfVectorizer(ngram_range=(2,2), sublinear_tf=True)

    # calculate tf-idf score for each bigram in the relevant document
    _ = tfidf_vectorizer.fit([combined_relevant_docs])

    # get term words
    document_word = tfidf_vectorizer.get_feature_names_out()

    # loop through each permutation
    for perm in query_perm:
        # create bigrams of the current permutation
        perm_count_matrix = count_vectorizer.fit_transform([perm])
        
        # get bigram term words of the current permutation
        bigrams = count_vectorizer.get_feature_names_out()
       
        # calculate tf-idf score for each bigram in the current permutation
        perm_tdfif_vector = tfidf_vectorizer.transform(bigrams)
     
        # create term vector for all terms in the document containing the tf-idf score and the word
        term_vector = dict(zip(document_word, perm_tdfif_vector.toarray().sum(axis=0)))
       
        # Initialize the score
        current_score = 0

        # Loop through each bigram
        for b in bigrams:
            # get the tf-idf score of the bigram and add it to the current score if the bigram is in the relevant document else add 0
            current_score += term_vector.get(b,0)

        # Add the current score to the dictionary [perm] to represent the weight of the permutation
        query_perm[perm] = current_score

    # sort the permutations by weight in descending order
    sorted_query_perm = sorted(query_perm.items(), key=lambda x:x[1], reverse=True)

    # Return the best permutation to be new ordered query, one with highest weight
    return sorted_query_perm[0][0]

    

def relevance_feedback(original_query, relevant_feedback, non_relevant_feedback, alpha=1, beta=0.9, gamma=0.1):
    """
    Relevance Feedback Function
    Description: implement Rocchio's algorithm for relevance feedback based on user feedback on relevant and non-relevant documents from Google Search (y/n). 
    Calculates the updated query to improve search results by reducing irrelevant terms and increasing relevant terms.
    Takes original query, relevant feedback, array containing all relevant documents (y), non-relevant feedback, array containing all non-relevant documents(n).
    Consist of snippets and title from google search results.
    Takes alpha, beta, alpha, beta, and gamma for Rocchio's algorithm (1, 0.9, 0.1)
    Returns updated query, the new query including two new words to be used in the next search (the best query that leans more towards relevant search results)
    """
    
     # Clean the terms in the relevant and non-relevant feedback arrays (remove stop words, stemming) and store them in a list of terms ['per', 'se', ...]
    original_query = [term.lower() for text in original_query for term in text.split()]
    
    relevant_feedback = [clean_terms(term) for text in relevant_feedback for term in text.split() 
                         if ((term.lower() not in STOP_WORDS) & (len(term) > 1) & (term not in string.punctuation) & (term != "..."))]
    
    non_relevant_feedback = [clean_terms(term) for text in non_relevant_feedback for term in text.split() 
                             if ((term.lower() not in STOP_WORDS) & (len(term) > 1) & (term not in string.punctuation) & (term != "..."))]
    

    # Initialize the number of relevant and non-relevant docs
    relevant_docs_length = len(relevant_feedback)
    non_relevant_docs_length = len(non_relevant_feedback)

    # # Initalize dictionary for relevant term frequencies
    frequency_count = {}

    for term in relevant_feedback:
        # Using get method to handle the case where the word is not in the dictionary
        frequency_count[term] = frequency_count.get(term, 0) + 1
        
  
     # create tf-idf vectorizer to calculate tf-idf score
    vectorizer = TfidfVectorizer(use_idf=True, sublinear_tf=True)

    # calculate tf-idf score for each word in the document with a databse of both (non-relevant, relevant)
    tfidf_vectors = vectorizer.fit_transform(relevant_feedback + non_relevant_feedback)

    # Create term vectors for the original query, relevant, and non-relevant feedback
    original_query_vector = calculate_tf_idf(original_query, vectorizer)
    relevant_feedback_vector = calculate_tf_idf(relevant_feedback, vectorizer)
    non_relevant_feedback_vector = calculate_tf_idf(non_relevant_feedback, vectorizer)
    
    # Update the query using Rocchio's algorithm
    updated_query_vector = {}
    for term in set(original_query + relevant_feedback + non_relevant_feedback):
        # Calculate the new term weight of the term using Rocchio's algorithm
        term_weight = (
            alpha * original_query_vector.get(term, 0) # Original query component
            + 
            
            beta * ( 1 / relevant_docs_length)  * relevant_feedback_vector.get(term, 0)  #  relevant document component

            - 
            gamma * ( 1 / non_relevant_docs_length) * non_relevant_feedback_vector.get(term, 0)  # non-relevant document component
            
            + 
            frequency_count.get(term,0) # give extra weight to frequent relevant terms 
            ) 
        
        # Set the new term weight to 0 if it is less than 0 else set it to the new term weight (remove negative values)
        updated_query_vector[term] = max(0, term_weight)

    # Sort the terms in the updated query by weight in descending order, if the tie then sort by lexigraphic order
    sorted_terms = sorted(updated_query_vector.items(), key=lambda x: (x[1], x[0]), reverse=True)
    

    # Take the top two terms that were not in the original query
    # prevent duplicates from original query and stem terms ('apples','apple') in the new query -> [term for term in original_query] + [clean_terms(term) for term in original_query]
    
    top_two_terms = [term for term, _ in sorted_terms if term not in 
                     ([term for term in original_query] + [clean_terms(term) for term in original_query])][:2]
    
    # join the new top two terms with original query terms to represent the new query terms

    augmented_terms = top_two_terms + [term for term, _ in sorted_terms if term in original_query]
    
    # reorder the terms to find the final augmented query using bigrams and tf-idf weighting

    augmented_query = reorder_query(augmented_terms, relevant_feedback)

    # Combine the two new query terms (used to display to user the chosen terms in next iteration i.e. Augmented by restuarant newyork)

    new_augmented_terms = ' '.join(top_two_terms)

    # Return the new augmented query and the augmented terms
    return new_augmented_terms, augmented_query


def search(query,target, api_key, cx, k_results=10):
    """
    Search Function
    Description: API call to JSON API for Google Search results for user inputed query
    Takes user inputed API_Key, CS, query, and desired precision (real number 0-1)
    Returns query results to user for relevance feedback
    """
    # Initialize link counters
    ## Count valid links (HTML results based on fileFormat field
    qualified_results = 0

    ## Count relevant links indicated by user ('y')
    relevant_links = 0 

    try:
        # Display search parameters lines to user
        query_print_cmd(api_key, cx, query, target)

        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "q": query,
            "key": api_key,
            "cx": cx,
            "num": k_results
        }

        # Perform a Google search using the requests package
        response = requests.get(url, params=params)
        json = response.json()
        # Display search results
        if 'items' in json:
          # Initiaize a list to store results
          relevant_results = []
          non_relevant_results = []

          # Loop through each search result one at a time, ask user for feedback
          for i, result in enumerate(json['items'], 1):
                # Return only HTML results for user
                    if ((result.get('fileFormat') is None) | ('fileFormat' not in json)):
                        # Increase qualified results counter
                        qualified_results += 1
                        print(f"Result {i}")
                        print("[")
                        print(f" URL: {result['link']}")
                        print(f" Title: {result['title']}")
                        print(f" Summary: {result.get('snippet', 'No summary available')}")
                        print("]")
                        print()
                        feedback = input("Relevant (Y/N)?")

                    # Convert feedback to lower in case user enters inconsistently, remove accidental spaces
                    ## If user indicates relevant link - save title to relevant list
                
                    if feedback.strip().lower() == 'y' or feedback.strip().lower() == 'yes':
                        relevant_links += 1
                        relevant_results.append(result['title'])
                        relevant_results.append(result.get('snippet'))

                    elif feedback.strip().lower() == 'n' or feedback.strip().lower() == 'no':
                        non_relevant_results.append(result['title'])
                        non_relevant_results.append(result.get('snippet'))
                    
                    elif feedback.strip().lower() == '':
                        print("Invalid feedback. Feedback empty")
                        sys.exit(1)
                    

          # check if there was any relevant results indicated by user, if not exit
          augmented_query = ""
          if qualified_results == 0:
              print("======================")
              print("FEEDBACK SUMMARY")
              print(f"Query {query} ")
              print(f"HTML results found: {qualified_results} ")  
              ("No results returned. Please rewrite your query and try again.")
              sys.exit(0)   
          
          # Calculate precision now that we know qualified_results will not be 0
          percision = round((relevant_links / qualified_results),1)

          # If number of relevant results indicated by user is 0 ,
          #(program has not found any good results terminate progam), display summary and exit
          augmented_terms = ""

          if relevant_links == 0:
            print("======================")
            print("FEEDBACK SUMMARY")
            print(f"Query {query} ")
            print(f"Precision {percision}")
            print(f"Still below the desired percision of {target}.")
            print("Indexing results....")
            print("Indexing results....")
            print(f"Augmented by {augmented_terms}")
            print(f"Below desired precision, but can no longer augment the query")
            sys.exit(0)   

          # If number of relevant results is less than user inputed target, rerun search
          if percision < target:
            print("======================")
            print("FEEDBACK SUMMARY")
            print(f"Precision {percision}")
            print(f"Still below the desired percision of {target}.")
            print("Indexing results....")
            print("Indexing results....")
            print("Generating relevance feedback...")

            # Conduct relevance feedback (rocchio) to find next query and augmented terms that will be added to the previous query
            augmented_terms, augmented_query = relevance_feedback([query], relevant_results, non_relevant_results)

            # Display augmented terms to user
            print(f"Augmented by {augmented_terms}")
            
            # Recursively call search() until desired precision is reached
            search(augmented_query, target, api_key, cx)

          # Desired precision reached. Exit
          else:
            print("======================")
            print("FEEDBACK SUMMARY")
            print(f"Precision {percision}")
            print(f"Desired precision reached.")
            sys.exit(0)

    except Exception as e:
      # Return error if unable to get a response
      print(f"Error: {e}")
      sys.exit(1)

def query_print_cmd(api_key, cx, query, percision):
    """
    Query Print CMD
    Description: Display keys and current query to user (parameters and result line to be displayed before each search)
    """
    print('Parameters:')
    print(f"Client key = {api_key}")
    print(f"Engine key = {cx}")
    print(f"Query      = {query}")
    print(f"Precision  = {percision}")
    print(f"Google Search Results:")
    print("======================")


# Main function - start of the relevance feedback process
def main():
    # Read in the required keys, precision, and query from command-line
    api_key, cx, target, query = cmd_line()

    # Initiate search with user input
    search(query, target, api_key, cx)

if __name__ == "__main__":
    main()