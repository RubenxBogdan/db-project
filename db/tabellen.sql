create table Spieler (
  Spielername varchar(80),
  NBA_Spielerwins int,
  Position varchar(80),
  Alter int,
  Grösse int,
  Gewicht int,
  Spielerid int primary key,
  constraint fk_team
    foreign key (teamid)
    references team(teamid)
  );
create table Team (
  Teamname varchar(80),
  NBA_Teamwins int,
  City varchar(80),
  Coachname varchar(80),
  Teamid int primary key
  );
create table Stats (
  Statsid int primary key,
  PPG float(1),
  RPG float(1),
  APG float(1),
  SPG float(1),
  BPG float(1),
  FFG% float(1),
  );
create table Spiel (
  Spielid int primary key,
  Score int,
  Ort varchar(80),
  Datum date
  );
create table Spielt_fuer (
  Spielerid varchar(80) 
