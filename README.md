# 🚲 Bike Sharing Dashboard

Dashboard analisis data penyewaan sepeda mengenai Bike Sharing Dataset, Tahun 2011–2012.

## 📁 Struktur File
```
Dashboard/
submission
├───dashboard
| ├───merged_bike.csv
| └───dashboard.py
├───data
| ├───day.csv
| └───hour.csv
├───notebook.ipynb
├───README.md
└───requirements.txt
```

## Setup Environment - Anaconda
```
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
```
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run steamlit app
```
streamlit run dashboard.py
``` -m streamlit run dashboard.py
```

Dashboard akan terbuka otomatis di browser pada `http://localhost:8501`
