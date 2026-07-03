create table customers (
	id serial primary key,
	email varchar(100) unique not null,
	name varchar(100) not null
);

create table customer_info (
	customer_id int primary key references customers(id) on delete cascade,
	phone varchar(20),
	delivery_address text not null
);

create table categories (
	id serial primary key,
	name varchar(100) not null unique
);

create table games (
	id serial primary key,
	title varchar(200) not null,
	price numeric(10, 2) check (price > 0),
	category_id int references categories(id)
);

create table orders (
	id serial primary key,
	customer_id int references customers(id) on delete cascade,
	order_date date default current_date
);

create table order_items (
	order_id int references orders(id),
	game_id int references games(id),
	quantity int check (quantity > 0),
	primary key (order_id, game_id)
);
