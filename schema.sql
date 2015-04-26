sqlite3 hangman.db

drop table if exists users; 
create table users (
	id integer primary key autoincrement, 
	username text not null unique, 
	password text not null,
	wins integer default 0,
	loses int default 0
);

s

drop table if exists games;
create table games(
	id integer primary key autoincrement,
	status text not null,
	guessed text not null,
	answer text not null,
	username text not null
);

insert into games (status, guessed, answer, username) values ('win', 'test', 'test', 'jess');

create table words(
	id integer primary key autoincrement,
	word text not null
);

insert into words (word) values ('test');