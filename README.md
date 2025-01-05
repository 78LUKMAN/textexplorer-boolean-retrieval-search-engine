# Preview
![image](https://github.com/user-attachments/assets/c3b8440b-13c9-4128-8f3b-c473c1bb1fbf)
## q : harry potter
![image](https://github.com/user-attachments/assets/544c9bfa-4068-474a-80cd-001293368f6d)
## q : harry potter NOT stone
![image](https://github.com/user-attachments/assets/69b989e4-559a-4eba-94e2-f20d7d07d792)

# Panduan Instalasi

## Prasyarat

### 1. Instalasi Python
Pertama, Anda perlu menginstal Python di sistem Anda:

- **Windows**: 
  - Unduh Python dari [python.org](https://python.org)
  - Saat instalasi, pastikan mencentang "Add Python to PATH"

- **Linux**:
```bash
sudo apt update
sudo apt install python3 python3-pip
```

- **macOS**:
```bash
brew install python3
```

## Langkah-langkah Instalasi

### 1. Mengunduh Repository
```bash
git clone https://github.com/78LUKMAN/textexplorer-boolean-retrieval-search-engine.git
cd textexplorer-boolean-retrieval-search-engine
```

### 2. Membuat Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalasi Dependensi yang Diperlukan
Setelah virtual environment aktif, install paket-paket yang diperlukan:

```bash
pip install pandas
pip install streamlit
pip install scikit-learn
```

Atau, buat file `requirements.txt` dengan isi:
```
pandas
streamlit
scikit-learn
```

Kemudian install menggunakan:
```bash
pip install -r requirements.txt
```

## Menjalankan Aplikasi

1. Pastikan virtual environment sudah aktif
2. Jalankan aplikasi Streamlit:

```bash
streamlit run app.py
```

Secara default, aplikasi akan terbuka di browser Anda dengan alamat `http://localhost:8501`

## Struktur Proyek
```
root/
│
├── dataset/         # Folder untuk menyimpan dataset
│    ├── bookv2.csv
│
├── models/          # Folder untuk menyimpan model     
│    ├── books_df.pkl
│    ├── processed_titles.pkl
│    ├── tfidf_matrix.pkl
│    ├── vectorizer.pkl
│
└── app.py           # File utama aplikas
```
Pastikan Anda memiliki semua file yang diperlukan di direktori proyek:
- `app.py` - Aplikasi utama Streamlit
- File pickle (`.pkl`) untuk model yang digunakan
- Dataset atau file lain yang diperlukan

## Penyelesaian Masalah

Jika mengalami masalah:

1. Periksa instalasi Python:
```bash
python --version  # atau python3 --version
```

2. Pastikan virtual environment aktif (akan terlihat `(venv)` di terminal)

3. Periksa instalasi paket:
```bash
pip list
```

4. Jika ada masalah dengan Streamlit:
```bash
streamlit --version
```

## Perintah Penting

Ringkasan perintah yang sering digunakan:

```bash
# Mengaktifkan virtual environment
# Windows
.\venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# Menonaktifkan virtual environment
deactivate

# Menginstal dependensi
pip install -r requirements.txt

# Menjalankan aplikasi
streamlit run app.py
```

## Persyaratan Sistem

- Python 3.7 atau lebih tinggi
- RAM yang cukup untuk memuat model dan memproses data
- Ruang disk untuk dependensi dan file model
- Browser web modern (Chrome, Firefox, Safari, atau Edge)

## Catatan Tambahan

- Pastikan semua file model (`.pkl`) berada di lokasi yang benar
- Aplikasi akan membuka browser secara otomatis saat dijalankan
- Jika browser tidak terbuka otomatis, buka manual di `http://localhost:8501`
- Untuk menghentikan aplikasi, tekan `Ctrl+C` di terminal
