#WEB

from functions import (initialize, new_profile, give_song, puntua,
                       print_data, get_spotify_link, get_embed_link,
                       new_genre_preferences, install_libraries)

install_libraries()

import streamlit as st
import pandas as pd
import base64
import os


# Configuración de la página
st.set_page_config(
    page_title="Descobreix cançons al teu gust",
    layout="centered"
)


import streamlit.components.v1 as components

#Funció que s'executa unicament el primer cop que es visita la web,
#No cada cop que l'usuari interactua
@st.cache_resource
def carregar():
    initialize()
    return True


carregar()




# Carpeta donde está guardado este archivo app.py
CARPETA_APP = os.path.dirname(os.path.abspath(__file__))
numSongs = 0
nom_usuari = ""


# Imagen de fondo
ruta_fons = os.path.join(CARPETA_APP, "fondo.png")


# ==================================================
# FUNCIÓN PARA PONER LA IMAGEN DE FONDO
# ==================================================


def posar_fons(ruta_imatge):
    """
    Carga una imagen como fondo de la aplicación.
    Si no encuentra la imagen, muestra un aviso
    en lugar de detener el programa.
    """


    if not os.path.isfile(ruta_imatge):
        st.warning(
            f"No s'ha trobat la imatge de fons: {ruta_imatge}"
        )
        return


    try:
        with open(ruta_imatge, "rb") as imatge:
            contingut = imatge.read()


        imatge_base64 = base64.b64encode(
            contingut
        ).decode("utf-8")


        # Detectar el formato real de la imagen
        if contingut.startswith(b"\x89PNG\r\n\x1a\n"):
            format_imatge = "png"
        elif contingut.startswith(b"\xff\xd8\xff"):
            format_imatge = "jpeg"
        else:
            format_imatge = "jpeg"


        css = f"""
        <style>
        .stApp {{
            background-image: url(
                "data:image/{format_imatge};base64,{imatge_base64}"
            );
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """


        st.markdown(css, unsafe_allow_html=True)


    except OSError as error:
        st.warning(
            f"No s'ha pogut carregar la imatge de fons: {error}"
        )


# Posar totes les lletres en blanc
st.markdown("""
<style>


/* Textos en blanc, amb una mica d'ombra perquè es llegeixin sobre el fons */
.stApp h1,
.stApp h2,
.stApp h3,
.stApp h5,
.stApp p,
.stApp label,
.stApp li,
.stApp a {
    color: #FFFFFF !important;
    text-shadow: 0 1px 4px rgba(0, 0, 0, 0.8);
}


/* Botons amb fons ple */
.stButton button,
.stLinkButton a {
    background-color: #1DB954 !important;   /* verd Spotify */
    color: #000000 !important;
    border: none !important;
    border-radius: 24px !important;
    font-weight: 600 !important;
    text-shadow: none !important;
}


.stButton button p,
.stLinkButton a p {
    color: #000000 !important;
    text-shadow: none !important;
}


.stButton button:hover,
.stLinkButton a:hover {
    background-color: #1ED760 !important;
    color: #000000 !important;
}


/* Botó desactivat (Finalitzar abans de 20 cançons) */
.stButton button:disabled {
    background-color: #535353 !important;
    opacity: 0.8 !important;
}
.stButton button:disabled p {
    color: #B3B3B3 !important;
}


/* Barra de puntuar: targeta amb el color de l'embed de Spotify */
.stSlider {
    background-color: #282828;
    padding: 1rem 1.5rem 1.5rem 1.5rem;
    border-radius: 12px;
}


/* Camp de text */
.stTextInput input {
    color: #FFFFFF !important;
    background-color: rgba(0, 0, 0, 0.45) !important;
}


</style>
""", unsafe_allow_html=True)




# Aplicar el fondo
posar_fons(ruta_fons)


# Inicializar el estado de la aplicación
if "pantalla" not in st.session_state:
    st.session_state.pantalla = "inici"


st.title("Recomanador de cançons amb Machine Learning​")
st.markdown("<h3 style='text-align:center;'>Descobreix el teu gust musical en minuts i valora la teva experiència</h3>", unsafe_allow_html=True)

