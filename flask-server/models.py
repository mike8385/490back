
from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry  # Import Geometry type


db = SQLAlchemy()


class Category(db.Model):
    __tablename__ = 'category'
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))

class FilmCategory(db.Model):
    __tablename__ = 'film_category'
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'), primary_key=True)
    film_id = db.Column(db.Integer, primary_key=True)

class Film(db.Model):
    __tablename__ = 'film'
    film_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    description = db.Column(db.String(128))
    release_year = db.Column(db.Date)
    language_id = db.Column(db.Integer)
    original_language_id = db.Column(db.Integer)
    rental_duration = db.Column(db.Integer)
    rental_rate = db.Column(db.Float)
    length = db.Column(db.Integer)
    replacement_cost = db.Column(db.Float)
    #rating = db.Column(db.Enum)

class Rental(db.Model):
    __tablename__ = 'rental'
    rental_id = db.Column(db.Integer, primary_key=True)
    rental_date = db.Column(db.DateTime, nullable=False)  # Rental timestamp
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.inventory_id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    return_date = db.Column(db.DateTime, nullable=True)  # Nullable, since some may not be returned yet
    staff_id = db.Column(db.Integer)#, db.ForeignKey('staff.staff_id'), nullable=False)
    last_update = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class Inventory(db.Model):
    __tablename__ = 'inventory'
    inventory_id = db.Column(db.Integer, primary_key=True)
    film_id = db.Column(db.Integer, db.ForeignKey('film.film_id'))
    store_id = db.Column(db.Integer, db.ForeignKey('store.store_id'))


class Film_Actor(db.Model):
    __tablename__ = 'film_actor'
    actor_id = db.Column(db.Integer, db.ForeignKey('actor.actor_id'), primary_key=True)
    film_id = db.Column(db.Integer, db.ForeignKey('film.film_id'), primary_key=True)


class Actor(db.Model):
    __tablename__ = 'actor'
    actor_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45))
    last_name = db.Column(db.String(45))
 #   class Category(db.Model):
  #  __tablename__ = 'category'
   # category_id = db.Column(db.Integer, primary_key=True)
    #name = db.Column(db.String(25))

class Address(db.Model):
    __tablename__ = 'address'
    address_id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(50))
    address2 = db.Column(db.String(50), nullable = True)
    district = db.Column(db.String(20))
    city_id = db.Column(db.Integer, db.ForeignKey('city.city_id'))
    phone = db.Column(db.String(20))
    location = db.Column(Geometry("POINT"), nullable=True)  # Add location column



    #Create A string
  #  def __repr__(self):
 #       return '<Name %r>' % self.name

class Customer(db.Model):
    __tablename__ = 'customer'
    customer_id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer,db.ForeignKey('store.store_id'))
    first_name = db.Column(db.String(45), nullable=False)
    last_name = db.Column(db.String(45), nullable=False)
    email = db.Column(db.String(50), nullable=True)
    address_id = db.Column(db.Integer, db.ForeignKey('address.address_id'))
    active = db.Column(db.Integer())
    #create_date = db.Column(db.Date)
 #   class Category(db.Model):

class Country(db.Model):
    __tablename__ = 'country'
    country_id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(50), nullable=False)
    last_update = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class City(db.Model):
    __tablename__ = 'city'
    city_id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(50), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('country.country_id'), nullable=False)
    last_update = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())



class Store(db.Model):
    __tablename__ = 'store'
    store_id = db.Column(db.Integer, primary_key=True)  # TINYINT in MySQL
    manager_staff_id = db.Column(db.Integer, db.ForeignKey('staff.staff_id'), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('address.address_id'), nullable=False)


class Staff(db.Model):
    __tablename__ = 'staff'
    staff_id = db.Column(db.Integer, primary_key=True)  # TINYINT in MySQL
    first_name = db.Column(db.String(45), nullable=False)
    last_name = db.Column(db.String(45), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('address.address_id'), nullable=False)
    email = db.Column(db.String(50), nullable=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.store_id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)  # TINYINT(1) as Boolean
    username = db.Column(db.String(16), nullable=False, unique=True)
    password = db.Column(db.String(40), nullable=False)  # Hashing recommended in actual use
    last_update = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())



# class Address(db.Model):
#     __tablename__ = 'address'
#     address_id = db.Column(db.Integer, primary_key=True)
#     store_id = db.Column(db.Integer,db.ForeignKey('store.store_id'))
#     first_name = db.Column(db.String(45))
#     last_name = db.Column(db.String(45))
#     email = db.Column(db.String(50))
#     address_id = db.Column(db.Integer, db.ForeignKey('address.address_id'))
#     active = db.Column(db.Integer(1))
#     create_date = db.Column(db.Date)
