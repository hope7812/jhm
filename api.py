
import requests
import streamlit as st

# Last.fm API 기본 주소
BASE_URL = "https://ws.audioscrobbler.com/2.0/"


# API Key 가져오기
def get_api_key():
    try:
        api_key = st.secrets["LASTFM_API_KEY"]
    except Exception:
        api_key = ""

    if not api_key:
        raise ValueError(
            "Last.fm API Key가 설정되지 않았습니다. "
            ".streamlit/secrets.toml 파일을 확인하세요."
        )

    return api_key


# Last.fm API에 요청 보내기
def request_lastfm(params):
    params["api_key"] = get_api_key()
    params["format"] = "json"

    try:
        response = requests.get(
            BASE_URL,
            params=params,
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        # Last.fm에서 오류를 반환했는지 확인
        if "error" in data:
            raise ValueError(data.get("message", "Last.fm API 오류"))

        return data

    except requests.exceptions.Timeout:
        raise Exception("API 응답 시간이 초과되었습니다.")

    except requests.exceptions.RequestException:
        raise Exception("인터넷 연결 또는 API 요청에 문제가 발생했습니다.")


# 음악 검색
def search_music(keyword):
    if not keyword or not keyword.strip():
        raise ValueError("검색할 음악 제목을 입력하세요.")

    params = {
        "method": "track.search",
        "track": keyword.strip(),
        "limit": 10
    }

    return request_lastfm(params)


# 유사 음악 추천
def recommend_music(artist, title):
    if not artist or not artist.strip():
        raise ValueError("가수 이름을 입력하세요.")

    if not title or not title.strip():
        raise ValueError("음악 제목을 입력하세요.")

    params = {
        "method": "track.getsimilar",
        "artist": artist.strip(),
        "track": title.strip(),
        "limit": 10
    }

    return request_lastfm(params)
