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
    __tablename__ = 'recipe'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100))
    description = Column(String(255))


class ProductType(Base):
    __tablename__ = 'ProductType'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100))
    code = Column(String(100))
    batch_size = Column(Integer, default=0)
    expire_duration = Column(Integer, default=0)


class Product(Base):
    __tablename__ = 'Product'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100))
    current_quantity = Column(Integer, default=0)
    description = Column(String(500))

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100))
    email = Column(String(500))
    contact_no = Column(String(500))

class Location(Base):
    __tablename__ = 'Location'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100))
    address = Column(String(500))


class Ingredient(Base):
    __tablename__ = 'Ingredient'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    currentQuantity = Column(Integer)


class GRN(Base):
    __tablename__ = 'GRN'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    issued_date = Column(DateTime, default=datetime.now)
    type = Column(Integer, default=0)

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
