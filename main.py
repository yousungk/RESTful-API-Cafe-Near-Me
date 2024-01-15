from flask import Flask, jsonify, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random", methods=["get"])
def get_random_cafe():
    row_count = db.session.query(Cafe).count()
    row = random.randint(1, row_count + 1)
    cafe = db.session.query(Cafe).filter_by(id=row).first()
    # Use jsonify to turn data into JSON format
    return jsonify(name=cafe.name)


@app.route("/all")
def get_all():
    cafes = db.session.execute(db.select(Cafe).order_by(Cafe.name))
    all_cafes = cafes.scalars().all()
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])


@app.route("/search")
def find_cafe():
    loc = request.args.get("loc")
    cafes = db.session.execute(db.select(Cafe).where(Cafe.location == loc))
    cafes = cafes.scalars().all()
    if cafes:
        return jsonify(cafes=[cafe.to_dict() for cafe in cafes])
    else:
        empty = {
            "Not Found": "Sorry, we don't have that cafe"
        }
        return jsonify(error= empty), 404


# HTTP POST - Create Record
@app.route("/add", methods=["post"])
def add_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.sesssion.commit()
    return jsonify(response= {"success": "Successfully added the new cafe."}), 200


@app.errorhandler(404)
def invalid_route(e):
    return jsonify(error={'Not found': 'Sorry a cafe with that id was not found in the database.'}), 400


# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<cafe_id>", methods=["patch"])
def update_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.session.get(Cafe, cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price!"}), 200
    else:
        return {{ url_for("invalid_route") }}


# HTTP DELETE - Delete Record
@app.route("/report-closed/<cafe_id>", methods=["delete"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api-key")
    if api_key == "TopSecretAPIKey":
        cafe = db.get_or_404(Cafe, cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200
        else:
            return {{ url_for("invalid_route") }}
    else:
        return jsonify(error= {"forbidden": 'Sorry you are now allowed to remove data from database.'}), 403


if __name__ == '__main__':
    app.run(debug=True)
