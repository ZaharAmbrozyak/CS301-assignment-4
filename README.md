Це четверта домашня робота з курсу Бази Даних. В ній я вирішив створити базу даних для магазину настільних ігор, оскільки недавно купував в одному органайзер для гри Root

Репозиторій складається з таких файлів:
* tables.sql - скрипти для створення таблиць
* optimization.sql - невеликий файл з оптимізацією фільтрації в запиті
* users.sql - невеликий файл, де я створив кілька нових користувачів, та дав їм різні права, в залежності від посади користувача.
* extra_points.sql - файл, де зберігаються скрипти для додаткових балів
* ERD.png - фотографія ERD діаграми моєї БД
* main.py - python-скрипт для генерації даних. Був створений з допомогою Gemini.
* requirements.txt - список необхідних модулів для python-скрипта
* task.md - завдання, які треба було виконати

Надалі буду розбирати кожен файл .sql окремо:

## Структура таблиць (tables.sql)
Я придумав наступну структуру таблиць:
##### customers
* id PK,
* email,
* name
##### customers_info (зв'язок 1:1 з таблицею customers)
* customer_id PK, референс на customer(id)
* phone,
* delivery_address

##### categories (зв'язок 1:M з games)
* id PK,
* name

##### games (зв'язок M:1 з categories)
* id PK,
* title,
* price,
* category_id FK (categories(id))

##### orders (зв'язок 1:M з customers)
* id PK,
* customer_id FK (customers(id)),
* order_date

##### table_order_items (зв'язок M:M між orders та games)
* order_id PK (references orders(id)),
* game_id PK (references games(id)),
* quantity,
## Оптимізація (optimization.sql)
Скрипт:
```
explain analyze
select
	game_id,
	sum(quantity) as total
from
	order_items
where
	quantity > 5
group by 
	game_id;
```
Результат explain analyze:
```
GroupAggregate  (cost=7071.94..7071.96 rows=1 width=12) (actual time=24.474..26.018 rows=0.00 loops=1)
  Group Key: game_id
  Buffers: shared hit=2576
  ->  Sort  (cost=7071.94..7071.95 rows=1 width=8) (actual time=24.473..26.016 rows=0.00 loops=1)
        Sort Key: game_id
        Sort Method: quicksort  Memory: 25kB
        Buffers: shared hit=2576
        ->  Gather  (cost=1000.00..7071.93 rows=1 width=8) (actual time=24.449..25.992 rows=0.00 loops=1)
              Workers Planned: 1
              Workers Launched: 1
              Buffers: shared hit=2573
              ->  Parallel Seq Scan on order_items  (cost=0.00..6071.83 rows=1 width=8) (actual time=20.310..20.311 rows=0.00 loops=2)
                    Filter: (quantity > 5)
                    Rows Removed by Filter: 237920
                    Buffers: shared hit=2573
Planning:
  Buffers: shared hit=79
Planning Time: 0.720 ms
Execution Time: 26.090 ms
```
Бачимо по Query Plan:
1. Запит тривав 26,090 мс, хоча планувалося 0,720 мс
2. Була агрегація з group_key: game_id
3. Далі зробило фільтр quantity > 5. Використало **Seq Scan**. Прибрало 237920 рядків

Тепер оптимізуємо:
```
create index idx_order_items_quantity on order_items(quantity);
```

Запускаємо цей же скрипт. Результат explain analyze:
```
GroupAggregate  (cost=8.29..8.31 rows=1 width=12) (actual time=0.070..0.071 rows=0.00 loops=1)
  Group Key: game_id
  Buffers: shared read=3
  ->  Sort  (cost=8.29..8.30 rows=1 width=8) (actual time=0.069..0.069 rows=0.00 loops=1)
        Sort Key: game_id
        Sort Method: quicksort  Memory: 25kB
        Buffers: shared read=3
        ->  Index Scan using idx_order_items_quantity on order_items  (cost=0.42..8.28 rows=1 width=8) (actual time=0.063..0.064 rows=0.00 loops=1)
              Index Cond: (quantity > 5)
              Index Searches: 1
              Buffers: shared read=3
Planning:
  Buffers: shared hit=21 read=1
Planning Time: 1.244 ms
Execution Time: 0.119 ms
```
Знову дивимось:
1. Час тепер зайняв 0,119 мс, хоча планувалось 1.244 мс
2. Була агрегація з group_key: game_id
3. Тепер був використаний Index Scan для фільтрації

## Створення користувачів (users.sql)
Скрипт:
```
create user shop_admin with password 'cool-password-1';
create user shop_manager with password 'cool-password-2';
create user shop_junior with password 'bad-password-1';
create user shop_senior with password 'cool-password-3';

grant all privileges on database tabletop to shop_admin;

grant select, insert, update on all tables in schema public to shop_manager;

grant select on games, categories to shop_junior;

grant select, insert, update on all tables in schema public to shop_senior;

```

Для адміна я дав всі права доступу, бо він - адмін

Для менеджера я дав трохи менші права доступу, але все ще дозволяю більшість операцій

Для junior-а я даю лише доступ на select з двох таблиць, щоб він не наробив біди

Для senior-а я даю ті ж самі доступи, що й менеджеру

## Додаткові завдання (extra_points.sql)

### Створити view
Фактично все те саме, тільки ще треба додати create view. Вирішив зробити невеликий запит з одним join:
```
create view available_games as
select
	g.title as game_title,
	g.price as game_price,
	c.name as category_name
from games g
inner join categories c on 
	g.category_id = c.id;
```

### Процедура
Створив невеличку процедуру, щоб можна було легше додавати нові категорії:

```
create procedure add_new_category(new_category_name varchar)
language plpgsql
as $$
begin
insert into categories(name) values (new_category_name);
end;
$$;
```

### Функція + тригер
Cтворив функцію, яка буде перевіряти ціну на те, чи не є вона надто низькою. Далі створюю тригер, який викликає цю функцію при кожному інсерті, або апдейті в табличці games:

```
create function check_minimum_price()
returns trigger
language plpgsql
as $$
begin
	if new.price < 100.00 then
	raise exception 'ціна гри не може бути такою дешевою !';
end if;
return new;
end;
$$;

create trigger trg_check_price
before insert or update on games
for each row
execute function check_minimum_price();
```
