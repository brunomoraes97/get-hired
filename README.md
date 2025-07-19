# Get Hired!

Simple Flask application that generates optimized CVs using AI. It also allows you to create an account and login using Supabase as a backend.

## Running locally

1. Create a Python virtual environment and install the requirements:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Create a `.env` file in the project root containing at least:

```dotenv
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
JWT_SECRET=some-secret
```

3. Start the application:

```bash
flask --app wsgi run
```

The web interface will be available at `http://localhost:5000`.

## Setting up Supabase

If you don't already have a Supabase project you can follow these steps:

1. Sign up at [supabase.com](https://supabase.com) and create a new project.
2. In the SQL editor run the following to create a `users` table:

```sql
create table users (
  id uuid default uuid_generate_v4() primary key,
  email text unique not null,
  password text not null,
  name text
);
```

3. Disable Row Level Security for this table or create policies that allow inserting and selecting rows so the application can read and write user profiles.
4. In **Project Settings → API** copy the project URL and the anon or service role key and place them in your `.env` as `SUPABASE_URL` and `SUPABASE_KEY`.

After these steps the login and registration pages should work using Supabase as storage.
