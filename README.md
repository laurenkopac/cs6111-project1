# CS6111 Advanced Database Systems - Project 1

## Authors
Amari Byrd (ab5311) and Lauren Kopac (ljk2148)

## Files in Repo
|File Name| Description|
|---------|------------|
|`feedback.py`| Project 1 `.py` file|

## API Keys
|Key Name | Key|
|---------|------------|
|JSON API KEY| `AIzaSyBHRHOxxGtFuRU3bfpVkGKc29_R8jN6Gu8`|
|Google Search Engine Key|`83cef68fbbe834498`|

## How to Use
Navigate to the project 1 folder in Google Cloud:

```
source /home/ab5311/Project1
```
In the Project1 directory, run:

```
python3 feedback.py <json api key> <google engine id> <precision> <query in quotation>"
```
## Work Flow
Our program is designed to take 4 arguments passed through the command line by the user: `JSON API KEY`, `GOOGLE SEARCH ENGINE KEY`, `precision@K`, and `a query in quotation marks`. When valid parameters are passed, the program proceeds by...

1. Making a call to Google for a custom search on the query
2. Returning results (max 10) to the user for relevance feedback one-by-one. **Note:** results will only be presented to the user if they are HTML (not PDT, PowerPoint, `.csv`, etc.). The number of valid results given to the user are iteratively counted as they are processed.
3. Asking the used to asses each result as relevant ('Y') or non-relevant ('N') to their query. The number of relevant results are counted 
   
