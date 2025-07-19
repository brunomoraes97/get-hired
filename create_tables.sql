-- SQL script to create required tables for Get Hired!
-- Creates the users table used for authentication
create table if not exists users (
  id uuid default uuid_generate_v4() primary key,
  email text unique not null,
  password text not null,
  name text
);
