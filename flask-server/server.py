from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from models import db, FilmCategory, Film  # Import db from models, and necessary models
from flask_cors import CORS
import logging;
from datetime import datetime, timezone





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
        func.count(Rental.rental_id).label("rented"),
        Film.description
    ).join(Inventory, Inventory.inventory_id == Rental.inventory_id
    ).join(FilmCategory, FilmCategory.film_id == Inventory.film_id
    ).join(Category, Category.category_id == FilmCategory.category_id
    ).join(Film, Film.film_id == FilmCategory.film_id
        ).group_by(Inventory.film_id, Film.title, Category.category_id, Film.description
            ).order_by(func.count(Rental.rental_id).desc()).limit(5).all()
    
    films = []

    for film in film_list:
        films.append({"film_id": film.film_id, "title": film.title,"category_id" :film.category_id, "rented":film.rented, "description" : film.description})

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



@app.route("/searchcustomers", methods=['GET'])
def search_customers():
    from models import FilmCategory, Inventory, Film, Category, Actor, Film_Actor, Customer, Rental  # Import Film model from models.py

    customer_list = db.session.query(
        Customer.customer_id,
        Customer.first_name,
        Customer.last_name,
        func.count(Rental.rental_id).label("count")
    ).outerjoin(Rental, Rental.customer_id == Customer.customer_id
    ).group_by(Customer.customer_id
               ).order_by(Customer.last_name.asc()).all()


    
    customer = []

    for cust in customer_list:
        customer.append({"customer_id": cust.customer_id,
                       "first_name": cust.first_name,
                        "last_name":cust.last_name,
                        "count" : cust.count,

                        })
    return jsonify({'customers': customer})

@app.route("/addcustomers", methods=['POST', 'GET'])
def add_customers():
    from models import Customer, Address, City, Country# Import Film model from models.py

    data = request.json  # Use JSON data from request body


    if request.method == "POST":

            # Check if the city already exists
        
#-----------------------------------------------
        # Check if the address already exists

#----------------------------------------------------------
        existing_country = Country.query.filter_by(country=data['country']).first()
        
        if existing_country:
            country_id = existing_country.country_id  # Ensure country_id is always set
        else:
            new_country = Country(country=data['country'])
            db.session.add(new_country)
            db.session.commit()
            country_id = new_country.country_id  # Get the new city's ID
#-------------------------------------------

        existing_city = City.query.filter_by(city=data['city']).first()
        
        if existing_city:
            city_id = existing_city.city_id  # Use existing city ID
        else:
            new_city = City(city=data['city'], country_id=country_id)
            db.session.add(new_city)
            db.session.commit()
            city_id = new_city.city_id  # Get the new city's ID
#---------------------------------------------------------
        existing_address = Address.query.filter_by(address=data['address'], district=data['district']).first()

        if existing_address:
            new_address = existing_address  # Use existing address ID
        else:
            new_address = Address(address=data['address'], district=data['district'], 
                                  city_id=city_id,
                                  phone=data.get('phone', '000-000-0000'),  # Provide a default phone number
                                    location='POINT(0 0)')  # Provide a placeholder location if required
            db.session.add(new_address)
            db.session.commit()
            address_id = new_address.address_id  # Get the new address ID
#---------------------------------------------------------

        customer = Customer(first_name=data['first_name'], 
                            last_name=data['last_name'], 
                            email=data['email'],
                            address_id=new_address.address_id,
                            store_id= 1 ,
                            active=data.get('active', 1))

        db.session.add(customer)
        db.session.commit()


        return jsonify({
            "success": True,
            "message": "Customer added successfully!",
            "customer": {
                "customer_id": customer.customer_id,
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "count" : 0
            }
        })
    
@app.route("/deletecustomers/<int:customer_id>",methods = ['DELETE'])
def delete_customers(customer_id):
    from models import Customer, Rental
    if request.method == 'DELETE':
        customer = Customer.query.get(customer_id)



        
        if not customer:
            return jsonify({"success": False, "message": "Customer not found"}), 404

        # Delete customer from database
        db.session.query(Rental).filter(Rental.customer_id == customer_id).delete()
        db.session.commit()
        db.session.delete(customer)
        db.session.commit()

        return jsonify({"success": True, "message": "Customer deleted"}), 200

