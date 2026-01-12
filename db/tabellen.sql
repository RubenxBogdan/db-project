create table Spieler (
  Spielername varchar(80) primary key,
  NBA_Spielerwins int,
  Position varchar(80),
  Alter int,
  Grösse int,
  Gewicht int
  );
create table Team (
  Teamname varchar(80) primary key,
  NBA_Teamwins int,
  City varchar(80),
  Coachname varchar(80)
  );
create table Stats (
  Statsid int primary key,
  PPG float,
  RPG float,
  APG float,
  SPG float,
  BPG float,
  FFG% float
  );
create table Spiel (
  Spielid int primary key,
  Score int,
  Ort varchar(80),
  Datum date
  );
