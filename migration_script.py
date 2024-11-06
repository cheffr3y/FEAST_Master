# migration_script.py
import sqlite3
from models.models import session, Ingredient, MasterIngredient, Base, engine

def migrate_ingredients():
    print("Starting migration...")
    
    # Step 1: Create master ingredients table and populate it
    print("Creating master ingredients...")
    Base.metadata.create_all(engine)
    
    # Get all unique ingredient names from existing ingredients
    existing_ingredients = session.query(Ingredient.ingredient).distinct().all()
    
    # Add each unique ingredient to master_ingredients
    ingredient_count = 0
    for (ingredient_name,) in existing_ingredients:
        existing_master = session.query(MasterIngredient).filter_by(name=ingredient_name).first()
        if not existing_master:
            uom_query = session.query(Ingredient.uom).filter_by(ingredient=ingredient_name).first()
            preferred_uom = uom_query[0] if uom_query else None
            
            master_ingredient = MasterIngredient(
                name=ingredient_name,
                preferred_uom=preferred_uom
            )
            session.add(master_ingredient)
            ingredient_count += 1
    
    session.commit()
    print(f"Added {ingredient_count} ingredients to master list")

    # Step 2: Add master_ingredient_id column to ingredients table
    print("Adding new column to ingredients table...")
    conn = sqlite3.connect('banquet_planning.db')
    cursor = conn.cursor()
    
    # Add the new column if it doesn't exist
    try:
        cursor.execute("ALTER TABLE ingredients ADD COLUMN master_ingredient_id INTEGER REFERENCES master_ingredients(id)")
        conn.commit()
        print("Added master_ingredient_id column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column already exists, skipping...")
        else:
            raise e

    conn.close()
    print("Migration complete!")

if __name__ == "__main__":
    migrate_ingredients()