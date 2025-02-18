from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime
from models import db, FilmCategory, Film  # Import db from models, and necessary models
from flask_cors import CORS




app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:123barreca321@localhost/sakila"



#Initalize the database
db.init_app(app)


CORS(app)


@app.route("/topfilms", methods=['GET'])
def top_films():
    from models import FilmCategory, Inventory, Film, Category, Rental  # Import Film model from models.py

    film_list = db.session.query(
        Inventory.film_id, 
        Film.title, 
        Category.category_id, 
        func.count(Rental.rental_id).label("rented")
    ).join(Inventory, Inventory.inventory_id == Rental.inventory_id
    ).join(FilmCategory, FilmCategory.film_id == Inventory.film_id
    ).join(Category, Category.category_id == FilmCategory.category_id
    ).join(Film, Film.film_id == FilmCategory.film_id
        ).group_by(Inventory.film_id, Film.title, Category.category_id
            ).order_by(func.count(Rental.rental_id).desc()).limit(5).all()
    
    films = []

    for film in film_list:
        films.append({"film_id": film.film_id, "title": film.title,"category_id" :film.category_id, "rented":film.rented})

    return jsonify({'films': films})

@app.route("/topactors", methods=['GET'])
def top_actors():
    from models import Actor, Inventory, Film, Film_Actor, Rental  # Import Film model from models.py

    subquery = db.session.query(
        Film_Actor.actor_id
    ).group_by(Film_Actor.actor_id
               ).order_by(func.count(Film_Actor.actor_id
    ).desc()).limit(5).subquery()

    
    actor_list = db.session.query(

        #Film.film_id, 
        func.group_concat(func.distinct(Film.title)).label('titles'), 
        func.count(Rental.rental_id).label("rented"),
        Actor.first_name, Actor.last_name, Actor.actor_id

    ).join(Film_Actor, Film_Actor.actor_id == Actor.actor_id
    ).join(Film, Film.film_id == Film_Actor.film_id
    ).join(Inventory, Inventory.film_id == Film.film_id
    ).join(Rental, Rental.inventory_id == Inventory.inventory_id
        ).filter(Actor.actor_id.in_(subquery)
        ).group_by(Actor.actor_id
            ).order_by(func.count(Rental.rental_id).desc()
                       ).limit(5).all()
    
    actors = []

    for actor in actor_list:
        actors.append({
                        #"film_id": actor.film_id,
                        "titles": actor.titles.split(','), 
                        "rented": actor.rented,
                        "first_name": actor.first_name,
                        "last_name": actor.last_name,
                        "actor_id" : actor.actor_id
                        })
    

    return jsonify({'actors': actors})

@app.route("/searchfilms", methods=['GET'])
def search_films():
    from models import FilmCategory, Inventory, Film, Category, Actor, Film_Actor  # Import Film model from models.py

    film_list = db.session.query(
        Film.film_id,
        Film.title,
        func.group_concat(func.distinct(Category.name).op('ORDER BY')(Category.name), ', ').label("categories"),
        func.group_concat(func.distinct(func.concat(Actor.first_name, ' ', Actor.last_name)).op('ORDER BY')(Actor.first_name), ', ').label("actors"),
        Film.description
    ).join(FilmCategory, FilmCategory.film_id == Film.film_id
    ).join(Category, Category.category_id == FilmCategory.category_id
    ).join(Film_Actor, Film_Actor.film_id == Film.film_id  # Fix to join Film_Actor directly to Film.film_id
    ).join(Actor, Actor.actor_id == Film_Actor.actor_id
    ).group_by(Film.film_id, Film.title, Film.description).all()


    
    films = []

    for film in film_list:
        films.append({"film_id": film.film_id,
                       "title": film.title,
                        "category_name":film.categories,
                        "actors" : film.actors,
                        "description" : film.description
                        })

    return jsonify({'films': films})


if __name__ == "__main__":
    app.run(debug=True)


#films = Category.query.order_by(Category.category_id).all()

    # Convert the results into a list of dictionaries
 #   films_list = [{"category_id": film.category_id, "name": film.name} for film in films]

  #  return jsonify(films_list) 