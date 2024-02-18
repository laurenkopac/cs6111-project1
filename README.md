# CS6111 Advanced Database Systems Spring 24 - Project 1
Feb 19, 2024

## Team
Amari Byrd (ab5311) and Lauren Kopac (ljk2148)

## Files in Submission
|File Name| Description|
|---------|------------|
|`feedback.py`| Project 1 `.py` file|
|`README.pdf` | PDF version of `README.md` file on Github|
|`transcript.pdf`| PDF transcript of test case results |


## API Keys
|Key Name | Key|
|---------|------------|
|JSON API KEY| `AIzaSyBHRHOxxGtFuRU3bfpVkGKc29_R8jN6Gu8`|
|Google Search Engine Key|`f2d45d63dda814dd6`|

## How to Use
Navigate to the project 1 folder in Google Cloud:

```bash
$ source /home/ab5311/Project1
```
In the Project1 directory, run:

```bash
$ python3 feedback.py <json api key> <google engine id> <precision> <query in quotation marks>
```
**Note:** `precision` must be a real number between 0 and 1 (can include 1 for perfect precision) and `query in quotation marks` must be an intentionally ambigious search keyword or phrase within quotation marks (i.e. "per se").
  
## Internal Design
Our program is designed to take 4 arguments passed through the command line by the user: `JSON API KEY`, `GOOGLE SEARCH ENGINE KEY`, `precision`, and `a query in quotation marks`. When valid parameters are passed, the program proceeds with three main components and their associated methods:

|Phase| Component | Description |Associated Methods|
|---------|---------|------------|------------|
|1|Retrieval and presentation of Google Search Results for user | The program will first accept a set of parameters from the user. If valid, the program will print back the parameters for the user in the terminal. Next, an API call will be made to Google's custom search engine. One API call will be made per iteration of collecting relevance feedback (i.e. returning 10 results (displayed one at a time) will count as one iteration and therefore one API call). The API call processes and returns only HTML results back for the user (see section below on how non-HTML results are handled). | <ul><li>`cmd_line()`</li><li>`search(query,target,api_key,cx,k_results=10)`</li><li>`query_print_cmd(api_key, cx, query, target)`</li></ul>|
|2| Relevance feedback collection |One at a time, the user must decide if the result is relevant or not to their query. Relevant and non-relevant results are sorted and stored accordingly, pulling text from result titles and summaries. **Possible outcomes:** If, after the inital search, the desired precision is reached, the program will exit. If no results at all are marked as relevant, the program will exit and ask the user to try a new query. If no results are fetched, the program will exit and ask the user to try again. If results are turned, but do not meet the precision requirements, the program will move to the next phase of query augmentation.| Relevance feedback is collected from the user within the `search()` method as results are displayed following an API call to Google.|
|3| Query Augmentation | After the results have been saved and sorted as either relevant or nonrelevant, terms are passed through `relevance_feedback()` method, which calls upon `clean_terms()` and `calculate_tf_idf()` to determine and extract two terms to best augment the original query for the user. See Query Modification Method section below for more details. The augmented query, which will always contain the original query, will then be used to call `search()` until the desired precision is reached or the program reaches another exit contition.| <ul><li>`relevance_feedback(original_query, relevant_feedback, non_relevant_feedback, alpha=1, beta=0.9, gamma=.1)`</li><li>`clean_terms(text)`</li><li>`calculate_tf_idf(documents)`</li></ul>|

### Custom Methods
|Method | Params |Description |
|---------|------------|------------|
|`cmd_line()`| `None`| Take arguments from the user via the command line. Assert that: <ul><li>The correct number of arguments have been passsed to run the program</li><li>Precision provided is a real number between 0 and 1 inclusive</li><li>Query is not empty</li></ul>|
|`search(query,target,api_key,cx,k_results=10)`| <ul><li>`query` - user provided query</li><li>`target` - user provided desired precision</li><li>`api_key` - JSON API Key (see Keys section above)</li><li> `cx` - Google Search Engine Key (see Keys section above)</li><li>`k_results` - number of results returned by API call (default set to 10)</li></ul>| API call to Google Search results for user inputed query. Takes user inputed keys, query, and desired precision (real number 0-1). Returns query results to user for relevance feedback.|
|`relevance_feedback(original_query, relevant_feedback, non_relevant_feedback, alpha=1, beta=0.9, gamma=.1)`|<ul><li>`original_query` - original query inputed by the user through the command line or most recently used augmented query</li><li>`relevant_feedback` - list of raw text from results deemed relevant to the user</li><li>`non_relevant_feedback` - list of raw text from results deemed not relevant</li><li>`alpha` - value for the Rocchio algo, default to 1</li><li>`beta` - value for the Rocchio algo, set to .9</li><li>`gamma` - value for the Rocchio algo - set to .1</li></ul>|

### Non-HTML Result Handling
Results will only be presented to the user if they are HTML (not PDT, PowerPoint, `.csv`, etc.). 

We weed out these unwanted filed types by relying on the JSON field `fileFormat` from the returned resutls of our API calls. In the case where the result is not some unwanted filetype, and is instead an HTML result, this field will be `None`.

```python
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
```


### Fixed Values and Parameters
The following values are fixed within the code. Further modification can be done outside the scope of this project to make these customizable from the user perspective if desired.
* `k_results=10` - number of results returned from an API call to Google (can be fewer if the top 10 Google hits include non-HTML results).
* `alpha=1` - Rocchio alpha weight (default value from original algorithm design)
* `beta=.9` - Rocchio beta weight
* `gamma=.1` - Rocchio gamma weight (default value from original algorithm design)
   
### External Libraries
Our programs relies on the following Python frameworks:

|Library | Use |
|---------|------------|
|`sys`| Used to get arguments from the command line (i.e. JSON API key, Google Search Engine Key, Percision, Query).|
|`re`| Used to clean search results into more uniform terms byt dropping punctuation and other non-alphanumeric characters.|
|`requests`| Used in the `search()` function to make a call Google's custom search engine API. Responses converted to JSON for processing.|
|`sklearn`|Using `TfidfVectorizer` to calculate tf-idf score for each term in returned results and generate a term vector.|
|`nltk`| Used to collect English stopwords for stopword elimination from term list. Also used for stemming terms with `RegexpStemmer`|

## Query Modification Method

Our query modification is handled in a few methods inspiried by idologies from lecture and the textbook.

## External References
1. Manning, Raghavan, & Schütze. Stanford University. (2009). Information Retrieval and Web Search (Online Edition) - Chapter 9: Query Operations. Retrieved from https://nlp.stanford.edu/IR-book/pdf/09expand.pdf

2. “Custom Search JSON API  |  Google for Developers.” Google, Google, developers.google.com/custom-search/v1/reference/rest/v1/Search. Accessed 10 Feb. 2024. 