@app.route("/updatecustomers/<int:customer_id>",methods = ['PUT', 'GET'])
def update_customers(customer_id):
    from models import Customer, Address, City, Country
    customer = Customer.query.get(customer_id)
    if not customer:
            return jsonify({"success": False, "message": "Customer not found"}), 404
    
    if request.method == 'GET':
        address = Address.query.get(customer.address_id)
        city = City.query.get(address.city_id)
        country = db.session.get(Country, city.country_id)
        return jsonify({
            "customer_id": customer.customer_id,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "email": customer.email,
            "address": address.address,
            "district": address.district,
            "city": city.city,
            "country": country.country,
            "phone": address.phone
        })
    
    data = request.json

        # Update Country if different
    existing_country = Country.query.filter_by(country=data['country']).first()
    if not existing_country:
        new_country = Country(country=data['country'])
        db.session.add(new_country)
        db.session.commit()
        country_id = new_country.country_id
    else:
        country_id = existing_country.country_id

    # Update City if different
    existing_city = City.query.filter_by(city=data['city'], country_id=country_id).first()
    if not existing_city:
        new_city = City(city=data['city'], country_id=country_id)
        db.session.add(new_city)
        db.session.commit()
        city_id = new_city.city_id
    else:
        city_id = existing_city.city_id

    # Update Address if different
    existing_address = Address.query.filter_by(address=data['address'], district=data['district']).first()
    if not existing_address:
        new_address = Address(
            address=data['address'], 
            district=data['district'], 
            city_id=city_id,
            phone=data.get('phone', '000-000-0000'),  # Provide a default if missing
            location='POINT(0 0)'  # Placeholder
        )
        db.session.add(new_address)
        db.session.commit()
        address_id = new_address.address_id
    else:
            existing_address.phone = data.get('phone', existing_address.phone)  # Keep existing if not provided
            db.session.commit()  # Save changes
            address_id = existing_address.address_id

    # Update Customer Information
    customer.first_name = data['first_name']
    customer.last_name = data['last_name']
    customer.email = data['email']
    customer.address_id = address_id

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Customer updated successfully!",
        "customer": {
            "customer_id": customer.customer_id,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "email": customer.email
        }
    }), 200



@app.route("/rent", methods=["PATCH","POST"])
def rent_movie():
    from models import Customer, Rental  # Import necessary models
    data = request.json
    customer_id = data.get('customer_id')
    film_id = data.get('film_id')

    if not customer_id or not film_id:
        return jsonify({"success": False, "message": "customer_id and film_id are required"}), 400

    try:
        # Find the customer
        customer = db.session.get(Customer, customer_id)
        if not customer:
            return jsonify({"success": False, "message": "Customer not found"}), 404

        # Increment the customer's rental count
        #customer.rented_count = (customer.rented_count or 0) + 1

        # Create a new rental record
        new_rental = Rental(
            customer_id=customer_id,
            inventory_id=film_id,  # Assuming film_id maps to inventory_id
            staff_id=1
            #rental_date=datetime.now(),
            #return_date=None  # Set return_date as needed
        )
        db.session.add(new_rental)

        # Commit changes to the database
        db.session.commit()

        return jsonify({"success": True, "message": "Rental recorded successfully!"}), 200
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        logging.error(f"Error in rent_movie: {str(e)}")  # Log the error
        return jsonify({"success": False, "message": str(e)}), 500

# @app.route("/rent" ,methods = ["PATCH"])
# def rent_movie():
#     from models import Customer, Address, City, Country
#     data = request.json
#     customer_id = data['customer_id']
#     film_id = data['film_id']

#     # Update rented movies count
#     cursor = db.cursor()
#     cursor.execute("UPDATE customer SET rented_count = rented_count + 1 WHERE customer_id = %s", (customer_id,))
#     cursor.execute("INSERT INTO rental (customer_id, film_id, rental_date) VALUES (%s, %s, NOW())", (customer_id, film_id))
#     db.commit()

#     return jsonify({"success": True})

