from datetime import datetime
from datetime import date

from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Table, DateTime, Date
from sqlalchemy.orm import relationship

from utils.database import Base


class Order(Base):
    __tablename__ = 'Order'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100))
    quantity = Column(Integer)


class Recipe(Base):
    __tablename__ = 'Recipe'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100))
    description = Column(String(255))


class ProductType(Base):
    __tablename__ = 'producttype'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100))
    code = Column(String(100))
    batchSize = Column(Integer, default=0)
    expireDuration = Column(Integer, default=0)


class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100))
    currentQuantity = Column(Integer, default=0)
    description = Column(String(500))
    ProductType_id = Column(Integer, ForeignKey('producttype.id'))


class LocationHasUsers(Base):
    __tablename__ = 'Location_has_User'

    Location_id = Column(Integer, ForeignKey("Location.id"), primary_key=True)
    User_id = Column(Integer, ForeignKey("User.id"), primary_key=True)


class User(Base):
    __tablename__ = 'User'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100))
    email = Column(String(500))
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
    currentQuantity = Column(Integer)
    image = Column(String)


class GRN(Base):
    __tablename__ = 'GRN'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    issuedDate = Column(DateTime, default=datetime.now)

class Batch(Base):
    __tablename__ = 'batch'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    productionDate = Column(Date)
    Recipe_id = Column(Integer, ForeignKey("recipe.id"))
    initialQuantity = Column(Integer)
    availableQuantity = Column(Integer)
    dateOfExpiry = Column(Date)
    User_id = Column(Integer, ForeignKey("user.id"))


# models.py

class RecipeHasIngredient(Base):
    __tablename__ = 'Recipe_has_Ingredient'

    Recipe_id = Column(Integer, ForeignKey("Recipe.id"), primary_key=True)
    Ingredient_id = Column(Integer, ForeignKey("Ingredient.id"), primary_key=True)
    quantity = Column(Integer)


class Recipe_has_producttype(Base):
    __tablename__ = 'recipe_has_producttype'  # Matches the table name in your database

    Recipe_id = Column(Integer, ForeignKey('recipe.id'), primary_key=True)  # Foreign key reference to `recipe`
    ProductType_id = Column(Integer, ForeignKey('producttype.id'), primary_key=True)  # Foreign key reference to `producttype`


class GRN_has_Ingredient(Base):
    __tablename__ = 'GRN_has_Ingredient'

    GRN_id = Column(Integer, ForeignKey('GRN.id'), primary_key=True)
    Ingredient_id = Column(Integer, ForeignKey('Ingredient.id'), primary_key=True)
    quantity = Column(Integer, default=0)