from fastapi import FastAPI
import models  # ← THIS registers Todos with Base!
import database

app = FastAPI()

####################Testing Import####################
# Base knows about Todos:
print("Tables registered with Base:")
print(database.Base.metadata.tables.keys())
# Output: dict_keys(['todos'])

print("\nTable details:")
for table_name, table in database.Base.metadata.tables.items():
    print(f"  {table_name}: {table.columns.keys()}")
# Output: todos: ['id', 'title', 'description', 'priority', 'complete']
######################################################
# Now create the tables
database.Base.metadata.create_all(bind=database.engine)