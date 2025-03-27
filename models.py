from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    security_question = db.Column(db.String(255), nullable=False)
    security_answer = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<User {self.name}>"

    @classmethod
    def check_email_exists(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def check_security_answer(cls, email, answer):
        user = cls.query.filter_by(email=email).first()
        return user and user.security_answer == answer

    @classmethod
    def create(cls, name, email, password, security_question, security_answer):
        new_user = cls(name=name, email=email, password=password,
                       security_question=security_question, security_answer=security_answer)
        db.session.add(new_user)
        db.session.commit()
