# Dohvat filmova
# Pisanje funkcije za dohvat podataka iz naše tablice

import streamlit as st
import pandas as pd
import gspread

def učitaj_podatke():
    podaci_računa=dict(st.secrets["gcp_service_account"])
    klijent=gspread.service_account_from_dict(podaci_računa)
    tablica=klijent.open("FILMOVI")
    radni_list=tablica.worksheet("filmovi")
    podaci=radni_list.get_all_records()
    filmovi=pd.DataFrame(podaci)
    return filmovi, radni_list

filmovi, radni_list=učitaj_podatke()

# Prikaz filmova
# Prikaz podataka iz naše tablice

if not filmovi.empty:
    filmovi["Godina"]=pd.to_numeric(
        filmovi["Godina"],
        errors="coerce"
    )

    filmovi["Ocijena"]=pd.to_numeric(
        filmovi["Ocjena"],
        errors="coerce"
    )

st.title("Moji omiljeni filmovi")
st.subheader("Trenutni popis filmova")

if filmovi.empty:
    st.info("U tablici još nema filmova.")
else:
    st.dataframe(
        filmovi,
        hide_index=True, 
    )

# Dodavanje filmova
# Dodajemo nekoliko filmova u našu tablicu

st.subheader("Dodaj novi film")

with st.form("forma za dodavanje filma", clear_on_submit=True):
    naslov=st.text_input("Naslov: ")
    godina=st.number_input("Godina:",
                           min_value=1900, max_value=2100,
                           value=None, placeholder="Unesite godinu")
    žanr=st.text_input("Žanr:")
    ocjena=st.slider("Ocjena:",
                     min_value=1, max_value=10, value=5)
    gumb_dodaj=st.form_submit_button("Dodaj film")

if gumb_dodaj:
    if naslov.strip() and žanr.strip() and godina is not None:
        novi_red=[naslov.strip(), int(godina), žanr.strip(), ocjena]
        radni_list.append_row(novi_red)
        st.success("Film je uspješno dodan")
        st.rerun()
    else:
        st.warning("Unesite naslov, godinu i žanr filma.")

# Pretraživanje filmova
# Omogučimo pretraživanje filmova po žanru i godini

st.subheader("Pretraži filmove")

if filmovi.empty:
    st.info("Nema filmova za pretraživanje.")
else:
    traženi_žanr=st.text_input("Pretraži po žanru: ", placeholder="Primjerice: triler")
    tražena_godina=st.number_input("Pretraži po godini: ", min_value=1900, max_value=2100,
                                   value=None, placeholder="Unesite godinu")
    filtrirani_filmovi=filmovi

    if traženi_žanr.strip():
        filtrirani_filmovi=filtrirani_filmovi[
            filtrirani_filmovi["Žanr"].str.contains(traženi_žanr.strip(), case=False)
        ]

    if tražena_godina is not None:
        filtrirani_filmovi=filtrirani_filmovi[filtrirani_filmovi["Godina"]==int(tražena_godina)
        ]

    if filtrirani_filmovi.empty:
        st.info("Nije pronađen nijedan film.")

    else:
        st.dataframe(filtrirani_filmovi, hide_index=True)

# Brisanje filmova
# Obrišimo neki film iz naše tablice

st.subheader("Izbriši film")

if filmovi.empty:
    st.info("Nema filmova za brisanje")
else:
    def opis_filma(indeks):
        film=filmovi.iloc[indeks]

        return (
            f"{film["Naslov"]} "
            f"({int(film["Godina"])}) | "
            f"{film["Žanr"]} | "
            f"Ocjena: {film["Ocjena"]}"
        )

    odabrani_indeks=st.selectbox(
        "Odaberi film za brisanje: ",
        options=range(len(filmovi)),
        index=None,
        placeholder="Odaberite film",
        format_func=opis_filma
    )

    if st.button("Izbriši film"):
        if odabrani_indeks is not None:
            redak_u_tablici=odabrani_indeks+2
            radni_list.delete_rows(redak_u_tablici)
            st.rerun()

        else:
            st.warning("Najprije odaberite film za brisanje.")

# Najbolji filmovi
# Prikažimo 3 najbolja filma po ocjeni

st.subheader("Top 3 filma po ocjeni")

if filmovi.empty():
    st.info("Nema filmova za prikaz.")

else:
    najbolja_tri=filmovi.sort_values(
        by="Ocjena",
        ascending=False
    ).head(3)

    st.dataframe(
        najbolja_tri, 
        hide_index=True
    )


