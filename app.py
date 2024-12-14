from auth.authentification import authentificate_user, register_user, validate_role_code
import streamlit as st
from views.admin_view import admin_dashboard
from views.editor_view import editor_dashboard
from views.user_view import user_dashboard

if 'authentificated' not in st.session_state:
    st.session_state['authentificated'] = False
if 'role' not in st.session_state:
    st.session_state['role'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'company_id' not in st.session_state:
    st.session_state['company_id'] = None
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = "login"  # По умолчанию показываем страницу входа
if 'action_triggered' not in st.session_state:
    st.session_state['action_triggered'] = False


def trigger_action():
    st.session_state['action_triggered'] = True

def logout():
    st.session_state['authentificated'] = False
    st.session_state['role'] = None
    st.session_state['username'] = None
    st.session_state['company_id'] = None
    st.session_state['current_page'] = "login"
    trigger_action()

def handle_login():
    username = st.session_state.get("login_username", "")
    password = st.session_state.get("login_password", "")
    if username == '':
        st.warning('Введите данные')
    if username and password == '':
        st.warning('Введите пароль')
    if username and password:
        user_id, role, company_id = authentificate_user(username, password)
        if role:
            st.session_state['authentificated'] = True
            st.session_state['role'] = role
            st.session_state['username'] = username
            st.session_state['company_id'] = company_id
            st.session_state['current_page'] = "main"
        else:
            pass

def login_page():
    st.markdown("<h2 style='text-align: center;'>Авторизация</h2>", unsafe_allow_html=True)
    cols = st.columns([3, 2, 3])  # Центрируем форму
    with cols[1]:
        st.text_input("Логин", key="login_username")
        st.text_input("Пароль", type="password", key="login_password")
        st.button("Войти", on_click=handle_login)

def handle_registration():
    username = st.session_state.get("register_username", "")
    password = st.session_state.get("register_password", "")
    confirm_password = st.session_state.get("register_confirm_password", "")
    role = st.session_state.get("register_role", "Пользователь")
    role_code = st.session_state.get("register_role_code", "")
    if username == '':
        st.warning('Введите логин')
    else:
        if username and password == '':
            st.warning('Введите пароль')
        else:
            if password != confirm_password:
                st.error("Пароли не совпадают!")
            elif role in ["Редактор", "Администратор"] and not validate_role_code(role, role_code):
                st.error("Неверный код для выбранной роли!")
            else:
                success = register_user(username, password, role)
                if success:
                    st.success("Регистрация прошла успешно! Теперь вы можете войти.")
                    st.session_state['current_page'] = "login"
                else:
                    st.error("Ошибка регистрации: пользователь с таким логином уже существует.")

def registration_page():
    st.markdown("<h2 style='text-align: center;'>Регистрация нового пользователя</h2>", unsafe_allow_html=True)
    cols = st.columns([3, 2, 3])  # Центрируем форму
    with cols[1]:
        st.text_input("Придумайте логин", key="register_username")
        st.text_input("Придумайте пароль", type="password", key="register_password")
        st.text_input("Повторите пароль", type="password", key="register_confirm_password")
        role = st.selectbox("Выберите роль", ["Пользователь", "Редактор", "Администратор"], key="register_role")
        if role in ["Редактор", "Администратор"]:
            st.text_input("Введите код для регистрации в этой роли", key="register_role_code")
        st.button("Зарегистрироваться", on_click=handle_registration)

def main_content():
    st.markdown(f"<h3 style='text-align: center;'>Добро пожаловать, {st.session_state['username']}!</h3>",
                unsafe_allow_html=True)
    if st.session_state['role'] == "Администратор":
        admin_dashboard()
    elif st.session_state['role'] == "Редактор":
        if st.session_state['company_id'] is None:
            st.warning('Вы не привязаны ни к одной компании')
        else:
            editor_dashboard(st.session_state['company_id'])
    else:
        user_dashboard(st.session_state['username'])

# Основное приложение
def main():
    st.set_page_config(page_title="Система авторизации", layout="centered")
    if st.session_state['authentificated']:
        st.sidebar.markdown(f"**Вы вошли как: {st.session_state['role']} {st.session_state['username']}**")
        if st.sidebar.button("Выйти", on_click=logout):
            pass
        main_content()
    else:
        if st.session_state['current_page'] == "login":
            login_page()
            if st.session_state['current_page'] != "registration":
                if st.button("Перейти к регистрации", on_click=lambda: st.session_state.update(
                        {'current_page': 'registration', 'action_triggered': True})):
                    pass
        elif st.session_state['current_page'] == "registration":
            registration_page()
            if st.session_state['current_page'] != "login":
                if st.button("Перейти к авторизации",
                             on_click=lambda: st.session_state.update(
                                 {'current_page': 'login', 'action_triggered': True})):
                    pass

if __name__ == "__main__":
    main()
