-- створити view
create view available_games as
select
	g.title as game_title,
	g.price as game_price,
	c.name as category_name
from games g
inner join categories c on 
	g.category_id = c.id;

-- процедура
create procedure add_new_category(new_category_name varchar)
language plpgsql
as $$
begin
	insert into categories(name) values (new_category_name);
end;
$$;

-- функція + тригер
create function check_minimum_price()
returns trigger
language plpgsql
as $$
begin
	-- дурака не продаєм, в нас дорогі ігри
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