@app.route("/info/<int:customer_id>",methods = ['PUT', 'GET'])
def info_customers(customer_id):
    from models import Customer, Address, City, Country, Rental, Inventory
    customer = Customer.query.get(customer_id)


    if not customer:
            return jsonify({"success": False, "message": "Customer not found"}), 404
    

    #Filters a customers id, name, and rental count based off of their id
    customerData = db.session.query(
        Customer.customer_id,
        Customer.first_name,
        Customer.last_name,
        func.count(Rental.rental_id).label("count")
    ).outerjoin(Rental, Rental.customer_id == Customer.customer_id
    ).group_by(Customer.customer_id
               ).filter(Customer.customer_id == customer.customer_id  
               ).order_by(Customer.last_name.asc()).all()
    


    rental_history = db.session.query(
        Customer.customer_id,
        Customer.first_name,
        Customer.last_name,
        Rental.rental_date,
        Rental.return_date,
        Inventory.film_id,
        func.ifnull(Rental.return_date, "Not Returned").label("status")
    ).join(Rental, Rental.customer_id == Customer.customer_id
    ).join(Inventory, Inventory.inventory_id == Rental.inventory_id
    ).filter(Customer.customer_id == customer_id  
    ).order_by(Rental.rental_date.desc()
    ).all()


    currently_rented = db.session.query(
        Rental.rental_id,
        Rental.rental_date,
        Inventory.film_id
    ).join(Inventory, Inventory.inventory_id == Rental.inventory_id
    ).filter(Rental.customer_id == customer_id, Rental.return_date.is_(None)  
    ).order_by(Rental.rental_date.desc()
    ).all()



    
    if request.method == 'GET':
        address = Address.query.get(customer.address_id)
        city = City.query.get(address.city_id)
        country = Country.query.get(city.country_id)
        rented = customerData[0].count if customerData else 0
        returned = sum(1 for rental in rental_history if rental.return_date is not None)

        rented_movies = [
            {"rental_id": rental.rental_id, "rental_date": rental.rental_date, "film_id": rental.film_id}
            for rental in currently_rented
        ]

        rental_history_list = [
            {"rental_date": rental.rental_date, "return_date": rental.return_date, "film_id": rental.film_id}
            for rental in rental_history
        ]

        

        

        return jsonify({
            "customer_id": customer.customer_id,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "email": customer.email,
            "address": address.address,
            "district": address.district,
            "city": city.city,
            "country": country.country,
            "phone": address.phone,
            "rented": rented,
            "returned": returned,
            "rental_history": rental_history_list,
            "currently_rented": rented_movies

        })
    
    data = request.json

        # Update Country if different
    existing_country = Country.query.filter_by(country=data['country']).first()
    country_id = existing_country.country_id

    # Update City if different
    existing_city = City.query.filter_by(city=data['city'], country_id=country_id).first()
    city_id = existing_city.city_id

    # Update Address if different
    existing_address = Address.query.filter_by(address=data['address'], district=data['district']).first()
    address_id = existing_address.address_id



@app.route("/returnfilm", methods=["PATCH","POST"])
def return_movie():
    from models import Customer, Rental  # Import necessary models
    data = request.json
    customer_id = data.get('customer_id')
    film_id = data.get('film_id')

    if not customer_id or not film_id:
        return jsonify({"success": False, "message": "customer_id and film_id are required"}), 400

    try:
        # Find the customer
        customer = db.session.get(Customer, customer_id)
        if not customer:
            return jsonify({"success": False, "message": "Customer not found"}), 404

        # Increment the customer's rental count
        #customer.rented_count = (customer.rented_count or 0) + 1

        rental = Rental.query.filter_by(customer_id=customer_id, 
                                        return_date=None).first()

        if not rental:
            return jsonify({"success": False, "message": "No active rental found for this movie"}), 404
        rental.return_date = datetime.now(timezone.utc)

        # Commit changes to the database
        db.session.commit()

        return jsonify({"success": True, "message": "Rental recorded successfully!"}), 200
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        logging.error(f"Error in rent_movie: {str(e)}")  # Log the error
        return jsonify({"success": False, "message": str(e)}), 500



if __name__ == "__main__":
    app.run(debug=True)


#films = Category.query.order_by(Category.category_id).all()

    # Convert the results into a list of dictionaries
 #   films_list = [{"category_id": film.category_id, "name": film.name} for film in films]

  #  return jsonify(films_list) 