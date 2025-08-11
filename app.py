import streamlit as st
import requests
from bs4 import BeautifulSoup
import unicodedata
from datetime import datetime
import pandas as pd

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

def extract_polos_ies(url: str) -> list[str]:
    try:
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(resp.text, 'html.parser')
        polos = set()

        for card in soup.select(".card-body"):
            rows = card.select(".row.p-2")
            for row in rows:
                p = row.find("p")
                if p:
                    text = p.get_text(strip=True)
                    if text:
                        polos.add(normalize(text))
        return sorted(polos)
    except Exception as e:
        st.error(f"Erro ao extrair polos do site IES: {e}")
        return []

def extract_polos_nosso_site(url: str) -> list[str]:
    try:
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(resp.text, 'html.parser')
        polos = set()

        for item in soup.find_all(["b", "strong"]):
            text = item.get_text(strip=True)
            if text:
                polos.add(normalize(text))
        return sorted(polos)
    except Exception as e:
        st.error(f"Erro ao extrair polos do nosso site: {e}")
        return []

st.title("Comparador de Polos Marcas")

url_nosso = st.text_input("URL - Nosso Site", "https://ufbra.com.br/unidades")
url_ies = st.text_input("URL - Fonte Oficial (IES)", "https://ufbra.edu.br/polos")

if st.button("Gerar Listas"):
    polos_nosso = extract_polos_nosso_site(url_nosso)
    polos_ies = extract_polos_ies(url_ies)

    st.write(f"**Data/hora da verificação:** {datetime.now():%d/%m/%Y %H:%M:%S}")

    # Cria lista única de todos os polos (união)
    todos_polos = sorted(set(polos_nosso) | set(polos_ies))

    # Para cada polo, checar presença em cada lista e definir ação
    acoes = []
    for polo in todos_polos:
        in_nosso = polo in polos_nosso
        in_ies = polo in polos_ies
        if in_ies and not in_nosso:
            acoes.append("Incluir Polo")
        elif in_nosso and not in_ies:
            acoes.append("Excluir Polo")
        else:
            acoes.append("-")

    # Monta DataFrame para exibir
    df = pd.DataFrame({
        "Polo": todos_polos,
        "No Nosso Site": [ "Sim" if p in polos_nosso else "-" for p in todos_polos ],
        "Na Fonte Oficial": [ "Sim" if p in polos_ies else "-" for p in todos_polos ],
        "Ação": acoes
    })

    st.dataframe(df)
