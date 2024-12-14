import streamlit as st
from database.queries import add_worker, get_all_services, fetch_orders_for_company, update_order_status, \
    get_company_profit


def editor_dashboard(company_id):
    st.title(f"Панель редактора {company_id} компании")

    # Добавление работника
    menu = st.selectbox("Действия", ["Добавить рабочего", "Управление заказами", "Прибыль компании"])
    if menu == "Добавить рабочего":
        st.subheader("Добавление рабочего")
        first_name = st.text_input("Имя")
        last_name = st.text_input("Фамилия")
        phone_number = st.text_input("Телефон")
        age = st.number_input("Возраст", min_value=18)
        positions = get_all_services()
        parsed_positions = [position['service_name'] for position in positions]
        position = st.selectbox("Выберите должность", parsed_positions)
        if first_name == '' or last_name == '' or phone_number == '':
            st.warning("Введите данные рабочего")
        else:
            if st.button("Добавить работника"):
                success = add_worker(company_id, first_name, last_name, position, phone_number, age)
                if success:
                    st.success("Работник добавлен")
                else:
                    st.error("Этот работник уже добавлен")

    elif menu == "Управление заказами":
        st.subheader("Список заказов компании")
        orders = fetch_orders_for_company(st.session_state["company_id"])
        if len(orders) == 0:
            st.warning("У компании нет активных/не было заказов")
        completed_orders = [order for order in orders if order['status_name'] == 'Выполнено']
        uncompleted_orders = [order for order in orders if order['status_name'] != 'Выполнено']
        for order in completed_orders:
            st.subheader('Выполненные заказы')
            st.write(f"Заказ ID: {order['order_id']}, Услуга: {order['service_name']}, Статус: {order['status_name']}")
        for order in uncompleted_orders:
            st.subheader('Заказы в процессе')
            st.write(f"Заказ ID: {order['order_id']}, Услуга: {order['service_name']}, Статус: {order['status_name']}")
            new_status = st.selectbox(f"Изменить статус заказа {order['order_id']}",
                                      ["Ожидание", "Выполняется", "Выполнено"], index=0)
            if st.button(f"Обновить статус для заказа {order['order_id']}"):
                update_order_status(order["order_id"], new_status)
                st.success(f"Статус заказа {order['order_id']} обновлен на {new_status}.")
    elif menu == "Прибыль компании":
        st.subheader("Прибыль компании")
        df = get_company_profit(company_id)
        st.dataframe(df)