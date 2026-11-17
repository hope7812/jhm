
import sqlite3
from pathlib import Path

# 데이터베이스 파일 경로
DB_PATH = Path(__file__).resolve().parent / "playlist.db"


# 데이터베이스 연결
def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# 데이터베이스 및 테이블 생성
def init_db():
    conn = connect_db()
    cursor = conn.cursor()

    # 플레이리스트 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        )
    """)

    # 음악 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            music_url TEXT
        )
    """)

    # 플레이리스트와 음악을 연결하는 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS playlist_songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            playlist_id INTEGER NOT NULL,
            song_id INTEGER NOT NULL,
            UNIQUE(playlist_id, song_id),
            FOREIGN KEY (playlist_id)
                REFERENCES playlists(id) ON DELETE CASCADE,
            FOREIGN KEY (song_id)
                REFERENCES songs(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


# 플레이리스트 목록 조회
def get_playlists():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM playlists ORDER BY id DESC")
    playlists = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return playlists


# 플레이리스트 생성
def create_playlist(name, description=""):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO playlists (name, description) VALUES (?, ?)",
        (name, description)
    )

    conn.commit()
    conn.close()


# 플레이리스트 삭제
def delete_playlist(playlist_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM playlists WHERE id = ?",
        (playlist_id,)
    )

    conn.commit()
    conn.close()


# 특정 플레이리스트의 음악 목록 조회
def get_songs(playlist_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT songs.*
        FROM songs
        JOIN playlist_songs
        ON songs.id = playlist_songs.song_id
        WHERE playlist_songs.playlist_id = ?
        ORDER BY songs.id DESC
    """, (playlist_id,))

    songs = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return songs


# 플레이리스트에 음악 추가
def add_song(playlist_id, title, artist, music_url=""):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # 기존에 같은 제목과 가수의 음악이 있는지 확인
        cursor.execute("""
            SELECT id FROM songs
            WHERE title = ? AND artist = ?
        """, (title, artist))

        song = cursor.fetchone()

        if song:
            song_id = song["id"]
        else:
            # 새로운 음악 저장
            cursor.execute("""
                INSERT INTO songs (title, artist, music_url)
                VALUES (?, ?, ?)
            """, (title, artist, music_url))

            song_id = cursor.lastrowid

        # 플레이리스트와 음악 연결
        cursor.execute("""
            INSERT INTO playlist_songs (playlist_id, song_id)
            VALUES (?, ?)
        """, (playlist_id, song_id))

        conn.commit()

    except sqlite3.IntegrityError:
        conn.rollback()
        raise ValueError("이미 플레이리스트에 추가된 음악이거나 잘못된 요청입니다.")

    finally:
        conn.close()


# 음악 삭제
def delete_song(song_id):
    conn = connect_db()
    cursor = conn.cursor()

    # 음악과 연결된 플레이리스트 정보 삭제
    cursor.execute(
        "DELETE FROM playlist_songs WHERE song_id = ?",
        (song_id,)
    )

    # 음악 자체 삭제
    cursor.execute(
        "DELETE FROM songs WHERE id = ?",
        (song_id,)
    )

    conn.commit()
    conn.close()
