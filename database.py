# database.py

import sqlite3

conn = sqlite3.connect("hemanth_ai.db", check_same_thread=False)
cursor = conn.cursor()

# ---------- TABLES ---------- #

# Users
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

# Sessions
cursor.execute("""
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT DEFAULT 'New Chat',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Messages
cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    role TEXT,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()


# ---------- USERS ---------- #

def create_user(username, password):
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        return True
    except:
        return False


def login_user(username, password):
    cursor.execute(
        """
        SELECT id FROM users
        WHERE username=? AND password=?
        """,
        (username, password)
    )

    user = cursor.fetchone()

    if user:
        return user[0]

    return None


# ---------- SESSIONS ---------- #

def create_session(user_id, name="New Chat"):
    cursor.execute(
        """
        INSERT INTO sessions (user_id, name)
        VALUES (?, ?)
        """,
        (user_id, name)
    )
    conn.commit()
    return cursor.lastrowid


def get_sessions(user_id):
    cursor.execute(
        """
        SELECT id, name
        FROM sessions
        WHERE user_id=?
        ORDER BY id DESC
        """,
        (user_id,)
    )
    return cursor.fetchall()


def delete_session(session_id):
    cursor.execute(
        "DELETE FROM messages WHERE session_id=?",
        (session_id,)
    )

    cursor.execute(
        "DELETE FROM sessions WHERE id=?",
        (session_id,)
    )

    conn.commit()


# ---------- MESSAGES ---------- #

def save_message(session_id, role, message):
    cursor.execute(
        """
        INSERT INTO messages (session_id, role, message)
        VALUES (?, ?, ?)
        """,
        (session_id, role, message)
    )
    conn.commit()


def get_messages(session_id):
    cursor.execute(
        """
        SELECT role, message
        FROM messages
        WHERE session_id=?
        ORDER BY id ASC
        """,
        (session_id,)
    )
    return cursor.fetchall()


# ---------- ANALYTICS ---------- #

def get_stats():
    cursor.execute("SELECT COUNT(*) FROM users")
    users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM sessions")
    sessions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM messages")
    messages = cursor.fetchone()[0]

    return {
        "users": users,
        "sessions": sessions,
        "messages": messages
    }


# ---------- ADMIN ---------- #

def clear_all():
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM sessions")
    cursor.execute("DELETE FROM messages")
    conn.commit()