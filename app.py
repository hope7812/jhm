import streamlit as st

from database import (
    init_db,
    get_playlists,
    create_playlist,
    delete_playlist,
    get_songs,
    add_song,
    delete_song
)

from api import search_music, recommend_music


# ---------------------------------
# 1. 기본 설정
# ---------------------------------

st.set_page_config(
    page_title="My Playlist",
    page_icon="🎵",
    layout="wide"
)

init_db()

st.title("🎵 My Playlist")
st.caption("나만의 음악을 검색하고 플레이리스트를 관리해 보세요.")


# ---------------------------------
# 2. 공통 함수
# ---------------------------------

def get_playlist_options():
    """플레이리스트 목록을 가져온다."""
    return get_playlists()


def add_music(playlist_id, music):
    """선택한 노래를 플레이리스트에 저장한다."""

    title = music.get("name", music.get("title", ""))
    artist = music.get("artist", "")

    if isinstance(artist, dict):
        artist = artist.get("name", "")

    if not title or not artist:
        st.error("노래 정보가 올바르지 않습니다.")
        return

    music_url = music.get("url", "")

    try:
        add_song(
            playlist_id,
            title,
            artist,
            music_url
        )
        st.info(f"'{title}'을(를) 플레이리스트에 추가했습니다.")
        st.rerun()

    except Exception as e:
        st.error(f"노래 저장 중 오류가 발생했습니다: {e}")


def parse_search_results(data):
    """Last.fm 노래 검색 결과를 정리한다."""

    tracks = data.get("results", {}).get(
        "trackmatches", {}
    ).get("track", [])

    if isinstance(tracks, dict):
        tracks = [tracks]

    return tracks


def parse_recommend_results(data):
    """Last.fm 유사곡 추천 결과를 정리한다."""

    tracks = data.get("similartracks", {}).get(
        "track", []
    )

    if isinstance(tracks, dict):
        tracks = [tracks]

    return tracks


# ---------------------------------
# 3. 사이드바 메뉴
# ---------------------------------

menu = st.sidebar.radio(
    "메뉴",
    [
        "🏠 홈",
        "🔍 음악 검색",
        "✨ 음악 추천",
        "📚 플레이리스트 관리"
    ]
)


# =================================
# 4. 홈 화면
# =================================

if menu == "🏠 홈":

    st.header("내 플레이리스트")

    playlists = get_playlist_options()

    if not playlists:
        st.info("아직 플레이리스트가 없습니다. 새로운 플레이리스트를 만들어 보세요.")

    else:
        for playlist in playlists:

            with st.expander(
                f"🎧 {playlist['name']}"
            ):

                st.write(
                    playlist.get("description", "")
                )

                songs = get_songs(playlist["id"])

                if songs:
                    for song in songs:
                        st.write(
                            f"🎵 {song['title']} - {song['artist']}"
                        )
                else:
                    st.write("저장된 노래가 없습니다.")


# =================================
# 5. 음악 검색 화면
# =================================

elif menu == "🔍 음악 검색":

    st.header("음악 검색")

    keyword = st.text_input(
        "검색할 노래 제목 또는 가수를 입력하세요.",
        placeholder="예: Yellow, Coldplay"
    )

    if st.button("노래 검색"):

        if not keyword.strip():
            st.warning("검색어를 입력해 주세요.")

        else:
            try:
                with st.spinner("음악을 검색하고 있습니다..."):
                    data = search_music(keyword.strip())

                st.session_state.search_results = (
                    parse_search_results(data)
                )

            except Exception as e:
                st.error(f"음악 검색에 실패했습니다: {e}")

    results = st.session_state.get(
        "search_results", []
    )

    if results:

        st.subheader("검색 결과")

        playlists = get_playlist_options()

        if not playlists:
            st.warning("먼저 플레이리스트를 만들어 주세요.")

        else:
            playlist_names = {
                p["name"]: p["id"] for p in playlists
            }

            for index, music in enumerate(results):

                title = music.get("name", "제목 없음")
                artist = music.get("artist", "가수 정보 없음")
                url = music.get("url", "")

                with st.container(border=True):

                    st.write(f"**{title}**")
                    st.write(f"가수: {artist}")

                    if url:
                        st.markdown(
                            f"[Last.fm에서 음악 정보 보기]({url})"
                        )

                    selected_playlist = st.selectbox(
                        "저장할 플레이리스트",
                        list(playlist_names.keys()),
                        key=f"search_playlist_{index}"
                    )

                    if st.button(
                        "➕ 플레이리스트에 추가",
                        key=f"add_search_{index}"
                    ):
                        add_music(
                            playlist_names[selected_playlist],
                            music
                        )

    elif "search_results" in st.session_state:
        st.info("검색 결과가 없습니다.")


