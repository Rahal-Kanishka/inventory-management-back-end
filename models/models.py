from datetime import datetime

from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship

from utils.database import Base

recipe_ingredient = Table(
    'recipe_ingredient', Base.metadata,
    Column('recipe_id', ForeignKey('recipes.id'), primary_key=True),
    Column('ingredient_id', ForeignKey('ingredients.id'), primary_key=True)
)


class Recipe(Base):
    __tablename__ = 'recipes'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True)
    description = Column(String(500))
    instructions = Column(String(1000))
    image = Column(String(500))
    favourite = Column(Integer)
    row_index = Column(Integer)
    ingredients = relationship("Ingredient", secondary="recipe_ingredient", back_populates='recipes')


class Ingredient(Base):
    __tablename__ = 'ingredients'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True)
    description = Column(String(500))
    image = Column(String(500))
    created_by = Column(Integer, default=0)
    created_on = Column(DateTime, default=datetime.now)
    recipes = relationship("Recipe", secondary="recipe_ingredient", back_populates='ingredients')


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(500))
    name = Column(String(500))
    username = Column(String(500))
    password = Column(String(500))
    created_on = Column(DateTime, default=datetime.now)
    type = Column(Integer, default=0)
