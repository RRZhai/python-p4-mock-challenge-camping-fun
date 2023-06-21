from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    # Add relationship
    signups = db.relationship('Signup', back_populates='activity')
    campers = association_proxy('signups', 'camper', creator=lambda camper:Signup(camper=camper))

    # Add serialization rules
    serialize_only = ('id', 'name', 'difficulty')

    def __repr__(self):
        return f'<Activity {self.id}: {self.name}>'


class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    # Add relationship
    signups = db.relationship('Signup', back_populates='camper')
    # Add serialization rules
    activity = association_proxy('signups', 'activity', creator=lambda activity:Signup(activity=activity))
    serialize_only = ('id', 'name', 'age')

    # Add validation
    @validates('name')
    def validate_name(self, key, name):
        if not name:
            raise TypeError(f'Camper must has a name.')
        return name
    
    @validates('age')
    def validate_age(self, key, age):
        if 8 > age or age > 18:
            raise TypeError(f'Camper must be 8 to 18 years old!')
        return age
    
    def __repr__(self):
        return f'<Camper {self.id}: {self.name}>'
    
    # def as_dict(self):
    #     return {
    #         'id': self.id,
    #         'name': self.name,
    #         'age': self.age,
    #         'signup': self.signup
    #     }


class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)

    # Add relationships
    camper_id = db.Column(db.Integer, db.ForeignKey('campers.id'))
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))
    camper = db.relationship('Camper', back_populates='signups')
    activity = db.relationship('Activity', back_populates='signups')
    # Add serialization rules
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    serialize_only = ('id', 'time', 'camper_id', 'activity_id')

    # Add validation
    @validates('time')
    def validate_time(self, key, time):
        if 0 > time or time > 23:
            raise TypeError(f'time must be between 0 to 23')
        return time
    
    def __repr__(self):
        return f'<Signup {self.id}>'


# add any models you may need.
