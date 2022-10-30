import sys
import os
from sqlalchemy import Column,Integer,String,DateTime,ForeignKey,Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Units(Base):
    __tablename__ = 'units'
    id = Column(Integer, primary_key=True)
    code = Column(String(50), nullable=False)
    name = Column(String(200), nullable=False)
    
class BinLocation(Base):
    __tablename__ = 'binlocation'
    id = Column(Integer, primary_key=True)
    code = Column(String(50), nullable=False)

class Products(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    code = Column(String(100), nullable=False)
    name = Column(String(350), nullable=False)
    units_id = Column(Integer, ForeignKey('units.id'))
    units = relationship(Units)
    price = Column(Float)
    image = Column(String(350), nullable=True)
    
class Projects(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    code = Column(String(50), nullable=False)
    name = Column(String(350), nullable=False)
    
class Suppliers(Base):
    __tablename__ = 'suppliers'
    id = Column(Integer, primary_key=True)
    code = Column(String(50), nullable=False)
    name = Column(String(350), nullable=False)
    
class Incoming(Base):
    __tablename__ = 'incoming'
    id = Column(Integer, primary_key=True)
    in_date = Column(DateTime)
    suppliers_id = Column(Integer, ForeignKey('suppliers.id'))
    suppliers = relationship(Suppliers)
    products_id = Column(Integer, ForeignKey('products.id'))
    products = relationship(Products)
    binlocation_id = Column(Integer, ForeignKey('binlocation.id'))
    binlocation = relationship(BinLocation)
    name = Column(String(350), nullable=False)
    quantity = Column(Float)
    remarks = Column(String(350), nullable=True)
    
class Outgoing(Base):
    __tablename__ = 'outgoing'
    id = Column(Integer, primary_key=True)
    out_date = Column(DateTime)
    projects_id = Column(Integer, ForeignKey('projects.id'))
    projects = relationship(Projects)
    products_id = Column(Integer, ForeignKey('products.id'))
    products = relationship(Products)
    binlocation_id = Column(Integer, ForeignKey('binlocation.id'))
    binlocation = relationship(BinLocation)
    name = Column(String(350), nullable=False)
    quantity = Column(Float)
    remarks = Column(String(350), nullable=True)
