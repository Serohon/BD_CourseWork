import streamlit as st
class DatabaseError(Exception):
    """Ошибка при выполнении операций с базой данных."""
    def __init__(self, message="Произошла ошибка базы данных"):
        self.message = message
        super().__init__(self.message)


class AuthenticationError(Exception):
    """Ошибка аутентификации пользователя."""
    def __init__(self, message="Неверное имя пользователя или пароль"):
        self.message = message
        super().__init__(self.message)


class AuthorizationError(Exception):
    """Ошибка авторизации пользователя."""
    def __init__(self, message="У вас нет прав для выполнения этой операции"):
        self.message = message
        super().__init__(self.message)


class InvalidPasswordError(Exception):
    """Ошибка авторизации пользователя."""
    def __init__(self, message="У вас нет прав для выполнения этой операции"):
        self.message = message
        super().__init__(self.message)


class ValidationError(Exception):
    """Ошибка валидации данных."""
    def __init__(self, message="Переданы некорректные данные"):
        self.message = message
        super().__init__(self.message)


class UserNotFoundError(Exception):
    """Ошибка, указывающая на то, что ресурс не найден."""
    def __init__(self, message="Запрошенный ресурс не найден"):
        self.message = message
        super().__init__(self.message)

def handle_error_with_st(error):
    """Обрабатывает ошибки и выводит их через st.error."""
    if isinstance(error, DatabaseError):
        st.error(error.message)
    elif isinstance(error, AuthenticationError):
        st.error(error.message)
    elif isinstance(error, AuthorizationError):
        st.error(error.message)
    elif isinstance(error, ValidationError):
        st.error(error.message)
    elif isinstance(error, UserNotFoundError):
        st.error(error.message)
    else:
        st.error("Произошла неизвестная ошибка")