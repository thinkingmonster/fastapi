# To check schema
.schema

# Open the database
sqlite3 todosapp.db

# Run the inserts
INSERT INTO todos (id, title, description, priority, complete) VALUES (1, 'Buy groceries', 'Get milk, eggs, bread, and vegetables', 3, 0);
INSERT INTO todos (id, title, description, priority, complete) VALUES (2, 'Finish FastAPI tutorial', 'Complete database integration chapter', 5, 0);
INSERT INTO todos (id, title, description, priority, complete) VALUES (3, 'Call dentist', 'Schedule appointment for teeth cleaning', 2, 1);
INSERT INTO todos (id, title, description, priority, complete) VALUES (4, 'Review pull requests', 'Check and approve pending PRs on GitHub', 4, 1);
INSERT INTO todos (id, title, description, priority, complete) VALUES (5, 'Exercise', 'Go for 30 minute run in the park', 3, 0);

# Verify the data
SELECT * FROM todos;

# Exit
.quit

# see table
.mode box