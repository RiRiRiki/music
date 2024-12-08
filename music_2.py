import streamlit as st
import requests

# Spotify APIクライアント情報
CLIENT_ID = "c1c46cd5a01c41148f9cd2f016693956"  # Spotify Developer Dashboardで取得
CLIENT_SECRET = "b5189dc035074d33b88b1ed2bd92adcd"  # Spotify Developer Dashboardで取得
REDIRECT_URI = "http://localhost:8505"  # "/callback"は不要

# Spotifyの認証URLを生成
AUTH_URL = (
    f"https://accounts.spotify.com/authorize?client_id={CLIENT_ID}"
    f"&response_type=code&redirect_uri={REDIRECT_URI}"
    f"&scope=user-top-read"
)

# アクセストークンを取得する関数
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

# トップアーティストを取得する関数
def get_top_artists(access_token):
    url = "https://api.spotify.com/v1/me/top/artists"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["items"]
    else:
        st.error("トップアーティスト取得に失敗しました")
        return []

# Streamlitアプリのメイン処理
st.title("Spotify 音楽推薦アプリ")

# ステップ1: Spotifyログインボタンを表示
if "access_token" not in st.session_state:
    st.markdown(f"[Spotifyでログインする]({AUTH_URL})")

    # リダイレクトされた後のクエリパラメータを取得
    auth_code = st.experimental_get_query_params().get("code")
    if auth_code:
        auth_code = auth_code[0]  # クエリパラメータからコードを取得
        st.session_state["access_token"] = get_access_token(auth_code)

# ステップ2: トップアーティストの表示
if "access_token" in st.session_state:
    access_token = st.session_state["access_token"]
    top_artists = get_top_artists(access_token)

    if top_artists:
        st.subheader("あなたのトップアーティスト:")
        for artist in top_artists:
            st.write(f"- {artist['name']} ({', '.join(artist['genres'])})")
