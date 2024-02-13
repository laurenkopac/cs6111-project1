# Environment Set Up
import requests
import sys
import string
import re

from sklearn.feature_extraction.text import TfidfVectorizer

## Import the nltk library for a list of english stop-words
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')

# Get the list of English stop words, save unique values in a set
STOP_WORDS = set(stopwords.words('english'))

def cmd_line():
    """
    Relevance Feedback Function
    Description:

    """
    # Check if the correct number of command line arguments is provided
    if len(sys.argv) != 5:
        print("Usage: python3 feedback.py <google api key> <google engine id> <precision> <query in quotation>")
        sys.exit(1)

    # Extract command line arguments: google api key, google engine key, precision, and query
    json_api_key = sys.argv[1]
    google_engine_id = sys.argv[2]
    
    try:
        target = float(sys.argv[3])
        if not (0 < target <= 1):
            raise ValueError("Precision must be a number greater than 0 and less than/equal to 1.")
        
        query = sys.argv[4]

        if not query:
            raise ValueError("Query is empty. input a query you want to search")
  
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

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

    return cleaned_text.lower()



def calculate_tf_idf(documents):
    """
    Search Function
    Description: Calculates tf-idf score for each word in the document 
    Takes documents containing snippets of the api user result
    Returns term vector as a dictionary containing the tf-idf score for each word in the document ((word:tf-idf score))
    """
     
    #calculate the idf_score for vector
    vectorizer = TfidfVectorizer(analyzer='word')
    tfidf_matrix = vectorizer.fit_transform(documents)

    # get term words
    document_word = vectorizer.get_feature_names_out()

    # create term vector for all terms in the document 
    term_vector = dict((word, idf_score) for word, idf_score in zip(document_word, tfidf_matrix.toarray()[0]))

    return term_vector

def get_new_query(original_query,updated_query):
    """
    Get New Query Function
    Description: Generate new query by getting two new words based on weights from relevance feedback and reorder them with n-grams
    Takes original query, the current query passed to api and updated query,  results from Rocchio's algorithm 
    Returns new query with two new words
    """
    # TODO - get two new words based on updated query contains terms and weights and 
    # find the two new words with highest tf-idf weight and add them to the original query) and find the best 
    #reordering of the new query with n-grams sklearn library (sklearn.feature_extraction.text.CountVectorizer)
    # and return the updated query

    pass

