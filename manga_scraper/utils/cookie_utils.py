import os
import sqlite3


def get_vivaldi_cookies(domain: str, user_data_path=None) -> dict:
    if user_data_path is None:
        user_data_path = os.path.expanduser(
            "~/Library/Application Support/Vivaldi/Default"
        )
    cookies_db_path = os.path.join(user_data_path, "Cookies")

    conn = sqlite3.connect(cookies_db_path)
    cursor = conn.cursor()
    sql = "SELECT name, value FROM cookies WHERE host_key LIKE ?"
    cursor.execute(sql, ("%" + domain,))
    cookies = {name: value for name, value in cursor.fetchall()}
    cursor.close()
    conn.close()
    return cookies
