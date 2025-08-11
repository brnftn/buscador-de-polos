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

def extract_polos_ies_com_estado(url: str) -> list[tuple[str, str]]:
    """
    Retorna lista de (estado, polo) extraídos do site oficial (IES).
    """
    try:
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(resp.text, 'html.parser')
        resultado = []

        # Cada card representa um grupo Estado + polos
        cards = soup.select(".card")
        for card in cards:
            header = card.select_one(".card-header")
            if not header:
                continue
            estado = header.get_text(strip=True)

            body = card.select_one(".card-body")
            if not body:
                continue

            rows = body.select(".row.p-2")
            for row in rows:
                p = row.find("p")
                if p:
                    polo_nome = p.get_text(strip=True)
                    if polo_nome:
                        resultado.append((normalize(estado), normalize(polo_nome)))
        return resultado
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

st.title("Comparador de Polos UFBRA")

url_nosso = st.text_input("URL - Nosso Site", "https://ufbra.com.br/unidades")
url_ies = st.text_input("URL - Fonte Oficial (IES)", "https://ufbra.edu.br/polos")

if st.button("Gerar Listas"):
    polos_nosso = extract_polos_nosso_site(url_nosso)
    polos_ies_com_estado = extract_polos_ies_com_estado(url_ies)

    st.write(f"**Data/hora da verificação:** {datetime.now():%d/%m/%Y %H:%M:%S}")

    # Criar dict polo->estado para consulta rápida
    dict_polo_estado = {polo: estado for estado, polo in polos_ies_com_estado}

    # Lista só dos polos da fonte oficial (sem estado)
    polos_ies = sorted({polo for _, polo in polos_ies_com_estado})

    # Lista única de todos polos (união)
    todos_polos = sorted(set(polos_nosso) | set(polos_ies))

    acoes = []
    estados = []
    for polo in todos_polos:
        in_nosso = polo in polos_nosso
        in_ies = polo in polos_ies

        estados.append(dict_polo_estado.get(polo, "-"))  # estado ou '-' se não existir

        if in_ies and not in_nosso:
            acoes.append("Incluir Polo")
        elif in_nosso and not in_ies:
            acoes.append("Excluir Polo")
        else:
            acoes.append("-")

    df = pd.DataFrame({
        "Estado": estados,
        "Polo": todos_polos,
        "No Nosso Site": ["Sim" if p in polos_nosso else "-" for p in todos_polos],
        "Na Fonte Oficial": ["Sim" if p in polos_ies else "-" for p in todos_polos],
        "Ação": acoes
    })

    st.dataframe(df)
