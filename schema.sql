drop table if exists plants;
create table plants (
  id integer primary key autoincrement,
  name text not null,
  photo_url text not null,
  water_ideal real not null,
  water_tolerance real not null,
  light_ideal real not null,
  light_tolerance real not null,
  acidity_ideal real not null,
  acidity_tolerance real not null,
  humidity_ideal real not null,
  humidity_tolerance real not null,
  mature_on date not null,
  created_at date not null
);