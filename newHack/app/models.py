from app import db, app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
class Admin(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text_question = db.Column(db.String(100), nullable=False)

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text_answer = db.Column(db.String(100), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    count_of_answer = db.Column(db.Integer)
@login.user_loader
def load_user(id):
    return Admin.query.get(int(id))

