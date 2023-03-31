import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smartphones.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set upload folder and allowed extensions for images
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}

# Initialize SQLAlchemy database
db = SQLAlchemy(app)


# Define Smartphone model
class Smartphone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    screen_diagonal = db.Column(db.Float, nullable=False)
    cameras_amount = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Smartphone {self.name}>'


# Define helper function to check file extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# Define routes
@app.route('/smartphones', methods=['GET'])
def get_smartphones():
    smartphones = Smartphone.query.all()
    return jsonify([smartphone.__dict__ for smartphone in smartphones])


@app.route('/smartphones/<int:smartphone_id>', methods=['GET'])
def get_smartphone(smartphone_id):
    smartphone = Smartphone.query.get_or_404(smartphone_id)
    return jsonify(smartphone.__dict__)


@app.route('/smartphones', methods=['POST'])
def add_smartphone():
    smartphone_data = request.form.to_dict()
    image = request.files['image']
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        smartphone_data['image'] = filename
    smartphone = Smartphone(**smartphone_data)
    db.session.add(smartphone)
    db.session.commit()
    return '', 201


@app.route('/smartphones/<int:smartphone_id>', methods=['PUT'])
def update_smartphone(smartphone_id):
    smartphone = Smartphone.query.get_or_404(smartphone_id)
    smartphone_data = request.form.to_dict()
    image = request.files.get('image')
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        smartphone_data['image'] = filename
    for key, value in smartphone_data.items():
        setattr(smartphone, key, value)
    db.session.commit()
    return '', 204


@app.route('/smartphones/<int:smartphone_id>', methods=['DELETE'])
def delete_smartphone(smartphone_id):
    smartphone = Smartphone.query.get_or_404(smartphone_id)
    db.session.delete(smartphone)
    db.session.commit()
    return '', 204


@app.route('/smartphones/compare', methods=['POST'])
def compare_smartphones():
    smartphone_ids = request.get_json()
    smartphones = Smartphone.query.filter(Smartphone.id.in_(smartphone_ids)).all()
    return jsonify([smartphone.__dict__ for smartphone in smartphones])


# Run app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
