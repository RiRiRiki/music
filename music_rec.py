import streamlit as st
import requests
import time

CLIENT_ID = "c1c46cd5a01c41148f9cd2f016693956"
CLIENT_SECRET = "b5189dc035074d33b88b1ed2bd92adcd"
REDIRECT_URI = "https://is8mrxddrtrwkdufntuhal.streamlit.app/"

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
        st.error(f"ジャンルベースのアーティスト検索に失敗しました: {response.json()}")
        return []

def recommend_artists_by_genre(top_artists, access_token):
    known_artists = {artist["name"] for artist in top_artists}
    recommendations = []

    for artist in top_artists:
        st.info(f"{artist['name']} のジャンルで推薦アーティストを検索中...")
        for genre in artist.get("genres", []):
            st.info(f"Searching for artists in genre: {genre}")
            genre_artists = search_artists_by_genre(access_token, genre)
            for genre_artist in genre_artists:
                if genre_artist["name"] not in known_artists:
                    recommendations.append(genre_artist)

    # 人気度が低い順にソート（未知のアーティストを優先）
    recommendations = sorted(recommendations, key=lambda x: x.get("popularity", 0))
    return recommendations[:5]  # 上位5つを推薦

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

        st.subheader("ジャンルを基にしたおすすめアーティスト:")
        recommendations = recommend_artists_by_genre(top_artists, access_token)
        for artist in recommendations:
            st.write(
                f"- {artist['name']} ({', '.join(artist.get('genres', []))}) "
                f"[Spotifyで見る](https://open.spotify.com/artist/{artist['id']})"
            )
    else:
        st.warning("トップアーティストが取得できませんでした。Spotifyで再度確認してください。")
