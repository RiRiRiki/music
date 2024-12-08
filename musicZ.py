import streamlit as st
import requests
import time
import random

CLIENT_ID = "c1c46cd5a01c41148f9cd2f016693956"
CLIENT_SECRET = "b5189dc035074d33b88b1ed2bd92adcd"
REDIRECT_URI = "http://localhost:8543"

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

def get_related_artists(access_token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/related-artists"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        st.write(f"Related artists response for {artist_id}: {response.json()}")
        return response.json().get("artists", [])
    elif response.status_code == 404:  # Related artists not found
        st.warning(f"関連アーティストが見つかりませんでした (ID: {artist_id})")
        return []
    else:
        st.error(f"関連アーティストの取得に失敗しました: {response.json()}")
        return []

def recommend_new_artists(top_artists, access_token):
    known_artists = {artist["name"] for artist in top_artists}
    recommendations = []

    for artist in top_artists:
        st.info(f"Fetching related artists for {artist['name']}...")
        related_artists = get_related_artists(access_token, artist["id"])
        time.sleep(0.2)
        if not related_artists:  # 関連アーティストが見つからない場合
            st.warning(f"{artist['name']} の関連アーティストが見つかりませんでした")
            continue

        for related in related_artists:
            if related["name"] not in known_artists:
                recommendations.append(related)

    if not recommendations:  # 推薦が見つからない場合
        st.warning("関連アーティストが見つからなかったため、ランダムに推薦します。")
        recommendations = random.sample(top_artists, min(3, len(top_artists)))

    # 人気度が低い順にソート（未知のアーティストを優先）
    recommendations = sorted(recommendations, key=lambda x: x.get("popularity", 0))
    return recommendations[:3]

st.title("Spotify 音楽推薦アプリ")

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

        st.subheader("おすすめの新しいアーティスト:")
        recommendations = recommend_new_artists(top_artists, access_token)
        for artist in recommendations:
            st.write(
                f"- {artist['name']} ({', '.join(artist['genres'])}) "
                f"[Spotifyで見る](https://open.spotify.com/artist/{artist['id']})"
            )
    else:
        st.warning("トップアーティストが取得できませんでした。Spotifyで再度確認してください。")
