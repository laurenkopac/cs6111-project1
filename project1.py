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
    # Seperate out hypened words
    cleaned_text = text.replace('-', ' ').lower()
    # Remove non-alphanumeric characters
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', cleaned_text)

    return cleaned_text

def relevance_feedback(original_query, relevant_feedback, non_relevant_feedback, alpha=1, beta=0.75, gamma=0.15):
    """
    Relevance Feedback Function
    Description:

    """

    original_query = [term.lower() for text in original_query for term in text.split()]
    relevant_feedback = [clean_terms(term) for text in relevant_feedback for term in text.split() if ((term not in STOP_WORDS) & (len(term) > 1) & (term not in string.punctuation) & (term != "..."))]
    non_relevant_feedback = [clean_terms(term) for text in non_relevant_feedback for term in text.split() if ((term not in STOP_WORDS) & (len(term) > 1) & (term not in string.punctuation) & (term != "..."))]

    # Initalize dictionary for relevant term frequencies
    frequency_count = {}

    for term in relevant_feedback:
        # Using get method to handle the case where the word is not in the dictionary
        frequency_count[term] = frequency_count.get(term, 0) + 1

    # Create vectors for the original query, relevant, and non-relevant feedback
    original_query_vector = {}
    relevant_feedback_vector = {}
    non_relevant_feedback_vector = {}

    for term in original_query:
        original_query_vector[term] = original_query_vector.get(term, 0) + 1

    for term in relevant_feedback:
        relevant_feedback_vector[term] = relevant_feedback_vector.get(term, 0) + 1

    for term in non_relevant_feedback:
        non_relevant_feedback_vector[term] = non_relevant_feedback_vector.get(term, 0) + 1

    # Update the query using Rocchio's algorithm
    updated_query_vector = {}
    for term in set(original_query + relevant_feedback + non_relevant_feedback):
        term_weight = alpha * original_query_vector.get(term, 0) + beta * relevant_feedback_vector.get(term, 0) - gamma * non_relevant_feedback_vector.get(term, 0) + frequency_count.get(term,0) # give extra weight to frequent relevant terms
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
          relevant_results = []
          non_relevant_results = []

          # Initialize link counters
          ## Count valid links (HTML results based on fileFormat field
          qualified_resutls = 0

          ## Count relevant links indicated by user ('y')
          relevant_links = 0 

          # Loop through each search result one at a time, ask user for feedback
          for i, result in enumerate(json['items'], 1):
                # Return only HTML results for user
                    if result.get('fileFormat') is None:
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
                    if feedback.strip().lower() == 'y':
                        relevant_links += 1
                        relevant_results.append(result['title'])
                        relevant_results.append(result.get('snippet'))

                    else:
                        non_relevant_results.append(result['title'])
                        non_relevant_results.append(result.get('snippet'))

        
          # check if there was any relevant results indicated by user, if not exit
          augmented_query = ""
          percision = relevant_links / qualified_resutls
          if relevant_links <= 0:
            print("===================================================")
            print("FEEDBACK SUMMARY")
            print(f"Query {query} ")
            print(f"Precision {percision}")
            print(f"Still below the desired percision of {target}.")
            print("Indexing results....")
            print("Indexing results....")
            print(f"Augmenting by {augmented_query} ")  
            print("Below desiered precision, but cannot augment the query with 0 relevant results")
            sys.exit(0)   

          # If number of relevant results is less than 9 (score of .9)...
            
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

          # Terminate code - desired precision reached
          else:
            print("===================================================")
            print("FEEDBACK SUMMARY")
            print(f"Precision {percision}")
            print(f"Desired precision reached, done.")
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
    print(f"""Parameters:\n
    Client Key = {api_key}\n
    Engine Key = {cx}\n
    Query      = {query}\n
    Precision  = {percision}\n
    Google Search Results:
    ======================
    """)

def main():
    # Read in the required keys, precision, and query from command-line
    api_key, cx, target, query = cmd_line()

    # Initiate search with user input
    search(query, target, api_key, cx)

if __name__ == "__main__":
    main()
    