# PANTALLA 1: INICIO
if st.session_state.pantalla == "inici":


    # Centrar el botó
    col1, col2, col3 = st.columns([1, 2, 1])


    with col2:
        st.write("")
        st.write("")


        with st.expander("Com funciona?"):
            st.write(" 1. El programa et mostrarà una cançó aleatòria.")
            st.write(" 2. Puntua la cançó.")
            st.write(" 3. Descobreix noves cançons al teu gust!")
            st.write(" 4. Fes un formulari de 2min per dir-nos com t'ha anat.")
            st.write("")  
        # Espai per centrar el botó
        st.markdown(
            "<h5 style='text-align:center;'>Durada aprox. 10 minuts</h5>",
            unsafe_allow_html=True
        )


        if st.button("Començar", use_container_width=True):
            st.session_state.pantalla = "crear o accedir a l'usuari"
            st.rerun()








# PANTALLA 2: REGISTRAR-SE
elif st.session_state.pantalla == "crear o accedir a l'usuari":


    st.write("")
    st.write("")
   
    nom_usuari = st.text_input("Introdueix el teu nom: (Aquesta dada no es guarda)")


    if st.button("Començar"):
        if nom_usuari.strip() == "":
            st.error("Ha ha, molt graciós. Ara que tothom s'ha rigut, introdueix un nom d'usuari.", icon="🤨")
        else:
            #Agafa el nom d'usuari i crea un perfil
            st.session_state.nombre = nom_usuari.strip()
            st.session_state.perfil = new_profile()
            st.session_state.genre_preferences = new_genre_preferences()


            #Creem un nou diccionari de cançons vistes = 0
            st.session_state.vistes = set()
            st.session_state.num_songs = 0


            st.session_state.canco_actual = give_song(
                st.session_state.perfil,
                st.session_state.vistes,
                st.session_state.genre_preferences
            )


            # Marquem la cançó com a vista immediatament
            if st.session_state.canco_actual is not None:
                st.session_state.vistes.add(
                    st.session_state.canco_actual
                )


            st.session_state.pantalla = "Puntua"
            st.rerun()




# PANTALLA 3: PUNTUAR
elif st.session_state.pantalla == "Puntua":
    idx = st.session_state.canco_actual


    st.write(f"Benvingut/da, {st.session_state.nombre} 👋")
    st.caption(f"Cançons valorades: {st.session_state.num_songs}")


    #Crea un iframe amb la can
    components.iframe(get_embed_link(idx), height=152)


    with st.expander("No es reprodueix?"):
        st.write("Per si de cas, asegura't de prémer el botó del triangle.")
        st.write("Si encara no surt res, aquest és l'enllaç de la cançó mostrada (Spotify):", get_spotify_link(idx))
        st.write("Si el problema persisteix, si us plau, refresca pàgina.")


    rating = st.slider("Puntua la cançó:", 1, 5, 3, key=f"rating_{idx}")


    if st.button("Enviar valoració"):
        st.session_state.perfil = puntua(
            st.session_state.perfil,
            rating,
            idx,
            st.session_state.genre_preferences
        )


        st.session_state.num_songs += 1


        # Busquem una cançó que encara no s'hagi mostrat
        st.session_state.canco_actual = give_song(
            st.session_state.perfil,
            st.session_state.vistes,
            st.session_state.genre_preferences
        )


        # La marquem com a vista immediatament
        if st.session_state.canco_actual is not None:
            st.session_state.vistes.add(
                st.session_state.canco_actual
            )


        else:
            st.session_state.pantalla = "finalitzar"


        st.rerun()


    if st.button("Finalitzar", disabled=(st.session_state.num_songs < 20)):
        st.session_state.pantalla = "finalitzar"
        st.rerun()


# PANTALLA 4: IMPRIMIR LES DADES I FORMULARI


elif st.session_state.pantalla =="finalitzar":
    st.title("Gràcies per la teva col·laboració!")
   
    with st.expander("Veure les teves dades"):
        st.dataframe(print_data(st.session_state.perfil), use_container_width=True)


    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
            st.link_button("​El nostre formulari​", "https://forms.gle/h35tvjKxsFXRteHz9")
   