# =================================
# 6. 음악 추천 화면
# =================================

elif menu == "✨ 음악 추천":

    st.header("음악 추천")

    st.write(
        "좋아하는 노래를 기준으로 비슷한 음악을 추천받을 수 있습니다."
    )

    artist = st.text_input(
        "가수 이름",
        placeholder="예: Coldplay"
    )

    title = st.text_input(
        "노래 제목",
        placeholder="예: Yellow"
    )

    if st.button("✨ 비슷한 노래 추천받기"):

        if not artist.strip() or not title.strip():
            st.warning("가수 이름과 노래 제목을 모두 입력해 주세요.")

        else:
            try:
                with st.spinner("비슷한 음악을 찾고 있습니다..."):

                    data = recommend_music(
                        artist.strip(),
                        title.strip()
                    )

                    st.session_state.recommend_results = (
                        parse_recommend_results(data)
                    )

            except Exception as e:
                st.error(f"음악 추천에 실패했습니다: {e}")

    results = st.session_state.get(
        "recommend_results", []
    )

    if results:

        st.subheader("추천 음악 목록")

        playlists = get_playlist_options()

        if not playlists:
            st.warning("먼저 플레이리스트를 만들어 주세요.")

        else:
            playlist_names = {
                p["name"]: p["id"] for p in playlists
            }

            for index, music in enumerate(results):

                title = music.get("name", "제목 없음")

                artist_info = music.get("artist", "")
                if isinstance(artist_info, dict):
                    artist = artist_info.get("name", "")
                else:
                    artist = artist_info

                url = music.get("url", "")

                with st.container(border=True):

                    st.write(f"**{title}**")
                    st.write(f"가수: {artist}")

                    if url:
                        st.markdown(
                            f"[Last.fm에서 음악 정보 보기]({url})"
                        )

                    selected_playlist = st.selectbox(
                        "저장할 플레이리스트",
                        list(playlist_names.keys()),
                        key=f"recommend_playlist_{index}"
                    )

                    if st.button(
                        "➕ 플레이리스트에 추가",
                        key=f"add_recommend_{index}"
                    ):

                        add_music(
                            playlist_names[selected_playlist],
                            music
                        )

    elif "recommend_results" in st.session_state:
        st.info("추천할 음악이 없습니다. 다른 노래를 입력해 보세요.")


# =================================
# 7. 플레이리스트 관리 화면
# =================================

elif menu == "📚 플레이리스트 관리":

    st.header("플레이리스트 관리")

    # 플레이리스트 생성
    st.subheader("새 플레이리스트 만들기")

    with st.form("create_playlist_form"):

        playlist_name = st.text_input(
            "플레이리스트 이름",
            placeholder="예: 공부할 때 듣는 노래"
        )

        description = st.text_area(
            "플레이리스트 설명",
            placeholder="플레이리스트에 대한 설명을 입력하세요."
        )

        submitted = st.form_submit_button(
            "플레이리스트 생성"
        )

        if submitted:

            if not playlist_name.strip():
                st.warning("플레이리스트 이름을 입력해 주세요.")

            else:
                try:
                    create_playlist(
                        playlist_name.strip(),
                        description.strip()
                    )

                    st.success("플레이리스트가 생성되었습니다.")
                    st.rerun()

                except Exception as e:
                    st.error(f"생성 중 오류가 발생했습니다: {e}")

    st.divider()

    # 기존 플레이리스트 관리
    st.subheader("내 플레이리스트")

    playlists = get_playlist_options()

    if not playlists:
        st.info("등록된 플레이리스트가 없습니다.")

    else:

        for playlist in playlists:

            with st.container(border=True):

                st.write(f"### 🎧 {playlist['name']}")

                st.write(
                    playlist.get("description", "")
                )

                songs = get_songs(playlist["id"])

                st.write(f"저장된 노래: {len(songs)}곡")

                for song in songs:

                    col1, col2 = st.columns([4, 1])

                    with col1:
                        st.write(
                            f"🎵 {song['title']} - {song['artist']}"
                        )

                    with col2:

                        if st.button(
                            "삭제",
                            key=f"delete_song_{song['id']}"
                        ):

                            delete_song(song["id"])
                            st.rerun()

                if st.button(
                    "플레이리스트 삭제",
                    key=f"delete_playlist_{playlist['id']}"
                ):

                    delete_playlist(playlist["id"])
                    st.rerun()


# ---------------------------------
# 8. 하단 안내
# ---------------------------------

st.sidebar.divider()

st.sidebar.caption(
    "My Playlist | Python + Streamlit + SQLite + Last.fm API"
)