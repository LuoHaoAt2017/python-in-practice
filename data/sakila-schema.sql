-- PostgreSQL 版 Sakila 示例数据库
-- 兼容 PostgreSQL 12+

-- 创建模式
DROP SCHEMA IF EXISTS sakila CASCADE;
CREATE SCHEMA sakila;
SET search_path TO sakila;

-- 1. 创建枚举类型
CREATE TYPE mpaa_rating AS ENUM ('G','PG','PG-13','R','NC-17');
CREATE TYPE special_features AS ENUM ('Trailers','Commentaries','Deleted Scenes','Behind the Scenes');

-- 2. 基础表定义
CREATE TABLE actor (
  actor_id SMALLSERIAL PRIMARY KEY,
  first_name VARCHAR(45) NOT NULL,
  last_name VARCHAR(45) NOT NULL,
  last_update TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_actor_last_name ON actor(last_name);

CREATE TABLE country (
  country_id SMALLSERIAL PRIMARY KEY,
  country VARCHAR(50) NOT NULL,
  last_update TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE city (
  city_id SMALLSERIAL PRIMARY KEY,
  city VARCHAR(50) NOT NULL,
  country_id SMALLINT NOT NULL,
  last_update TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_city_country FOREIGN KEY (country_id) REFERENCES country (country_id) ON UPDATE CASCADE
);
CREATE INDEX idx_fk_country_id ON city(country_id);

CREATE TABLE address (
  address_id SMALLSERIAL PRIMARY KEY,
  address VARCHAR(50) NOT NULL,
  address2 VARCHAR(50),
  district VARCHAR(20) NOT NULL,
  city_id SMALLINT NOT NULL,
  postal_code VARCHAR(10),
  phone VARCHAR(20) NOT NULL,
  last_update TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_address_city FOREIGN KEY (city_id) REFERENCES city (city_id) ON UPDATE CASCADE
);
CREATE INDEX idx_fk_city_id ON address(city_id);

CREATE TABLE language (
  language_id SMALLSERIAL PRIMARY KEY,
  name CHAR(20) NOT NULL,
  last_update TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE category (
  category_id SMALLSERIAL PRIMARY KEY,
  name VARCHAR(25) NOT NULL,
  last_update TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE store (
  store_id SMALLSERIAL PRIMARY KEY,
  manager_staff_id SMALLINT NOT NULL,
  address_id SMALLINT NOT NULL,
  last_update TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT idx_unique_manager UNIQUE (manager_staff_id)
);
CREATE INDEX idx_fk_address_id ON store(address_id);

CREATE TABLE staff (
  staff_id SMALLSERIAL PRIMARY KEY,
  first_name VARCHAR(45) NOT NULL,
  last_name VARCHAR(45) NOT NULL,
  address_id SMALLINT NOT NULL,
  picture BYTEA,
  email VARCHAR(50),
  store_id SMALLINT NOT NULL,
  active BOOLEAN NOT NULL DEFAULT TRUE,
  username VARCHAR(16) NOT NULL,
  password VARCHAR(40),
  last_update TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_fk_store_id ON staff(store_id);
CREATE INDEX idx_fk_address_id ON staff(address_id);

CREATE TABLE customer (
  customer_id SMALLSERIAL PRIMARY KEY,
  store_id SMALLINT NOT NULL,
  first_name VARCHAR(45) NOT NULL,
  last_name VARCHAR(45) NOT NULL,
  email VARCHAR(50),
  address_id SMALLINT NOT NULL,
  active BOOLEAN NOT NULL DEFAULT TRUE,
  create_date TIMESTAMP NOT NULL,
  last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_fk_store_id ON customer(store_id);
CREATE INDEX idx_fk_address_id ON customer(address_id);
CREATE INDEX idx_last_name ON customer(last_name);

CREATE TABLE film (
  film_id SMALLSERIAL PRIMARY KEY,
  title VARCHAR(128) NOT NULL,
  description TEXT,
  release_year INT,
  language_id SMALLINT NOT NULL,
  original_language_id SMALLINT,
  rental_duration SMALLINT NOT NULL DEFAULT 3,
  rental_rate DECIMAL(4,2) NOT NULL DEFAULT 4.99,
  length SMALLINT,
  replacement_cost DECIMAL(5,2) NOT NULL DEFAULT 19.99,
  rating mpaa_rating DEFAULT 'G',
  special_features special_features[],
  last_update TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_title ON film(title);
CREATE INDEX idx_fk_language_id ON film(language_id);
CREATE INDEX idx_fk_original_language_id ON film(original_language_id);

CREATE TABLE film_actor (
  actor_id SMALLINT NOT NULL,
  film_id SMALLINT NOT NULL,
  last_update TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (actor_id, film_id)
);
CREATE INDEX idx_fk_film_id ON film_actor(film_id);

CREATE TABLE film_category (
  film_id SMALLINT NOT NULL,
  category_id SMALLINT NOT NULL,
  last_update TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (film_id, category_id)
);

CREATE TABLE inventory (
  inventory_id SERIAL PRIMARY KEY,
  film_id SMALLINT NOT NULL,
  store_id SMALLINT NOT NULL,
  last_update TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_fk_film_id ON inventory(film_id);
CREATE INDEX idx_store_id_film_id ON inventory(store_id, film_id);

CREATE TABLE rental (
  rental_id SERIAL PRIMARY KEY,
  rental_date TIMESTAMP NOT NULL,
  inventory_id INT NOT NULL,
  customer_id SMALLINT NOT NULL,
  return_date TIMESTAMP,
  staff_id SMALLINT NOT NULL,
  last_update TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT rental_unique UNIQUE (rental_date, inventory_id, customer_id)
);
CREATE INDEX idx_fk_inventory_id ON rental(inventory_id);
CREATE INDEX idx_fk_customer_id ON rental(customer_id);
CREATE INDEX idx_fk_staff_id ON rental(staff_id);

CREATE TABLE payment (
  payment_id SMALLSERIAL PRIMARY KEY,
  customer_id SMALLINT NOT NULL,
  staff_id SMALLINT NOT NULL,
  rental_id INT,
  amount DECIMAL(5,2) NOT NULL,
  payment_date TIMESTAMP NOT NULL,
  last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_fk_staff_id ON payment(staff_id);
CREATE INDEX idx_fk_customer_id ON payment(customer_id);

-- 全文索引表
CREATE TABLE film_text (
  film_id SMALLINT NOT NULL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  search_vector tsvector GENERATED ALWAYS AS (to_tsvector('english', title || ' ' || description)) STORED
);
CREATE INDEX idx_title_description ON film_text USING gin(search_vector);

-- 3. 外键约束
ALTER TABLE store ADD CONSTRAINT fk_store_staff FOREIGN KEY (manager_staff_id) REFERENCES staff(staff_id) ON UPDATE CASCADE;
ALTER TABLE store ADD CONSTRAINT fk_store_address FOREIGN KEY (address_id) REFERENCES address(address_id) ON UPDATE CASCADE;
ALTER TABLE staff ADD CONSTRAINT fk_staff_store FOREIGN KEY (store_id) REFERENCES store(store_id) ON UPDATE CASCADE;
ALTER TABLE staff ADD CONSTRAINT fk_staff_address FOREIGN KEY (address_id) REFERENCES address(address_id) ON UPDATE CASCADE;
ALTER TABLE customer ADD CONSTRAINT fk_customer_address FOREIGN KEY (address_id) REFERENCES address(address_id) ON UPDATE CASCADE;
ALTER TABLE customer ADD CONSTRAINT fk_customer_store FOREIGN KEY (store_id) REFERENCES store(store_id) ON UPDATE CASCADE;
ALTER TABLE film ADD CONSTRAINT fk_film_language FOREIGN KEY (language_id) REFERENCES language(language_id) ON UPDATE CASCADE;
ALTER TABLE film ADD CONSTRAINT fk_film_language_original FOREIGN KEY (original_language_id) REFERENCES language(language_id) ON UPDATE CASCADE;
ALTER TABLE film_actor ADD CONSTRAINT fk_film_actor_actor FOREIGN KEY (actor_id) REFERENCES actor(actor_id) ON UPDATE CASCADE;
ALTER TABLE film_actor ADD CONSTRAINT fk_film_actor_film FOREIGN KEY (film_id) REFERENCES film(film_id) ON UPDATE CASCADE;
ALTER TABLE film_category ADD CONSTRAINT fk_film_category_film FOREIGN KEY (film_id) REFERENCES film(film_id) ON UPDATE CASCADE;
ALTER TABLE film_category ADD CONSTRAINT fk_film_category_category FOREIGN KEY (category_id) REFERENCES category(category_id) ON UPDATE CASCADE;
ALTER TABLE inventory ADD CONSTRAINT fk_inventory_store FOREIGN KEY (store_id) REFERENCES store(store_id) ON UPDATE CASCADE;
ALTER TABLE inventory ADD CONSTRAINT fk_inventory_film FOREIGN KEY (film_id) REFERENCES film(film_id) ON UPDATE CASCADE;
ALTER TABLE rental ADD CONSTRAINT fk_rental_staff FOREIGN KEY (staff_id) REFERENCES staff(staff_id) ON UPDATE CASCADE;
ALTER TABLE rental ADD CONSTRAINT fk_rental_inventory FOREIGN KEY (inventory_id) REFERENCES inventory(inventory_id) ON UPDATE CASCADE;
ALTER TABLE rental ADD CONSTRAINT fk_rental_customer FOREIGN KEY (customer_id) REFERENCES customer(customer_id) ON UPDATE CASCADE;
ALTER TABLE payment ADD CONSTRAINT fk_payment_rental FOREIGN KEY (rental_id) REFERENCES rental(rental_id) ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE payment ADD CONSTRAINT fk_payment_customer FOREIGN KEY (customer_id) REFERENCES customer(customer_id) ON UPDATE CASCADE;
ALTER TABLE payment ADD CONSTRAINT fk_payment_staff FOREIGN KEY (staff_id) REFERENCES staff(staff_id) ON UPDATE CASCADE;

-- 4. 自动更新 last_update 触发器函数
CREATE OR REPLACE FUNCTION update_last_update_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.last_update = CURRENT_TIMESTAMP;
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 为所有表添加更新时间触发器
DO $$
DECLARE
    tbl RECORD;
BEGIN
    FOR tbl IN SELECT tablename FROM pg_tables WHERE schemaname = 'sakila' AND tablename != 'film_text'
    LOOP
        EXECUTE format('CREATE TRIGGER trigger_%I_last_update
                        BEFORE UPDATE ON %I
                        FOR EACH ROW EXECUTE FUNCTION update_last_update_column()',
                        tbl.tablename, tbl.tablename);
    END LOOP;
END $$;

-- 5. film_text 同步触发器
CREATE OR REPLACE FUNCTION sync_film_text()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO film_text (film_id, title, description) VALUES (NEW.film_id, NEW.title, NEW.description);
    ELSIF TG_OP = 'UPDATE' THEN
        UPDATE film_text SET title=NEW.title, description=NEW.description WHERE film_id=OLD.film_id;
    ELSIF TG_OP = 'DELETE' THEN
        DELETE FROM film_text WHERE film_id=OLD.film_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_film_sync AFTER INSERT OR UPDATE OR DELETE ON film
FOR EACH ROW EXECUTE FUNCTION sync_film_text();

-- 6. 视图定义
CREATE VIEW customer_list AS
SELECT cu.customer_id AS ID,
       cu.first_name || ' ' || cu.last_name AS name,
       a.address AS address,
       a.postal_code AS "zip code",
       a.phone AS phone,
       city.city AS city,
       country.country AS country,
       CASE WHEN cu.active THEN 'active' ELSE '' END AS notes,
       cu.store_id AS SID
FROM customer cu
JOIN address a ON cu.address_id = a.address_id
JOIN city ON a.city_id = city.city_id
JOIN country ON city.country_id = country.country_id;

CREATE VIEW film_list AS
SELECT film.film_id AS FID,
       film.title AS title,
       film.description AS description,
       category.name AS category,
       film.rental_rate AS price,
       film.length AS length,
       film.rating AS rating,
       string_agg(actor.first_name || ' ' || actor.last_name, ', ') AS actors
FROM film
LEFT JOIN film_category ON film_category.film_id = film.film_id
LEFT JOIN category ON category.category_id = film_category.category_id
LEFT JOIN film_actor ON film.film_id = film_actor.film_id
LEFT JOIN actor ON film_actor.actor_id = actor.actor_id
GROUP BY film.film_id, category.name;

CREATE VIEW nicer_but_slower_film_list AS
SELECT film.film_id AS FID,
       film.title AS title,
       film.description AS description,
       category.name AS category,
       film.rental_rate AS price,
       film.length AS length,
       film.rating AS rating,
       string_agg(initcap(actor.first_name) || ' ' || initcap(actor.last_name), ', ') AS actors
FROM film
LEFT JOIN film_category ON film_category.film_id = film.film_id
LEFT JOIN category ON category.category_id = film_category.category_id
LEFT JOIN film_actor ON film.film_id = film_actor.film_id
LEFT JOIN actor ON film_actor.actor_id = actor.actor_id
GROUP BY film.film_id, category.name;

CREATE VIEW staff_list AS
SELECT s.staff_id AS ID,
       s.first_name || ' ' || s.last_name AS name,
       a.address AS address,
       a.postal_code AS "zip code",
       a.phone AS phone,
       city.city AS city,
       country.country AS country,
       s.store_id AS SID
FROM staff s
JOIN address a ON s.address_id = a.address_id
JOIN city ON a.city_id = city.city_id
JOIN country ON city.country_id = country.country_id;

CREATE VIEW sales_by_store AS
SELECT
    c.city || ', ' || cy.country AS store,
    m.first_name || ' ' || m.last_name AS manager,
    SUM(p.amount) AS total_sales
FROM payment p
INNER JOIN rental r ON p.rental_id = r.rental_id
INNER JOIN inventory i ON r.inventory_id = i.inventory_id
INNER JOIN store s ON i.store_id = s.store_id
INNER JOIN address a ON s.address_id = a.address_id
INNER JOIN city c ON a.city_id = c.city_id
INNER JOIN country cy ON c.country_id = cy.country_id
INNER JOIN staff m ON s.manager_staff_id = m.staff_id
GROUP BY s.store_id, c.city, cy.country, m.first_name, m.last_name
ORDER BY cy.country, c.city;

CREATE VIEW sales_by_film_category AS
SELECT
    c.name AS category,
    SUM(p.amount) AS total_sales
FROM payment p
INNER JOIN rental r ON p.rental_id = r.rental_id
INNER JOIN inventory i ON r.inventory_id = i.inventory_id
INNER JOIN film f ON i.film_id = f.film_id
INNER JOIN film_category fc ON f.film_id = fc.film_id
INNER JOIN category c ON fc.category_id = c.category_id
GROUP BY c.name
ORDER BY total_sales DESC;

CREATE VIEW actor_info AS
SELECT
    a.actor_id,
    a.first_name,
    a.last_name,
    string_agg(DISTINCT c.name || ': ' || (
        SELECT string_agg(f.title, ', ' ORDER BY f.title)
        FROM film f
        INNER JOIN film_category fc ON f.film_id = fc.film_id
        INNER JOIN film_actor fa ON f.film_id = fa.film_id
        WHERE fc.category_id = c.category_id AND fa.actor_id = a.actor_id
    ), '; ' ORDER BY c.name) AS film_info
FROM actor a
LEFT JOIN film_actor fa ON a.actor_id = fa.actor_id
LEFT JOIN film_category fc ON fa.film_id = fc.film_id
LEFT JOIN category c ON fc.category_id = c.category_id
GROUP BY a.actor_id, a.first_name, a.last_name;

-- 7. 函数与存储过程
CREATE OR REPLACE FUNCTION get_customer_balance(p_customer_id INT, p_effective_date TIMESTAMP)
RETURNS DECIMAL(5,2) AS $$
DECLARE
    v_rentfees DECIMAL(5,2);
    v_overfees INT;
    v_payments DECIMAL(5,2);
BEGIN
    SELECT COALESCE(SUM(film.rental_rate),0) INTO v_rentfees
    FROM film, inventory, rental
    WHERE film.film_id = inventory.film_id
      AND inventory.inventory_id = rental.inventory_id
      AND rental.rental_date <= p_effective_date
      AND rental.customer_id = p_customer_id;

    SELECT COALESCE(SUM(CASE WHEN (rental.return_date - rental.rental_date) > (film.rental_duration * INTERVAL '1 day')
        THEN EXTRACT(DAY FROM (rental.return_date - rental.rental_date) - (film.rental_duration * INTERVAL '1 day'))
        ELSE 0 END)),0) INTO v_overfees
    FROM rental, inventory, film
    WHERE film.film_id = inventory.film_id
      AND inventory.inventory_id = rental.inventory_id
      AND rental.rental_date <= p_effective_date
      AND rental.customer_id = p_customer_id;

    SELECT COALESCE(SUM(payment.amount),0) INTO v_payments
    FROM payment
    WHERE payment.payment_date <= p_effective_date
    AND payment.customer_id = p_customer_id;

    RETURN v_rentfees + v_overfees - v_payments;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION inventory_held_by_customer(p_inventory_id INT)
RETURNS INT AS $$
DECLARE
    v_customer_id INT;
BEGIN
    SELECT customer_id INTO v_customer_id
    FROM rental
    WHERE return_date IS NULL
    AND inventory_id = p_inventory_id;
    RETURN v_customer_id;
EXCEPTION WHEN NO_DATA_FOUND THEN
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION inventory_in_stock(p_inventory_id INT)
RETURNS BOOLEAN AS $$
DECLARE
    v_rentals INT;
    v_out INT;
BEGIN
    SELECT COUNT(*) INTO v_rentals
    FROM rental
    WHERE inventory_id = p_inventory_id;

    IF v_rentals = 0 THEN
        RETURN TRUE;
    END IF;

    SELECT COUNT(rental_id) INTO v_out
    FROM rental
    WHERE inventory_id = p_inventory_id
    AND return_date IS NULL;

    RETURN v_out = 0;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE film_in_stock(IN p_film_id INT, IN p_store_id INT, OUT p_film_count INT)
LANGUAGE plpgsql
AS $$
BEGIN
    SELECT inventory_id
    FROM inventory
    WHERE film_id = p_film_id
    AND store_id = p_store_id
    AND inventory_in_stock(inventory_id);

    SELECT COUNT(*) INTO p_film_count
    FROM inventory
    WHERE film_id = p_film_id
    AND store_id = p_store_id
    AND inventory_in_stock(inventory_id);
END;
$$;

CREATE OR REPLACE PROCEDURE film_not_in_stock(IN p_film_id INT, IN p_store_id INT, OUT p_film_count INT)
LANGUAGE plpgsql
AS $$
BEGIN
    SELECT inventory_id
    FROM inventory
    WHERE film_id = p_film_id
    AND store_id = p_store_id
    AND NOT inventory_in_stock(inventory_id);

    SELECT COUNT(*) INTO p_film_count
    FROM inventory
    WHERE film_id = p_film_id
    AND store_id = p_store_id
    AND NOT inventory_in_stock(inventory_id);
END;
$$;

CREATE OR REPLACE PROCEDURE rewards_report(
    IN min_monthly_purchases SMALLINT,
    IN min_dollar_amount_purchased DECIMAL(10,2),
    OUT count_rewardees INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    last_month_start DATE;
    last_month_end DATE;
BEGIN
    IF min_monthly_purchases = 0 THEN
        RAISE NOTICE 'Minimum monthly purchases parameter must be > 0';
        RETURN;
    END IF;
    IF min_dollar_amount_purchased = 0.00 THEN
        RAISE NOTICE 'Minimum monthly dollar amount purchased parameter must be > $0.00';
        RETURN;
    END IF;

    last_month_start := date_trunc('month', current_date - interval '1 month');
    last_month_end := (date_trunc('month', current_date) - interval '1 day');

    CREATE TEMP TABLE tmpCustomer (customer_id SMALLINT PRIMARY KEY) ON COMMIT DROP;

    INSERT INTO tmpCustomer (customer_id)
    SELECT p.customer_id
    FROM payment p
    WHERE p.payment_date BETWEEN last_month_start AND last_month_end
    GROUP BY customer_id
    HAVING SUM(p.amount) > min_dollar_amount_purchased
    AND COUNT(*) > min_monthly_purchases;

    SELECT COUNT(*) INTO count_rewardees FROM tmpCustomer;

    SELECT c.*
    FROM tmpCustomer t
    INNER JOIN customer c ON t.customer_id = c.customer_id;
END;
