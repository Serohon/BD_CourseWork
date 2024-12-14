import streamlit as st
from database.queries import get_services, get_workers, create_order, get_user_orders, get_rating, create_review


def switch_page(page):
    st.session_state.current_page = page

def user_dashboard(username):
    st.title("Личный кабинет клиента")
    # Создание заказа
    menu = st.selectbox("Действия", ["Создать заказ", "Просмотреть заказы"])
    if menu == "Создать заказ":
        st.subheader("Создание заказа")
        services = get_services()
        if not services.empty:
            service_id = st.selectbox("Выберите услугу", services["service_name"], index=0, format_func=lambda x: x)
            selected_service_id = services.loc[services["service_name"] == service_id, "service_id"].values[0]
            workers = get_workers(selected_service_id)
            if workers.empty:
                st.warning("На данный момент нет доступных работников для этой услуги.")
            else:
                st.subheader("Список доступных работников")
                for _, row in workers.iterrows():
                    st.write(
                        f"**{row['full_name']}** (Возраст: {row['age']}, Компания: {row['company_name']}, "
                        f"Средняя оценка: {row['avg_rating']:.1f}/5)"
                    )
                worker_id = st.selectbox(
                    "Выберите работника",
                    workers["full_name"],
                    index=0,
                    format_func=lambda x: x
                )
                selected_worker_id = workers.loc[workers["full_name"] == worker_id, "worker_id"].values[0]
                if st.button("Создать заказ"):
                    create_order(username, selected_worker_id)
                    st.success("Заказ успешно создан!")
        else:
            st.error("Нет доступных услуг")
    if menu == "Просмотреть заказы":
        st.header("Ваши заказы")
        orders = get_user_orders(username)
        unreviewed_orders = orders[orders.isna().any(axis=1)]
        reviewed_orders = orders[orders.notna().all(axis=1)]
        uncompleted_orders = unreviewed_orders[unreviewed_orders['status_name'] != 'Выполнено']
        completed_orders = unreviewed_orders[unreviewed_orders['status_name'] == 'Выполнено']
        st.subheader('Выполненные заказы')
        for _, row in completed_orders.iterrows():
            st.write(f"Заказ на {row['service_name'].lower()} выполнил {row['worker_name']}.")
            st.write("Хотите оценить заказ?")
            rating = st.slider("Рейтинг", min_value=1, max_value=5, step=1)
            review = st.text_area("Отзыв")
            if st.button("Поставить оценку"):
                create_review(rating, review, row['order_id'])
                st.success("Оценка сохранена")
        st.subheader('Заказы в процессе')
        for _, row in uncompleted_orders.iterrows():
            st.write(f"Заказ на {row['service_name'].lower()} выполняет {row['worker_name']}. Статус заказа: {row['status_name']}.")
        st.subheader("Оценённые заказы")
        for _, row in reviewed_orders.iterrows():
            rate = get_rating(row['review_id'])
            st.write(f"Заказ на {row['service_name'].lower()} выполнил {row['worker_name']}. Ваша оценка: {rate}/5.")

