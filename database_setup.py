import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key = True)
    username = Column(String(30))

class Category(Base):
    __tablename__ = 'category'
    name = Column(String(30), unique = True)
    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('users.id'))
    users = relationship(User)

    @property
    def serialize(self):
        return {
        'name' : self.name,
        'id' : self.id,
        'user_id' : self.user_id,
        'Items' : []
        }


class Item(Base):
    __tablename__='item'
    id = Column(Integer,primary_key=True)
    name = Column(String(30))
    description = Column(String(300))
    picture = Column(String(300))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category, foreign_keys=[category_id])
    category_name = Column(String(300), ForeignKey('category.name'))
    categoryName = relationship(Category, foreign_keys = [category_name])
    username = Column(String(30), ForeignKey('users.username'))
    users = relationship(User)

    @property
    def serialize(self):
        return {

            'name': self.name,
            'description' : self.description,
            'id':self.id
            }



engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)
