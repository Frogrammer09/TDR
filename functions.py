#FUNCIONS PER LA WEB

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
        'valence',
        'tempo',
        'loudness'
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
    distances, indices = distances[0], indices[0]

    # Traiem les cançons ja vistes
    mask = ~np.isin(indices, list(viewed))
    indices, distances = indices[mask], distances[mask]
    if len(indices) == 0:
        return None

    generes_cand = df.loc[indices, 'track_genre'].values

    # Triem el gènere amb probabilitat proporcional a la preferència
    generes = [g for g in genre_preferences if g in set(generes_cand)]
    pesos = np.array([genre_preferences[g] for g in generes])
    pesos = np.clip(pesos, 0.05, 0.95)   # sempre queda una mica d'exploració
    genere = np.random.choice(generes, p=pesos / pesos.sum())

    # Dins del gènere, una de les 10 més properes
    sel = np.where(generes_cand == genere)[0][:10]
    return int(indices[np.random.choice(sel)])


def new_genre_preferences():
    return {
        'spanish': 0.5,
        'reggaeton': 0.5
    }




def puntua(profile, rating, song_idx, genre_preferences):


    song_vector = df_norm.loc[song_idx, features].values
    user_vector = np.array(profile)


    # Actualitzem el perfil musical
    weight = (rating - 3) / 2
    lr = 0.4 if weight > 0 else 0.15

    user_vector = user_vector + lr * weight * (
        song_vector - user_vector
    )

    # Actualitzem la preferència pel gènere
    genre = df.loc[song_idx, 'track_genre']
    step = 0.25

    genre_preferences[genre] = float(
        np.clip(genre_preferences[genre] + step * weight, 0, 1)
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

