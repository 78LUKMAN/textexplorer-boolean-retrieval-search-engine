##----------------##
## LUKMANUL HAKIM ##
## A11.2022.14197 ##
##----------------##


## pake api openlibrary.org
# import streamlit as st
# import requests

# def search_books(query):
#     base_url = "http://openlibrary.org/search.json"
#     params = {'q': query}
#     response = requests.get(base_url, params=params)
#     if response.status_code == 200:
#         return response.json().get('docs', [])
#     else:
#         return []


# def main():
#     query = "kancil"

#     if query:
#         books = search_books(query)
#         if books:
#             for book in books:
#                 print(book.get('title', 'No Title'))
#                 print(book.get('author_name', ['Unknown Author']))
#                 print(book.get('first_publish_year', 'Unknown'))
#                 print(book.get('subject', ['Not available'])[:5])  # Display first 5 subjects

# if __name__ == "__main__":
#     main()


import pandas as pd

file_path = "dataset/books.csv"
df = pd.read_csv(file_path)

def process_boolean_query(query):
    terms = query.split()
    results = []
    operator = None

    for term in terms:
        if term.upper() == "AND":
            operator = "AND"
        elif term.upper() == "OR":
            operator = "OR"
        elif term.upper() == "NOT":
            operator = "NOT"
        else:
            current_results = df[df['Book-Title'].str.contains(term, case=False, na=False)]

            if operator == "AND" and results:
                results = pd.merge(results, current_results, how='inner')
            elif operator == "OR":
                results = pd.concat([results, current_results]).drop_duplicates()
            elif operator == "NOT":
                results = results[~results['Book-Title'].isin(current_results['Book-Title'])]
            else:
                results = current_results

    return results

query = "night"

# lihat 5 data
print(df.head())
if query:
    books = process_boolean_query(query)
    if not books.empty:
        for idx, row in books.head(20).iterrows():
            print(f"{row['Book-Title']} - {row['Book-Author']} - {row['Year-Of-Publication']}")
    else:
        print("No results found.")

