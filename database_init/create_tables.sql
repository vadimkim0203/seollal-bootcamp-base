create table users (
    user_id serial primary key,
	username varchar(50) unique not null,
    display_name varchar(50)
);
