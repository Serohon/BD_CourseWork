from database.db_connection import get_db_connection
import pandas as pd

# Получение всех пользователей
def get_all_users():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            SELECT user_id, username, role_name, company_id 
            FROM users 
            LEFT JOIN role_codes using(role_id)
            """)
            users = cur.fetchall()
            return [{"user_id": user[0], "username": user[1], "role": user[2], "company_id": user[3]} for user in users]

def get_all_companies():
    with get_db_connection() as conn:
        query = """
            SELECT c.company_id, c.company_name
            FROM companies c
            LEFT JOIN users u ON c.company_id = u.company_id
            LEFT JOIN role_codes r ON u.role_id = r.role_id
        WHERE r.role_name = 'Редактор' IS NULL"""
        df = pd.read_sql(query, conn)
        return df

def fetch_orders_for_company(company_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            query = """
            SELECT order_id, service_name, status_name FROM orders
            JOIN workers using(worker_id)
            JOIN statuses using(status_id)
            JOIN services using(service_id)
            WHERE company_id = %s
            """
            cur.execute(query, (company_id,))
            orders = cur.fetchall()
            return [{"order_id": order[0], "service_name": order[1], "status_name": order[2]} for order in orders]

def update_order_status(order_id, status_name):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            query_1 = "SELECT status_id FROM statuses WHERE status_name=%s"
            cur.execute(query_1, (status_name,))
            status_id = cur.fetchone()
            print(order_id, status_id[0])
            query = "CALL update_order_status(%s, %s)"
            cur.execute(query, (order_id, status_id[0]))
            conn.commit()

def get_all_services():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT service_id, service_name FROM services")
            services = cur.fetchall()
            return [{"service_id": service[0], "service_name": service[1]} for service in services]


# Добавить компанию
def add_company(name, description):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            check_query = "SELECT COUNT(*) FROM companies WHERE company_name = %s"
            cur.execute(check_query, (name,))
            if cur.fetchone()[0] > 0:
                conn.close()
                return False
            query = "CALL add_company(%s, %s)"
            cur.execute(query, (name, description))
            conn.commit()
            return True

def get_all_orders():
    with get_db_connection() as conn:
        conn = get_db_connection()
        query = "SELECT * FROM orders"
        df = pd.read_sql(query, conn)
        return df

def add_worker(company_id, first_name, last_name, position, phone_number, age):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            check_query = "SELECT COUNT(*) FROM workers WHERE first_name = %s and last_name = %s and phone_number = %s"
            cur.execute(check_query, (first_name,last_name, phone_number))
            if cur.fetchone()[0] > 0:
                conn.close()
                return False
            pos_query = "SELECT service_id FROM services WHERE service_name=%s"
            cur.execute(pos_query, (position,))
            position_id = cur.fetchone()
            query = f"CALL add_worker(%s, %s, %s, %s, %s, %s)"
            cur.execute(query, (company_id, first_name, last_name, position_id[0], phone_number, age))
            conn.commit()
            return True

# Добавить услугу
def add_service(service_name, description, price):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            check_query = "SELECT COUNT(*) FROM services WHERE service_name = %s"
            cur.execute(check_query, (service_name,))
            if cur.fetchone()[0] > 0:
                conn.close()
                return False
            query = "CALL add_service(%s, %s, %s)"
            cur.execute(query, (service_name, price, description))
            conn.commit()
            return True

# Получить заказы пользователя
def get_user_orders(username):
    with get_db_connection() as conn:
        query = f"""
            SELECT
            o.order_id,
            s.service_name,
            w.worker_id,
            CONCAT(w.first_name, ' ', w.last_name) AS worker_name,
            st.status_name,
            r.review_id
        FROM orders o
        LEFT JOIN workers w ON o.worker_id = w.worker_id
        LEFT JOIN services s ON w.service_id = s.service_id
        LEFT JOIN reviews r ON r.order_id = o.order_id
        LEFT JOIN statuses st ON o.status_id = st.status_id
        WHERE o.user_id = (SELECT user_id FROM users WHERE username like '{username}')
        """
        df = pd.read_sql(query, conn)
        return df

def assign_editor_to_company(username, company_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT role_id from role_codes WHERE role_name=%s", ("Редактор",))
            role_id = cur.fetchone()
            role_id = role_id[0]
            cur.execute("SELECT user_id FROM users WHERE username = %s AND role_id = %s", (username, role_id))
            editor = cur.fetchone()
            if not editor:
                conn.close()
                return False
            editor_id = editor[0]
            cur.execute("UPDATE users SET company_id = %s WHERE user_id = %s", (int(company_id), editor_id))
            conn.commit()
            return True

def get_services():
    with get_db_connection() as conn:
        query = "SELECT s.service_id, s.service_name, s.description FROM services as s"
        df = pd.read_sql(query, conn)
        conn.close()
        return df

def get_workers(service_id):
    with get_db_connection() as conn:
        query = f"""
        SELECT
            w.worker_id,
            CONCAT(w.first_name, ' ', w.last_name) AS full_name,
            c.company_name,
            w.age,
            COALESCE(AVG(r.rating), 0) AS avg_rating
        FROM workers w
        LEFT JOIN companies c ON w.company_id = c.company_id
        LEFT JOIN orders o using (worker_id)
        LEFT JOIN reviews r ON o.order_id = r.order_id
        WHERE w.service_id = {service_id} and w.in_work = False
        GROUP BY w.worker_id, c.company_name, w.age
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df

def create_order(username, worker_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            query_1 = "SELECT user_id FROM users WHERE username=%s"
            cur.execute(query_1, (username,))
            user_id = cur.fetchone()
            cur.execute("CALL create_order(%s, %s);", (user_id[0], int(worker_id)))
            conn.commit()
            conn.close()

def create_review(rating, review_text, order_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL create_review(%s, %s, %s);", (rating, review_text, order_id))
            conn.commit()

def get_company_profit(company_id):
    with get_db_connection() as conn:
        query = f"SELECT * from editor_company_profit_view WHERE company_name = (SELECT company_name from companies WHERE company_id={company_id})"
        df = pd.read_sql(query, conn)
        return df

def get_service_profit(service_id):
    with get_db_connection() as conn:
        query = f"SELECT * from service_order_count WHERE service_name = (SELECT service_name from services WHERE service_id={service_id})"
        df = pd.read_sql(query, conn)
        return df

def get_rating(review_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            query = f"SELECT rating from reviews where review_id={review_id}"
            cur.execute(query)
            rate = cur.fetchone()[0]
            return rate