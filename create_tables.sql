-- SQL script to create required tables for Get Hired!
-- Creates the users table used for authentication
create table if not exists users (
  id uuid default uuid_generate_v4() primary key,
  email text unique not null,
  password text not null,
  name text
);

-- Stores resume data used to generate LaTeX for each user
create table if not exists latex_data (
  id uuid default uuid_generate_v4() primary key,
  user_email text not null,
  resume_json jsonb not null,
  created_at timestamptz default now()
);
