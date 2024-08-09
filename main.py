from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random


app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)
    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

        # #Method 1. 
        # dictionary = {}
        # # Loop through each column in the data record
        # for column in self.__table__.columns:
        #     #Create a new dictionary entry;
        #     # where the key is the name of the column
        #     # and the value is the value of the column
        #     dictionary[column.name] = getattr(self, column.name)
        # return dictionary
        
        #Method 2. Altenatively use Dictionary Comprehension to do the same thing.




with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/random")
def get_random_cafe():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    random_cafe = random.choice(all_cafes)
    #Simply convert the random_cafe data record to a dictionary of key-value pairs. 
    return jsonify(cafe=random_cafe.to_dict())


@app.route("/all",methods=["GET"])
def all_cafes():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    return jsonify(cafe=[cafe.to_dict() for cafe in all_cafes])
    
@app.route("/search",methods=["GET"])
def search_cafes():
    param=request.args.get("loc")
    result = db.session.execute(db.select(Cafe).where(Cafe.location == param))
    cafe=result.scalars().all()
    if cafe:
        return jsonify(cafes=[loc.to_dict() for loc in cafe])
    else:
        return jsonify(error={"NOT FOUND":"ENTERED LOCATION IS NOT SERVICABLE"})
        
    
@app.route("/add", methods=["POST"])
def post_new_cafe():
    api_key=request.args.get("api_key")
    if api_key == "TopSecretKey":
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
        db.session.commit()
        return jsonify(response={"success": "Successfully added the new cafe."})
    else:
        return jsonify(error={"FAILED":"sorry you are not allowed to Post,Make sure you have correct api_key"}),403

# remember the loc parameter should be same in postman and in code because we previosly got location as loc
# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def price_change(cafe_id):
    cafe= db.get_or_404(Cafe,cafe_id)
    new_price=request.args.get("new_price")
    if cafe:
        cafe.coffee_price=new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully changed the coffee price."}),200
    else:
        return jsonify(error={"NOT FOUND":"Sorry there was an issue updating the price"}),404

# HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def cafe_delete(cafe_id):
    api_key=request.args.get("api_key")
    if api_key == 'TopSecretKey':
        try:
            cafe= db.get_or_404(Cafe,cafe_id)
            if cafe: #this helped in solving the error
                db.session.delete(cafe)
                db.session.commit()
                return jsonify(response={"success": f"Successfully deleted the Cafe:[{cafe.name}]"}),200
        except :
            return jsonify(response={"NOTFOUND": "Cafe with that id was not found"}),404

    else:
        return jsonify(error={"FAILED":"sorry you are not allowed to make this request,Make sure you have correct api_key"}),403

if __name__ == '__main__':
    app.run(debug=True)
