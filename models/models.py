from datetime import datetime
from datetime import date

from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Table, DateTime, Date, DECIMAL
from sqlalchemy.orm import relationship

from utils.database import Base


class Order(Base):
    __tablename__ = 'Order'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100))
    quantity = Column(Integer)


class RecipeHasIngredient(Base):
    __tablename__ = 'Recipe_has_Ingredient'

    Recipe_id = Column(Integer, ForeignKey("Recipe.id"), primary_key=True)
    Ingredient_id = Column(Integer, ForeignKey("Ingredient.id"), primary_key=True)
    quantity = Column(Integer)


class Recipe(Base):
    __tablename__ = 'Recipe'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100))
    description = Column(String(255))
    products = relationship("Product", back_populates='recipe')
    ingredients = relationship("Ingredient", secondary="Recipe_has_Ingredient", back_populates='recipes')


class Product(Base):
    __tablename__ = 'Product'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100))
    description = Column(String(500))
    type = Column(String(100), nullable=False, default='unknown')
    selling_price = Column(DECIMAL, default=0.0, nullable=False)
    batch_size = Column(Integer, default=0, nullable=False)
    expire_duration = Column(Integer, default=0, nullable=False)
    Recipe_id = Column(Integer, ForeignKey('Recipe.id'))
    recipe = relationship("Recipe", back_populates='products')
    batches = relationship("Batch", back_populates='product')


class LocationHasUsers(Base):
    __tablename__ = 'Location_has_User'

    Location_id = Column(Integer, ForeignKey("Location.id"), primary_key=True)
    User_id = Column(Integer, ForeignKey("User.id"), primary_key=True)


class User(Base):
    __tablename__ = 'User'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100))
    email = Column(String(500), unique=True, nullable=False)
    contactNo = Column(String(500))
    createdOn = Column(String(500))
    password = Column(String(500))
    UserType_id = Column(Integer, ForeignKey('UserType.id'))
    locations = relationship("Location", secondary="Location_has_User", back_populates='users')
    userType = relationship("UserType", back_populates='user')


class UserType(Base):
    __tablename__ = 'UserType'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100))
    user = relationship("User", back_populates='userType')


class Location(Base):
    __tablename__ = 'Location'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100))
    address = Column(String(500))
    users = relationship("User", secondary="Location_has_User", back_populates='locations')


class Ingredient(Base):
    __tablename__ = 'Ingredient'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    grn = relationship("GRN",secondary="GRN_has_Ingredient", back_populates="ingredient")
    recipes = relationship("Recipe", secondary="Recipe_has_Ingredient", back_populates='ingredients')
    current_stock = relationship("CurrentStock", back_populates='ingredient', uselist=False)


class CurrentStock(Base):
    __tablename__ = 'Current_Stock'

    Ingredient_id = Column(Integer, ForeignKey('Ingredient.id'), primary_key=True)
    current_quantity = Column(Integer, nullable=False, default=0)
    ingredient = relationship("Ingredient", back_populates='current_stock')


class GRN(Base):
    __tablename__ = 'GRN'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    issuedDate = Column(DateTime, default=datetime.now)
    ingredient = relationship("Ingredient",secondary="GRN_has_Ingredient", back_populates="grn")


class GRN_has_Ingredient(Base):
    __tablename__ = 'GRN_has_Ingredient'

    GRN_id = Column(Integer, ForeignKey('GRN.id'), primary_key=True)
    Ingredient_id = Column(Integer, ForeignKey('Ingredient.id'), primary_key=True)
    currentQuantity = Column(Integer, default=0)


class Batch(Base):
    __tablename__ = 'Batch'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    productionDate = Column(DateTime, default=datetime.now())
    initialQuantity = Column(Integer)
    availableQuantity = Column(Integer)
    dateOfExpiry = Column(Date)
    product_id = Column(Integer, ForeignKey("Product.id"))
    product = relationship("Product", back_populates="batches")


# models.py

