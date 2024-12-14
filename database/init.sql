CREATE TABLE role_codes (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(20) UNIQUE NOT NULL,
    code VARCHAR(50)
);

INSERT INTO role_codes (role_id, role_name, code) VALUES
(1, 'Администратор', 'ADMIN123'),
(2, 'Редактор', 'EDITOR456'),
(3, 'Пользователь', '');
-- Таблица компаний
CREATE TABLE companies (
    company_id SERIAL PRIMARY KEY,
    company_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role_id INT NOT NULL REFERENCES role_codes(role_id),
    company_id INT REFERENCES companies(company_id)
);
COMMENT ON TABLE users IS 'Информации о пользователях';
COMMENT ON COLUMN users.user_id IS 'Уникальный идентификатор пользователя';
COMMENT ON COLUMN users.username IS 'Имя пользователя, уникальное';
COMMENT ON COLUMN users.password_hash IS 'Хэш пароля пользователя';
COMMENT ON COLUMN users.role_id IS 'Идентификатор роли пользователя (Администратор, Редактор, Пользователь)';

COMMENT ON TABLE companies IS 'Данные о компаниях';
COMMENT ON COLUMN companies.company_id IS 'Уникальный идентификатор компании';
COMMENT ON COLUMN companies.company_name IS 'Название компании, уникальное';
COMMENT ON COLUMN companies.description IS 'Описание компании';


-- Таблица услуг
CREATE TABLE services (
    service_id SERIAL PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    description TEXT
);
COMMENT ON TABLE services IS 'Данные об услугах';
COMMENT ON COLUMN services.service_id IS 'Уникальный идентификатор услуги';
COMMENT ON COLUMN services.service_name IS 'Название услуги';
COMMENT ON COLUMN services.description IS 'Описание услуги';
COMMENT ON COLUMN services.price IS 'Цена услуги';

-- Таблица работников
CREATE TABLE workers (
    worker_id SERIAL PRIMARY KEY,
    company_id INT NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    service_id INT NOT NULL REFERENCES services(service_id) ON DELETE CASCADE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone_number VARCHAR(20),

    age INT NOT NULL
);
ALTER TABLE workers
ADD COLUMN in_work BOOLEAN DEFAULT FALSE;

COMMENT ON TABLE workers IS 'Данные о работниках';
COMMENT ON COLUMN workers.worker_id IS 'Уникальный идентификатор работника';
COMMENT ON COLUMN workers.company_id IS 'Идентификатор компании, в которой работает сотрудник';
COMMENT ON COLUMN workers.first_name IS 'Имя работника';
COMMENT ON COLUMN workers.last_name IS 'Фамилия работника';
COMMENT ON COLUMN workers.phone_number IS 'Контактный телефон работника';
COMMENT ON COLUMN workers.age IS 'Возраст работника';

-- Таблица статусов заказов
CREATE TABLE statuses (
    status_id SERIAL PRIMARY KEY,
    status_name VARCHAR(50) UNIQUE NOT NULL
);
COMMENT ON TABLE statuses IS 'Статусы заказов';
COMMENT ON COLUMN statuses.status_id IS 'Уникальный идентификатор статуса';
COMMENT ON COLUMN statuses.status_name IS 'Название статуса (Ожидание, Выполняется, Выполнено)';
INSERT INTO statuses(status_id, status_name) VALUES
(1, 'Ожидание'),
(2, 'Выполняется'),
(3, 'Выполнено');
-- Таблица заказов
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id),
    worker_id INT NOT NULL REFERENCES workers(worker_id),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status_id INT NOT NULL REFERENCES statuses(status_id)
);
COMMENT ON TABLE orders IS 'Данные о заказах';
COMMENT ON COLUMN orders.order_id IS 'Уникальный идентификатор заказа';
COMMENT ON COLUMN orders.user_id IS 'Идентификатор пользователя, создавшего заказ';
COMMENT ON COLUMN orders.worker_id IS 'Идентификатор рабочего, выполняющего услугу';
COMMENT ON COLUMN orders.order_date IS 'Дата и время создания заказа';
COMMENT ON COLUMN orders.status_id IS 'Идентификатор текущего статуса заказа';

