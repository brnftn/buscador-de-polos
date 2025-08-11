import streamlit as st
import requests
from bs4 import BeautifulSoup
import unicodedata
from datetime import datetime
import pandas as pd

# Função para normalizar nomes
def normalize(name: str) -> str:
    s = name.strip()
    for prefix in ["UFBRA - ", "POLO: ", "Polo ", "polo "]:
        if s.lower().startswith(prefix.lower()):
            s = s[len(prefix):]
            break
    s = ' '.join(s.split())  # remove espaços extras
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')  # remove acentos
    s = s.replace('–', '-')
    return s.casefold()

# Função para extrair polos do site oficial (IES)
def extract_polos_ies(url: str) -> list[str]:
    try:
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(resp.text, 'html.parser')
        polos = set()

        # Para cada .card-body, pega apenas o primeiro <p>
        for card in soup.select(".card-body"):
            p = card.find("p")  # pega só o primeiro <p> dentro do card-body
            if p:
                text = p.get_text(strip=True)
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




