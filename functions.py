#FUNCIONS PER LA WEB
import sys
import subprocess
import importlib.util

REQUIRED_LIBRARIES = {
    "numpy": "numpy",
    "pandas": "pandas",
    "sklearn": "scikit-learn",
    "streamlit": "streamlit",
}

# ESTE CODIGO NO ES NUESTRO, HAY QUE PONER ESO EN EL INFORME
def install_libraries():
    for module, package in REQUIRED_LIBRARIES.items():
        if importlib.util.find_spec(module) is None:
            print(f"[Auto-Install] '{module}' no trobat. Instal·lant...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"[OK] '{package}' instal·lat correctament.")
            except subprocess.CalledProcessError:
                raise RuntimeError(f"No s'ha pogut instal·lar '{package}'.")

install_libraries() 

import os
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors

def initialize():
    global df, df_norm, features, nbrs


    carpeta = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(carpeta, 'dataset.csv'))


    # Generes musicals que volem recomanar
    allowed_genres = [
        'spanish',
        'reggaeton'
    ]


    df = df[df['track_genre'].isin(allowed_genres)].copy()

    #Eliminem aquells que tenen alguna dada nula
    df = df.dropna(subset=['track_name', 'artists', 'track_id'])

    # Filtrem cançons poc populars
    df = df[df['popularity'] >= 60].copy()


    # Eliminem duplicats
    df['track_name'] = df['track_name'].str.strip().str.lower()
    df['artists'] = df['artists'].str.strip().str.lower()


    df = df.drop_duplicates(
        subset=['track_name', 'artists']
    ).reset_index(drop=True)


    # Característiques musicals
    features = [
        'danceability',
        'energy',
        'speechiness',
        'acousticness',
        'instrumentalness',
        'liveness',
        'valence'
    ]


    # Normalitzem les dades
    df_norm = df.copy()


    for col in features:
        min_val = df[col].min()
        max_val = df[col].max()


        if max_val != min_val:
            df_norm[col] = (df[col] - min_val) / (max_val - min_val)
        else:
            df_norm[col] = 0.0


    # Creem el model KNN
    nbrs = NearestNeighbors(
        n_neighbors=min(10, len(df)),
        algorithm='auto',
        metric='euclidean'
    ).fit(df_norm[features].values)


    print(df['track_genre'].value_counts())
    print(df.columns.tolist())
    print(df['track_genre'].value_counts().head(30))




def new_profile():
    return df_norm[features].sample(1).values[0].tolist()




def give_song(profile, viewed, genre_preferences):


    if len(viewed) >= len(df):
        return None


    distances, indices = nbrs.kneighbors(
        np.array(profile).reshape(1, -1),
        n_neighbors=len(df)
    )


    candidates = [
        int(idx)
        for idx in indices[0]
        if int(idx) not in viewed
    ]


    if not candidates:
        return None


    # Penalitzem els gèneres que no agraden
    scored_candidates = []


    for idx in candidates:
        genre = df.loc[idx, 'track_genre']


        distance = distances[0][
            np.where(indices[0] == idx)[0][0]
        ]


        preference = genre_preferences.get(genre, 0.5)


        score = distance / np.sqrt(len(features)) + (1 - preference) * 0.15


        scored_candidates.append((idx, score))


    # Ordenem les cançons segons la puntuació final
    scored_candidates.sort(key=lambda x: x[1])


    top_candidates = scored_candidates[:10]


    selected = np.random.choice(
        [idx for idx, score in top_candidates]
    )


    return int(selected)




def new_genre_preferences():
    return {
        'spanish': 0.5,
        'reggaeton': 0.5
    }




def puntua(profile, rating, song_idx, genre_preferences):


    song_vector = df_norm.loc[song_idx, features].values
    user_vector = np.array(profile)


    # Actualitzem el perfil musical
    lr = 0.4
    weight = (rating - 3) / 2


    user_vector = user_vector + lr * weight * (
        song_vector - user_vector
    )


    # Actualitzem la preferència pel gènere
    genre = df.loc[song_idx, 'track_genre']


    genre_preferences[genre] += 0.10 * weight


    genre_preferences[genre] = np.clip(
        genre_preferences[genre], 0, 1
    )


    return np.clip(user_vector, 0, 1).tolist()




def print_data(profile):
    #Agafem les 10 cançons més properes
    distances, indices = nbrs.kneighbors(np.array(profile).reshape(1, -1), n_neighbors=10)
    files = []
    for i, idx in enumerate(indices[0]):
        files.append({
            "Cançó": df.loc[idx, 'track_name'],
            "Artista": df.loc[idx, 'artists'],
            "Gènere": df.loc[idx, 'track_genre'],
            "Similitud": f"{1 - distances[0][i] / np.sqrt(len(features)):.2%}",
        })
    return pd.DataFrame(files)


def get_spotify_link(idx):
    return f"https://open.spotify.com/intl-es/track/{df.loc[idx, 'track_id']}"


def get_embed_link(idx):
    return f"https://open.spotify.com/embed/track/{df.loc[idx, 'track_id']}"

