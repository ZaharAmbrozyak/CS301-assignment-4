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
-- execution time without index: 26.090 ms

create index idx_order_items_quantity on order_items(quantity);


