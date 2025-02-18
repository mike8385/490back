
from flask_sqlalchemy import SQLAlchemy

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
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.inventory_id'))

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


    #Create A string
  #  def __repr__(self):
 #       return '<Name %r>' % self.name