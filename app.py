from flask import Flask, request, flash, url_for, redirect, render_template 
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///delicious.sqlite3'
app.config['SECRET_KEY'] = "random string"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

# Initialize the SQLAlchemy object
db = SQLAlchemy(app)


class Food(db.Model):
    id = db.Column('food_id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Float)
    availability = db.Column(db.Boolean)

    def __init__(self, name, price,availability):
        self.name = name
        self.price = price
        self.availability =availability

@app.route('/')
def show_all():
    Foods = Food.query.all()
    return render_template('show_all.html', Foods=Foods)


@app.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        if request.headers.get('content-type') == 'application/json':
            data = request.get_json()
            print(data)
            if not data.get('name') or not data.get('price') or not data.get('availability'):
                flash('Please enter all the fields', 'error')
            else:
                food = Food(data.get('name'), data.get('price'), data.get('availability'))
                db.session.add(food)
                db.session.commit()

                flash('Record was successfully added')
                return redirect(url_for('show_all'))
        else:
            flash('Invalid request content type. Expected application/json.', 'error')
    return render_template('new.html')

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    if request.method=='POST':
        name = request.form['name']
        price = request.form['price']
        availability = request.form['availability']
        food = Food.query.filter_by(id=id).first()
        food.name = name
        food.price = price
        food.availability = availability
        print(food)
        db.session.add(food)
        db.session.commit()
        return redirect("/")
        
    food = Food.query.filter_by(id=id).first()
    return render_template('update.html', food=food)
 

@app.route('/delete/<int:id>')
def delete(id):
    food= Food.query.filter_by(id=id).first()
    db.session.delete(food)
    db.session.commit()
    return redirect("/")

if __name__ == '__main__':
   with app.app_context():
    db.create_all()
    app.run(debug=True)