-- Таблица отзывов
CREATE TABLE reviews (
    review_id SERIAL PRIMARY KEY,
    review_text TEXT,
    order_id INT NOT NULL REFERENCES orders(order_id),
    rating INT CHECK (rating BETWEEN 1 AND 5),
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE reviews IS 'Отзывы о компании';
COMMENT ON COLUMN reviews.review_text IS 'Текст отзыва';
COMMENT ON COLUMN reviews.rating IS 'Оценка пользователя (от 1 до 5)';
COMMENT ON COLUMN reviews.review_date IS 'Дата и время создания отзыва';

CREATE PROCEDURE create_user(
    username_input VARCHAR,
    password_hash_input VARCHAR,
    role_id_input INT,
    company_id_input INT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO users (username, password_hash, role_id, company_id)
    VALUES (username_input, password_hash_input, role_id_input, company_id_input);
END;
$$;

CREATE PROCEDURE add_company(
    company_name_input VARCHAR,
    description_input TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO companies (company_name, description)
    VALUES (company_name_input, description_input);
END;
$$;


CREATE PROCEDURE add_service(
    service_name_input VARCHAR,
    service_price DECIMAL(10, 2),
    description_input TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO services (service_name, price, description)
    VALUES (service_name_input, service_price, description_input);
END;
$$;

CREATE PROCEDURE create_order(pu_user_id INT, p_worker_id INT)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO orders (user_id, worker_id, order_date, status_id)
    VALUES (pu_user_id, p_worker_id, CURRENT_TIMESTAMP, 1);
END;
$$;


CREATE PROCEDURE update_order_status(
    order_id_input INT,
    new_status_id INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE orders
    SET status_id = new_status_id
    WHERE order_id = order_id_input;
END;
$$;

CREATE PROCEDURE add_worker(
    company_id_input INT,
    first_name_input VARCHAR,
    last_name_input VARCHAR,
    pos_id_input INT,
    phone_number_input VARCHAR,
    age_input INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO workers (company_id, first_name, last_name, phone_number, age, service_id)
    VALUES (company_id_input, first_name_input, last_name_input,phone_number_input, age_input, pos_id_input);
END;
$$;

CREATE PROCEDURE create_review(
    rating_input INT,
    review_text_input TEXT,
    order_id_input INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO reviews (rating, review_text, review_date, order_id)
    VALUES (rating_input, review_text_input, CURRENT_TIMESTAMP, order_id_input);
END;
$$;


CREATE OR REPLACE FUNCTION set_worker_in_work()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE workers
    SET in_work = TRUE
    WHERE worker_id = NEW.worker_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_order_insert
AFTER INSERT ON orders
FOR EACH ROW
EXECUTE FUNCTION set_worker_in_work();

CREATE OR REPLACE FUNCTION reset_worker_in_work()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status_id = (SELECT status_id FROM statuses WHERE status_name = 'Выполнено') THEN
        UPDATE workers
        SET in_work = FALSE
        WHERE worker_id = NEW.worker_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_order_update
AFTER UPDATE OF status_id ON orders
FOR EACH ROW
EXECUTE FUNCTION reset_worker_in_work();

CREATE VIEW editor_company_profit_view AS
SELECT
    c.company_name,
    COUNT(o.order_id) as total_orders,
    SUM(s.price) as profit
FROM
    companies c
LEFT JOIN
    orders o ON o.order_id = c.company_id
LEFT JOIN
    workers w on w.worker_id = o.worker_id
LEFT JOIN
    services s on w.service_id = s.service_id
GROUP BY c.company_name;

CREATE VIEW service_order_count AS
SELECT
    s.service_name,
    COUNT(o.order_id) as total_orders,
    COUNT(o.order_id) * s.price as profit
FROM
    services s
LEFT JOIN
    workers w on s.service_id = w.service_id
LEFT JOIN
    orders o on w.worker_id = o.worker_id
GROUP BY
    s.service_name, s.price
