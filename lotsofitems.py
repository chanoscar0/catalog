from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Item, User

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


category3 = Category(user_id = 1, name = "Lacrosse")

session.add(category3)
session.commit()

category3 = Category(user_id = 1, name = "Frisbee")

session.add(category3)
session.commit()

category3 = Category(user_id = 1, name = "Snow Boarding")

session.add(category3)
session.commit()

category3 = Category(user_id = 1, name = "Gymnastics")

session.add(category3)
session.commit()

category3 = Category(user_id = 1, name = "Rowing")

session.add(category3)
session.commit()

category3 = Category(user_id = 1, name = "Baseball")

session.add(category3)
session.commit()

category3 = Category(user_id = 1, name = "Skiing")

session.add(category3)
session.commit()

category4 = Category(user_id = 1, name = "Basketball")

session.add(category4)
session.commit()

category5 = Category(user_id = 1, name = "Tennis")

session.add(category5)
session.commit()

category6 = Category(user_id = 1, name = "Bowling")

session.add(category6)
session.commit()

category7 = Category(user_id = 1, name = "Biking")

session.add(category7)
session.commit()

print ('Added Categories')
