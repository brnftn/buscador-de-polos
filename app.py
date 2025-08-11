import streamlit as st
import requests
from bs4 import BeautifulSoup
import unicodedata
from datetime import datetime

def normalize(name: str) -> str:
    s = name.strip()
    for prefix in ["UFBRA - ", "POLO: ", "Polo ", "polo "]:
        if s.lower().startswith(prefix.lower()):
            s = s[len(prefix):]
            break
    s = ' '.join(s.split())  # elimina espaços extras
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')  # remove acentos
    s = s.replace('–', '-')
    return s.casefold()

def extract_polos(url: str) -> list[str]:
    try:
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(resp.text, 'html.parser')
        textos = soup.find_all(string=True)
        nomes = set()
        for txt in textos:
            t = txt.strip()
            if len(t) > 3:
                nomes.add(normalize(t))
        return sorted(nomes)
    except Exception as e:
        st.error(f"Erro ao extrair polos de: {url}\n{e}")
        return []

st.title("Comparador de Polos UFBRA")

url1 = st.text_input("URL - Nosso Site (polos)", "https://ufbra.com.br/unidades")
url2 = st.text_input("URL - Fonte Oficial (site IES)", "https://ufbra.edu.br/polos")

if st.button("Gerar Listas"):
    polos1 = extract_polos(url1)
    polos2 = extract_polos(url2)

    st.write(f"**Data/hora da verificação:** {datetime.now():%d/%m/%Y %H:%M:%S}")

    df = {
        "Polos do Nosso Site": polos1,
        "Polos Fonte Oficial": polos2,
    }
    import pandas as pd
    df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in df.items()]))
    st.dataframe(df.fillna("-"))
