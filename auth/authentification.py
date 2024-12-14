import psycopg2
from utils.hashing import hash_password, verify_password
from database.db_connection import get_db_connection
import streamlit as st
# Аутентификация пользователя
def authentificate_user(username, password):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
               SELECT user_id, password_hash, role_id, company_id
                FROM users WHERE username=%s;
                """,
                (username,),
            )
            user = cur.fetchone()
            if not user:
                st.error("Пользователь не найден.")
                return None, None, None
            user_id, password_hash, role_id, company_id = user
            cur.execute("SELECT role_name from role_codes WHERE role_id=%s", (role_id,))
            role_name = cur.fetchone()
            role_name = role_name[0]
            if not verify_password(password_hash, password):
                st.error("Неверный пароль.")
                return None, None, None
            return user_id, role_name, company_id

def register_user(username, password, role, company_id=None):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT role_id from role_codes WHERE role_name=%s", (role,))
            role_id = cur.fetchone()
            role_id = role_id[0]
            check_query = "SELECT COUNT(*) FROM users WHERE username = %s"
            cur.execute(check_query, (username,))
            if cur.fetchone()[0] > 0:
                return False

            hashed_password = hash_password(password)
            insert_query = """
                    CALL create_user(%s, %s, %s, %s)
                """
            cur.execute(insert_query, (username, hashed_password, role_id, company_id))
            conn.commit()
            return True

def validate_role_code(role, provided_code):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            query = "SELECT code FROM role_codes WHERE role_name = %s"
            cur.execute(query, (role,))
            result = cur.fetchone()
            return result and result[0] == provided_code