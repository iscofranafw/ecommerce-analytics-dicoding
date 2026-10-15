# E-Commerce Public Dataset Analytics Dashboard

Proyek ini menganalisis performa penjualan kategori produk, distribusi geografis pelanggan, serta segmentasi pelanggan berbasis RFM (*Recency, Frequency, Monetary*) pada **E-Commerce Public Dataset** (periode 2017–2018).

## Struktur Direktori
- `dashboard/`: Berisi aplikasi Streamlit (`dashboard.py`) dan dataset hasil pembersihan (`main_data.csv`).
- `data/`: Berisi dataset mentah E-Commerce Public Dataset (`.csv`).
- `Proyek_Analisis_Data.ipynb`: Jupyter Notebook berisi tahapan lengkap *Data Wrangling*, *Exploratory Data Analysis (EDA)*, *Visualization & Explanatory Analysis*, serta *RFM Analysis & Manual Grouping*.
- `requirements.txt`: Daftar pustaka Python yang dibutuhkan.
- `url.txt`: Tautan menuju dashboard yang telah di-*deploy* di Streamlit Cloud.

## Cara Menjalankan Dashboard di Local

1. **Clone atau ekstrak repositori ini dan masuk ke direktori proyek:**
   ```bash
   cd submission
   .\.venv\Scripts\Activate.ps1        
   streamlit run dashboard/dashboard.py
   ```