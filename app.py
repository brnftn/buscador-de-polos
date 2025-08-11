import streamlit as st
import requests
from bs4 import BeautifulSoup
import unicodedata
from datetime import datetime
import pandas as pd

# Função para extrair polos do site oficial (IES)
def extract_polos_ies(url: str) -> list[str]:
    try:
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(resp.text, 'html.parser')
        polos = set()

        # Captura apenas o <p> dentro do .card-body
        for item in soup.select(".card-body p"):
            text = item.get_text(strip=True)
            if text:
                polos.add(normalize(text))
        return sorted(polos)
    except Exception as e:
        st.error(f"Erro ao extrair polos do site IES: {e}")
        return []

# Função para extrair polos do nosso site
def extract_polos_nosso_site(url: str) -> list[str]:
    try:
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(resp.text, 'html.parser')
        polos = set()

        # Captura apenas textos em negrito (b ou strong)
        for item in soup.find_all(["b", "strong"]):
            text = item.get_text(strip=True)
            if text:
                polos.add(normalize(text))
        return sorted(polos)
    except Exception as e:
        st.error(f"Erro ao extrair polos do nosso site: {e}")
        return []

# Interface Streamlit
st.title("Comparador de Polos UFBRA")

url_nosso = st.text_input("URL - Nosso Site", "https://ufbra.com.br/unidades")
url_ies = st.text_input("URL - Fonte Oficial (IES)", "https://ufbra.edu.br/polos")

if st.button("Gerar Listas"):
    polos_nosso = extract_polos_nosso_site(url_nosso)
    polos_ies = extract_polos_ies(url_ies)

    st.write(f"**Data/hora da verificação:** {datetime.now():%d/%m/%Y %H:%M:%S}")

    # Exibir tabelas lado a lado
    df = pd.DataFrame({
        "Polos do Nosso Site": pd.Series(polos_nosso),
        "Polos Fonte Oficial": pd.Series(polos_ies)
    })

    st.dataframe(df.fillna("-"))






