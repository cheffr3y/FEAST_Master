# migration_recipe_categories.py
from models.models import session, Recipe, Base, engine
from menu_categories import MENU_CATEGORIES

def add_category_columns():
    import sqlite3
    conn = sqlite3.connect('banquet_planning.db')
    cursor = conn.cursor()
    
    try:
        # Add category column
        cursor.execute("ALTER TABLE recipes ADD COLUMN category TEXT")
        # Add subcategory column
        cursor.execute("ALTER TABLE recipes ADD COLUMN subcategory TEXT")
        conn.commit()
        print("Added category columns to recipes table")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Category columns already exist")
        else:
            raise e
    finally:
        conn.close()

if __name__ == "__main__":
    add_category_columns()