def relevance_feedback(original_query, relevant_feedback, non_relevant_feedback, alpha=1, beta=0.9, gamma=1):
    """
    Relevance Feedback Function
    Description:

    """
    relevant_docs_length = len(relevant_feedback)
    non_relevant_docs_length = len(non_relevant_feedback)
    original_query = [term.lower() for text in original_query for term in text.split()]
    relevant_feedback = [clean_terms(term) for text in relevant_feedback for term in text.split() if ((term not in STOP_WORDS) & (len(term) > 1) & (term not in string.punctuation) & (term != "..."))]
    non_relevant_feedback = [clean_terms(term) for text in non_relevant_feedback for term in text.split() if ((term not in STOP_WORDS) & (len(term) > 1) & (term not in string.punctuation) & (term != "..."))]

    # Initalize dictionary for relevant term frequencies
    frequency_count = {}

    for term in relevant_feedback:
        # Using get method to handle the case where the word is not in the dictionary
        frequency_count[term] = frequency_count.get(term, 0) + 1


   #TODO: DELETE THIS LATER
    # #Create vectors for the original query, relevant, and non-relevant feedback
    # original_query_vector = {}
    # relevant_feedback_vector = {}
    # non_relevant_feedback_vector = {}

    # for term in original_query:
    #     original_query_vector[term] = original_query_vector.get(term, 0) + 1

    # for term in relevant_feedback:
    #     relevant_feedback_vector[term] = relevant_feedback_vector.get(term, 0) + 1

    # for term in non_relevant_feedback:
    #     non_relevant_feedback_vector[term] = non_relevant_feedback_vector.get(term, 0) + 1

    original_query_vector = calculate_tf_idf(original_query)
    relevant_feedback_vector = calculate_tf_idf(relevant_feedback)
    non_relevant_feedback_vector = calculate_tf_idf(non_relevant_feedback)

    # Update the query using Rocchio's algorithm
    updated_query_vector = {}
    for term in set(original_query + relevant_feedback + non_relevant_feedback):

        term_weight = (
            alpha * original_query_vector.get(term, 0) 
            + 

            beta * relevant_feedback_vector.get(term, 0) * 1 / relevant_docs_length 

            - 
            gamma * non_relevant_feedback_vector.get(term, 0) * 1 / non_relevant_docs_length
            + 
            frequency_count.get(term,0) # give extra weight to frequent relevant terms
            ) 
        
        updated_query_vector[term] = max(0, term_weight)

    # Sort the terms by weight in descending order
    sorted_terms = sorted(updated_query_vector.items(), key=lambda x: x[1], reverse=True)

    # Take the top two terms that were not in the original query
    top_two_terms = [(term,weight) for term, weight in sorted_terms if term not in original_query][:2]

    # Bring in the original query terms
    augmented_terms = top_two_terms + [(term, weight) for term, weight in sorted_terms if term in original_query]

    # Sort new query terms by their weights
    new_sorted_terms = sorted(augmented_terms, key=lambda x: x[1], reverse=True)

    # Create the final augmented query
    augmented_query = ' '.join([term for term, _ in new_sorted_terms])
    new_augmented_terms = ' '.join([term for term, _ in top_two_terms])

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

          print 
          relevant_results = []
          non_relevant_results = []

          # Loop through each search result one at a time, ask user for feedback
          for i, result in enumerate(json['items'], 1):
                # Return only HTML results for user
                    if result.get('fileFormat') is None:
                        print("blah123")
                        # Increase qualified results counter
                        qualified_results += 1
                        print(f"Result {i}")
                        print("[")
                        print(f"URL: {result['link']}")
                        print(f"Title: {result['title']}")
                        print(f"Summary: {result.get('snippet', 'No summary available')}")
                        print("]")
                        print()
                        feedback = input("Relevant (Y/N)? ")

                    # Convert feedback to lower in case user enters inconsistently, remove accidental spaces
                    ## If user indicates relevant link - save title to relevant list
                    print("feedback: ", feedback)
                    if feedback.strip().lower() == 'y':
                        relevant_links += 1
                        relevant_results.append(result['title'])
                        relevant_results.append(result.get('snippet'))

                    else:
                        non_relevant_results.append(result['title'])
                        non_relevant_results.append(result.get('snippet'))

          # check if there was any relevant results indicated by user, if not exit
          augmented_query = ""
          if qualified_results == 0:
              print("===================================================")
              print("FEEDBACK SUMMARY")
              print(f"Query {query} ")
              print(f"HTML results found: {qualified_results} ")  
              ("No results returned. Please rewrite your query and try again.")
              sys.exit(0)   
          
          # Calculate precision now that we know qualified_results will not be 0
          percision = round((relevant_links / qualified_results),1)

          if relevant_links == 0:
            print("===================================================")
            print("FEEDBACK SUMMARY")
            print(f"Query {query} ")
            print(f"Precision {percision}")
            print(f"Number of relevant results: {relevant_links}.")
            print("Below desiered precision, but cannot augment the query with 0 relevant results")
            sys.exit(0)   

          # If number of relevant results is less than user inputed target, rerun search
          if percision < target:
            print("===================================================")
            print("FEEDBACK SUMMARY")
            print(f"Precision {percision}")
            print(f"Still below the desired percision of {target}.")
            print("Indexing results....")
            print("Indexing results....")
            print("Generating relevance feedback...")

            augmented_terms, augmented_query = relevance_feedback([query], relevant_results, non_relevant_results)
            print(f"Augmented by {augmented_terms}")
            # Recursively call search() until desired precision is reached
            search(augmented_query, target, api_key, cx)

          # Desired precision reached. Exit
          else:
            print("===================================================")
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
    Description: Display user input from the command line
    """
    print('Parameters:')
    print(f"Client Key = {api_key}")
    print(f"Engine Key = {cx}")
    print(f"Query      = {query}")
    print(f"Precision  = {percision}")
    print(f"Google Search Results:")
    print("======================")

def main():
    # Read in the required keys, precision, and query from command-line
    api_key, cx, target, query = cmd_line()

    # Initiate search with user input
    search(query, target, api_key, cx)

if __name__ == "__main__":
    main()
