drop table if exists users;
drop table if exists ligues;
drop table if exists teams;
drop table if exists ligue_players;
drop table if exists matches;
drop table if exists divisions;
create table users (
    user_id integer primary key autoincrement,
    username text not null,
    hash text not null,
    deleted integer default 0,
    email text,
    user_div integer not null
);
CREATE TABLE ligues (
    ligue_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    ligue_name TEXT NOT NULL,
    rematch INTEGER NOT NULL,
    single_player INTEGER NOT NULL,
    start_date text NOT NULL,
    finish_date text,
    ligue_owner INTEGER NOT NULL,
    ligue_location INTEGER NOT NULL,
    started INTEGER NOT NULL DEFAULT 1,
    closed INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE teams (
    team_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    player1 INTEGER NOT NULL,
    player2 INTEGER NOT NULL
);
CREATE TABLE ligue_players (
    list_id integer primary key autoincrement not null,
    ligue integer not null,
    player integer not null,
    points integer,
    played_games integer
);
CREATE TABLE matches (
    match_id integer primary key autoincrement not null,
    ligue integer not null,
    match_data text not null,
    team1 integer not null,
    goals_t1 integer,
    team2 integer not null,
    goals_t2 integer
);
CREATE TABLE divisions (
    div_id integer primary key autoincrement not null,
    div_name text not null,
    logo text
);
