import streamlit as st
from database.queries import add_company, get_all_users, assign_editor_to_company, \
    add_service, get_all_companies, get_services, get_service_profit

def admin_dashboard():
    st.title("Панель администратора")

    menu = st.selectbox("Действия", ["Добавить услугу", "Привязать редактора к компании", "Добавить компанию", "Прибыль по услугам"])

    if menu == "Добавить компанию":
        st.subheader("Добавление компании")
        company_name = st.text_input("Название компании")
        description = st.text_area("Описание")
        if company_name == '' or description == '':
            st.warning('Введите название')
        elif company_name and description == '':
            st.warning('Введите описание')
        else:
            if st.button("Добавить компанию"):
                success = add_company(company_name, description)
                if success:
                    st.success("Компания добавлена")
                else:
                    st.error("Такая компания уже есть")

    if menu == "Привязать редактора к компании":
        users = get_all_users()
        st.subheader("Привязка редакторов")
        editor_choices = [user['username'] for user in users if user['role'] == 'Редактор' and user['company_id'] is None]
        if editor_choices:
            selected_editor = st.selectbox("Выберите редактора", editor_choices)
            companies = get_all_companies()
            if companies.empty:
                st.error("Добавьте компанию")
            else:
                company_name = st.selectbox(
                    "Выберите компанию",
                    companies["company_name"],
                    index=0,
                    format_func=lambda x: x
                )
                selected_company_id = companies.loc[companies["company_name"] == company_name, "company_id"].values[0]
                if st.button("Назначить редактора"):
                    if selected_editor and company_name:
                        success = assign_editor_to_company(selected_editor, selected_company_id)
                        if success:
                            st.success(f"Редактор {selected_editor} успешно назначен в компанию {company_name}")
                        else:
                            st.error("Ошибка при назначении редактора в компанию.")
                    else:
                        st.error("Пожалуйста, выберите редактора и укажите ID компании.")
        else:
            st.warning("Нет доступных редакторов для назначения.")
    if menu == "Добавить услугу":
        st.subheader("Добавить услугу")
        service_name = st.text_input("Название услуги")
        description = st.text_input("Описание услуги")
        price = st.number_input("Цена услуги")
        if service_name == '':
            st.warning('Напишите название услуги')
        elif service_name and description == '':
            st.warning('Введите описание услуги')
        else:
            if st.button("Добавить"):
                success = add_service(service_name, description, price)
                if success:
                    st.success(f"Услуга {service_name} добавлена в список")
                else:
                    st.error("Такая услуга уже существует")
    if menu == "Прибыль по услугам":
        st.subheader("Прибыль по услуге")
        services = get_services()
        if not services.empty:
            service_id = st.selectbox("Выберите услугу", services["service_name"], index=0, format_func=lambda x: x)
            st.subheader(f"Прибыль услуги {service_id}")
            selected_service_id = services.loc[services["service_name"] == service_id, "service_id"].values[0]
            df = get_service_profit(selected_service_id)
            st.dataframe(df)
        else:
            st.error("Нет доступных услуг")