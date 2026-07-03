create user shop_admin with password 'cool-password-1';
create user shop_manager with password 'cool-password-2';
create user shop_junior with password 'bad-password-1';
create user shop_senior with password 'cool-password-3';

grant all privileges on database tabletop to shop_admin;

grant select, insert, update on all tables in schema public to shop_manager;

grant select on games, categories to shop_junior;

grant select, insert, update on all tables in schema public to shop_senior;
