##----------------##
## LUKMANUL HAKIM ##
## A11.2022.14197 ##
##----------------##

import pandas as pd
import streamlit as st
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import webbrowser

class SearchEngine:
    def __init__(self):
        self.load_model_components()
    
    def load_model_components(self):
        """Load all saved model components"""
        try:
            with open('models/vectorizer.pkl', 'rb') as f:
                self.vectorizer = pickle.load(f)
            
            with open('models/tfidf_matrix.pkl', 'rb') as f:
                self.tfidf_matrix = pickle.load(f)
            
            with open('models/processed_titles.pkl', 'rb') as f:
                self.processed_titles = pickle.load(f)
            
            self.df = pd.read_pickle('models/books_df.pkl')
            return True
        except Exception as e:
            st.error(f"Error loading model components: {str(e)}")
            return False
    
    def preprocess_text(self, text):
        """Clean and preprocess text"""
        text = str(text).lower()
        text = re.sub(r'[^\w\s]', '', text)
        return text
    
    def boolean_filter(self, query):
        """Perform boolean filtering"""
        terms = query.split()
        filtered_indices = set(range(len(self.df)))
        operator = None
        
        for term in terms:
            if term.upper() in ['AND', 'OR', 'NOT']:
                operator = term.upper()
                continue
            
            term_indices = set([i for i, title in enumerate(self.processed_titles) 
                              if term.lower() in title])
            
            if operator == 'AND':
                filtered_indices &= term_indices
            elif operator == 'OR':
                filtered_indices |= term_indices
            elif operator == 'NOT':
                filtered_indices -= term_indices
            else:
                filtered_indices = term_indices
        
        return list(filtered_indices)
    
    def search(self, query, min_similarity=0.0, start_year=None, end_year=None, show_all_years=False):
        """Perform search with boolean filtering and TF-IDF ranking"""
        # hapus operator boolean untuk perhitungan kemiripan
        search_terms = ' '.join([term for term in query.split() 
                               if term.upper() not in ['AND', 'OR', 'NOT']])
        
        # Dapatkan indeks yang telah difilter
        filtered_indices = self.boolean_filter(query)
        
        if not filtered_indices:
            return pd.DataFrame()
        
        # jika show_all_years tidak dicentang, terapkan filter tahun
        if not show_all_years and start_year is not None and end_year is not None:
            filtered_indices = [
                idx for idx in filtered_indices
                if self.df.loc[idx, 'publishedDate'] is not None
                and extract_year_from_date(self.df.loc[idx, 'publishedDate']) is not None
                and (start_year <= extract_year_from_date(self.df.loc[idx, 'publishedDate']) <= end_year)
            ]
        
        # periksa apakah ada hasil filter sebelum menghitung kemiripan cosine
        if not filtered_indices:
            return pd.DataFrame()
        
        # hitung skor kesamaan
        processed_query = self.preprocess_text(search_terms)
        query_vector = self.vectorizer.transform([processed_query])
        
        # memastikan tidak ada matriks yang kosong
        if query_vector.shape[0] == 0 or self.tfidf_matrix[filtered_indices].shape[0] == 0:
            return pd.DataFrame()
        
        similarities = cosine_similarity(query_vector, 
                                        self.tfidf_matrix[filtered_indices]).flatten()
        
        # saring dan urutkan hasilnya
        doc_similarities = list(zip(filtered_indices, similarities))
        ranked_docs = [(idx, score) for idx, score in doc_similarities 
                      if score >= min_similarity]
        ranked_docs.sort(key=lambda x: x[1], reverse=True)
        
        if ranked_docs:
            indices, scores = zip(*ranked_docs)
            results = self.df.iloc[list(indices)].copy()
            results['Similarity_Score'] = scores
            return results
        return pd.DataFrame()

def extract_year_from_date(date_str):
    """Extract year from date string"""
    try:
        if pd.isna(date_str):
            return None
        return int(str(date_str).split('-')[0])
    except:
        return None

# streamlit
st.title("TextExplorer - Book Finder")

# muat engine dengan model yang di-cache
@st.cache_resource
def initialize_search_engine():
    engine = SearchEngine()
    return engine

search_engine = initialize_search_engine()

# kolom pencarian
min_similarity = st.slider("Minimum Similarity Score", 0.0, 1.0, 0.1, 0.05)
query = st.text_input("Enter your search query (e.g., 'Harry AND Potter OR Sorcerer NOT Stone')")

# fitur filter tahun
start_year = st.number_input("Start Year", min_value=1900, max_value=2100, value=1900, step=1)
end_year = st.number_input("End Year", min_value=1900, max_value=2100, value=2025, step=1)

# Checkbox untuk menampilkan semua buku alias mengabaikan filter tahun
show_all_years = st.checkbox("Show All Years (ignore the above filter)", value=False)

# proses pencarian
if query:
    results = search_engine.search(query, min_similarity, start_year, end_year, show_all_years)
    
    if not results.empty:
        st.write(f"Found {len(results)} results")
        results = results.sort_values('Similarity_Score', ascending=False)
        
        for idx, row in results.iterrows():
            with st.container():
                col1, col2 = st.columns(2)
                
                with col1:
                    try:
                        st.image(row['imgUrl'], width=300)
                    except:
                        st.write("Image not available")
                
                with col2:
                    st.write(f"**Title**: {row['title']}")
                    st.write(f"**Author**: {row['author']}")
                    st.write(f"**Publication Date**: {row['publishedDate']}")
                    st.write(f"**Rate**: {row['stars']}")
                    st.write(f"**Category**: {row['category']}")
                    st.write(f"**Similarity Score**: {row['Similarity_Score']:.4f}")
                    
                    if st.button("Get Item", key=f"item_{idx}", type="primary"):
                        webbrowser.open(row['productURL'])
                
                st.write("---")
    else:
        st.write("No results found. Please adjust your search criteria.")
