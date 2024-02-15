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

### CMD Parameters
* `precision`: must be a real number between 0 and 1 (can include 1 for perfect precision).
* `query in quotation marks`: must an intentionally ambigious search keyword or phrase within quotation marks (i.e. "per se").
  
## Internal Design
Our program is designed to take 4 arguments passed through the command line by the user: `JSON API KEY`, `GOOGLE SEARCH ENGINE KEY`, `precision@K`, and `a query in quotation marks`. When valid parameters are passed, the program proceeds by...

1. Making a call to Google for a custom search on the query
2. Returning results (max 10) to the user for relevance feedback one-by-one. **Note:** results will only be presented to the user if they are HTML (not PDT, PowerPoint, `.csv`, etc.). The number of valid results given to the user are iteratively counted as they are processed.
3. Asking the used to asses each result as relevant ('Y') or non-relevant ('N') to their query. The number of relevant results are counted

### Non-HTML Result Handling


### Fixed Values and Parameters
The following values are fixed within the code. Further modification can be done outside the scope of this project to make these customizable from the user perspective if desired.
* `num=10` - number of results returned from an API call to Google (can be fewer if the top 10 Google hits include non-HTML results).
* `alpha=1` - Rocchio alpha weight (default value from original algorithm design)
* `beta=.9` - Rocchio beta weight
* `gamma=1` - Rocchio gamma weigh
   
### External Libraries
Our programs relies on the following Python frameworks:

|Library | Use |
|---------|------------|
|`sys`| Used to get arguments from the command line (i.e. JSON API key, Google Search Engine Key, Percision, Query).|
|`re`| Used to clean search results into more uniform terms byt dropping punctuation and other non-alphanumeric characters.|
|`requests`| Used in the `search()` function to make a call Google's custom search engine API. Responses converted to JSON for processing.|
|`sklearn`|Using `TfidfVectorizer` to calculate tf-idf score for each term in returned results and generate a term vector.|
|`nltk`| Used to collect English stopwords for stopword elimination from term list.|

## Query Modification Method

## External References
1. Manning, Raghavan, & Schütze. Stanford University. (2009). Information Retrieval and Web Search (Online Edition) - Chapter 9: Query Operations. Retrieved from https://nlp.stanford.edu/IR-book/pdf/09expand.pdf

2. “Custom Search JSON API  |  Google for Developers.” Google, Google, developers.google.com/custom-search/v1/reference/rest/v1/Search. Accessed 10 Feb. 2024. 
