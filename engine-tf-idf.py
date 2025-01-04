import pandas as pd
import streamlit as st
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from datetime import datetime
import webbrowser

class BooleanTFIDFSearchEngine:
    def __init__(self, df):
        self.df = df
        self.vectorizer = TfidfVectorizer(lowercase=True, stop_words='english')
        # preprocessing judul buku untuk TF-IDF
        self.processed_titles = self.df['title'].fillna('').apply(self.preprocess_text)
        # membuat matriks TF-IDF
        self.tfidf_matrix = self.vectorizer.fit_transform(self.processed_titles)
        
    def preprocess_text(self, text):
        """Membersihkan dan memproses teks"""
        # konversi ke lowercase dan hapus karakter khusus
        text = str(text).lower()
        text = re.sub(r'[^\w\s]', '', text)
        return text
    
    def boolean_filter(self, query):
        """Melakukan filtering boolean dasar"""
        terms = query.split()
        results = []
        operator = None
        filtered_indices = set(range(len(self.df)))
        
        for term in terms:
            if term.upper() in ['AND', 'OR', 'NOT']:
                operator = term.upper()
                continue
                
            # mencari indeks dokumen yang mengandung term
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
    
    def calculate_query_similarity(self, query, doc_indices):
        """Menghitung similarity antara query dan dokumen menggunakan TF-IDF"""
        # preprocessing query
        processed_query = self.preprocess_text(query)
        # transformasi query ke vektor TF-IDF
        query_vector = self.vectorizer.transform([processed_query])
        
        # menghitung cosine similarity
        similarities = cosine_similarity(query_vector, 
                                      self.tfidf_matrix[doc_indices]).flatten()
        
        # mengembalikan indeks dokumen dan nilai similaritasnya
        return list(zip(doc_indices, similarities))
    
    def search(self, query, min_similarity=0.0):
        """Melakukan pencarian dengan boolean filtering dan ranking TF-IDF"""
        # hapus operator boolean dari query untuk perhitungan TF-IDF
        search_terms = ' '.join([term for term in query.split() 
                               if term.upper() not in ['AND', 'OR', 'NOT']])
        
        # lakukan boolean filtering
        filtered_indices = self.boolean_filter(query)
        
        if not filtered_indices:
            return pd.DataFrame()
        
        # hitung similarity dan ranking
        doc_similarities = self.calculate_query_similarity(search_terms, filtered_indices)
        
        # filter berdasarkan minimum similarity dan urutkan
        ranked_docs = [(idx, score) for idx, score in doc_similarities 
                      if score >= min_similarity]
        ranked_docs.sort(key=lambda x: x[1], reverse=True)
        
        # ambil hasil yang sudah diranking
        if ranked_docs:
            indices, scores = zip(*ranked_docs)
            results = self.df.iloc[list(indices)].copy()
            results['Similarity_Score'] = scores
            return results
        return pd.DataFrame()

# fungsi untuk mengkonversi string tanggal ke tahun
def extract_year_from_date(date_str):
    try:
        if pd.isna(date_str):
            return None
        # asumsi format tanggal adalah 'YYYY-MM-DD'
        return int(str(date_str).split('-')[0])
    except:
        return None

# streamlit 
st.title("TextExplorer - Book Finder")

# dataset
file_path = "dataset/bookv2.csv"
df = pd.read_csv(file_path)

# konversi kolom publishedDate ke tahun
df['Publication_Year'] = df['publishedDate'].apply(extract_year_from_date)

# inisialisasi search engine
search_engine = BooleanTFIDFSearchEngine(df)

# gunakan data yang memiliki tahun valid
df_with_year = df[df['Publication_Year'].notna()].copy()

# rentang tahun untuk filter
min_year = int(df_with_year['Publication_Year'].min())
max_year = int(df_with_year['Publication_Year'].max())
year_ranges = {
    f"{max_year-4} - {max_year}": (max_year-4, max_year),
    f"{max_year-9} - {max_year-5}": (max_year-9, max_year-5),
    f"{max_year-14} - {max_year-10}": (max_year-14, max_year-10)
}

# filter berdasarkan rentang tahun
filtered_df = df.copy()
st.write("Filter by Publication Year:")
show_all = st.checkbox("Show All Years", value=False)

if not show_all:
    for label, (start_year, end_year) in year_ranges.items():
        count = len(df_with_year[
            (df_with_year['Publication_Year'] >= start_year) & 
            (df_with_year['Publication_Year'] <= end_year)
        ])
        
        if st.checkbox(f"{label} ({count} books)"):
            filtered_df = filtered_df[
                (filtered_df['Publication_Year'] >= start_year) & 
                (filtered_df['Publication_Year'] <= end_year)
            ]

# minimum similarity threshold (untuk menyesuaikan skor kesamaan dengan kata kunci)
min_similarity = st.slider("Minimum Similarity Score", 0.0, 1.0, 0.1, 0.05)

#  query
query = st.text_input("Enter your search query (e.g., 'Harry AND Potter OR Sorcerer NOT Stone')")

#proses pencarian# Proses pencarian
if query:
    search_engine = BooleanTFIDFSearchEngine(filtered_df)
    results = search_engine.search(query, min_similarity)
    
    if not results.empty:
        st.write(f"Found {len(results)} results")
        # urutkan berdasarkan similarity score
        results = results.sort_values('Similarity_Score', ascending=False)
        
        # buat dictionary untuk menyimpan state tombol
        if 'button_states' not in st.session_state:
            st.session_state.button_states = {}
        
        # tampilkan hasil
        for idx, row in results.iterrows():
            # Buat unique key untuk setiap baris
            unique_key = f"item_{idx}"
            
            # container untuk setiap item
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
                    
                    # tombol dengan unique key
                    if st.button("Get Item", key=unique_key, type="primary"):
                        webbrowser.open(row['productURL'])
                    
                st.write("---")  # pemisah antar item
    else:
        st.write("No results found.")