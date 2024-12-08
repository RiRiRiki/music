import streamlit as st
import requests
import random

CLIENT_ID = "c1c46cd5a01c41148f9cd2f016693956"
CLIENT_SECRET = "b5189dc035074d33b88b1ed2bd92adcd"
REDIRECT_URI = "http://localhost:8551"

AUTH_URL = (
    f"https://accounts.spotify.com/authorize?client_id={CLIENT_ID}"
    f"&response_type=code&redirect_uri={REDIRECT_URI}"
    f"&scope=user-top-read user-read-private"
)

def get_access_token(auth_code):
    url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        st.error(f"アクセストークン取得に失敗しました: {response.json()}")
        return None

def get_top_artists(access_token):
    url = "https://api.spotify.com/v1/me/top/artists"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["items"]
    else:
        st.error(f"トップアーティスト取得に失敗しました: {response.json()}")
        return []

def search_artists_by_genre(access_token, genre, limit=5):
    url = f"https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "q": f"genre:{genre}",
        "type": "artist",
        "limit": limit
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("artists", {}).get("items", [])
    else:
        return []

def recommend_artists_by_genre(top_artists, access_token):
    recommendations = {}
    for artist in top_artists:
        for genre in artist.get("genres", []):
            genre_artists = search_artists_by_genre(access_token, genre)
            if genre_artists:
                recommendations[genre] = genre_artists[:3]  # 各ジャンルから3名選択
    return recommendations

# Custom CSS for background and style
st.markdown(
    """
    <style>
    body {
        background-image: url("https://source.unsplash.com/1600x900/?music,concert");
        background-size: cover;
        background-attachment: fixed;
    }
    .stApp {
        background-color: rgba(0, 0, 0, 0.5);
        color: white;
        font-family: "Helvetica", sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Spotify ジャンル推薦アプリ")

if "access_token" not in st.session_state:
    st.markdown(f"[Spotifyでログインする]({AUTH_URL})")
    auth_code = st.experimental_get_query_params().get("code")
    if auth_code:
        auth_code = auth_code[0]
        st.session_state["access_token"] = get_access_token(auth_code)

if "access_token" in st.session_state:
    access_token = st.session_state["access_token"]
    top_artists = get_top_artists(access_token)

    if top_artists:
        st.subheader("あなたのトップアーティスト:")
        for artist in top_artists:
            st.write(f"- {artist['name']} ({', '.join(artist['genres'])})")

        st.subheader("ジャンルごとのおすすめアーティスト:")
        recommendations = recommend_artists_by_genre(top_artists, access_token)
        for genre, artists in recommendations.items():
            st.write(f"### {genre.title()}:")
            for artist in artists:
                st.write(
                    f"- {artist['name']} "
                    f"[Spotifyで見る](https://open.spotify.com/artist/{artist['id']})"
                )
    else:
        st.warning("トップアーティストが取得できませんでした。Spotifyで再度確認してください。")
