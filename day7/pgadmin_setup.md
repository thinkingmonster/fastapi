# pgAdmin Setup for FastAPI Todo App

## Quick Connection Guide

### Step 1: Open pgAdmin
- Launch "pgAdmin 4" from Applications
- Set a master password when prompted (first time only)

### Step 2: Add Server Connection
1. Right-click "Servers" in the left panel
2. Select "Register" > "Server"

### Step 3: Connection Details

**General Tab:**
- Name: `FastAPI Todo App` (or any name you prefer)

**Connection Tab:**
- Host name/address: `localhost`
- Port: `5432`
- Maintenance database: `postgres` (default)
- Username: `akashthakur`
- Password: (leave empty for local dev, or set if you configured one)
- Save password: ✓ (optional)

### Step 4: Test Connection
- Click "Save" to test and save the connection

### Step 5: Access Your Database
- Expand "FastAPI Todo App" > "Databases" > "todosapp"
- You'll see your tables: `users` and `todos`

## Useful pgAdmin Features

1. **Query Tool**: Right-click database > "Query Tool" to run SQL
2. **View Data**: Right-click table > "View/Edit Data" > "All Rows"
3. **Table Properties**: Right-click table > "Properties" to see schema
4. **Execute SQL**: Use Query Tool to run custom queries

## Quick SQL Queries to Try

```sql
-- View all users
SELECT * FROM users;

-- View all todos
SELECT * FROM todos;

-- View todos with user info (join)
SELECT t.id, t.title, t.description, u.username, u.email
FROM todos t
JOIN users u ON t.owner_id = u.id;
```

