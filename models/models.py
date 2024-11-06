from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MasterIngredient(Base):
    __tablename__ = 'master_ingredients'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    category = Column(String)  # Optional categorization
    preferred_uom = Column(String)  # Preferred unit of measure
    last_used = Column(String)  # To track usage

    def __repr__(self):
        return f"<MasterIngredient(name='{self.name}')>"

# Your existing models remain the same
class Recipe(Base):
    __tablename__ = 'recipes'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    menu_description = Column(String)

    ingredients = relationship("Ingredient", back_populates="recipe", cascade="all, delete, delete-orphan")
    allergens = relationship("Allergen", back_populates="recipe", cascade="all, delete, delete-orphan")

class Ingredient(Base):
    __tablename__ = 'ingredients'
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    ingredient = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    uom = Column(String, nullable=False)
    master_ingredient_id = Column(Integer, ForeignKey('master_ingredients.id'))  # New reference

    recipe = relationship("Recipe", back_populates="ingredients")
    master_ingredient = relationship("MasterIngredient")  # New relationship

class Allergen(Base):
    __tablename__ = 'allergens'
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    allergen = Column(String, nullable=False)

    recipe = relationship("Recipe", back_populates="allergens")

# Database setup
engine = create_engine('sqlite:///banquet_planning.db')
Session = sessionmaker(bind=engine)
session = Session()

# Create the new table
Base.metadata.create_all(engine)