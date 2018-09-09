"""
This is models.py the main file for SQAlchemy to make the database from.
Here all the tables, columns, and defualt values are defind and setup.
"""
# pylint: disable=R0903
from datetime import datetime
from app import db, ma


class User(db.Model):
    """User is the table to store users"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True, unique=True, nullable=False)
    hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    firstname = db.Column(db.String(32), unique=False, nullable=False)
    lastname = db.Column(db.String(32), unique=False, nullable=False)
    country = db.Column(db.String(32), unique=False, nullable=False)
    state = db.Column(db.String(32), unique=False, nullable=False)
    city = db.Column(db.String(32), unique=False, nullable=False)
    avatar = db.Column(db.String(128), unique=False, nullable=True)

    item = db.relationship('Item', backref='owner', \
        lazy='dynamic', primaryjoin="User.id == Item.user_id")
    bought_item = db.relationship('Item', backref='buyer', \
        lazy='dynamic', primaryjoin="User.id == Item.buying_user")
    notification = db.relationship('Notification', backref='seller', \
        lazy='dynamic', primaryjoin="User.id == Notification.user_id")

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Item(db.Model):
    """Item is the table to store Items"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    price = db.Column(db.Integer)
    title = db.Column(db.String(32), unique=False, nullable=False)
    description = db.Column(db.String(256), unique=False, nullable=False)
    photo = db.Column(db.String(128), unique=False, nullable=True)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    category = db.Column(db.String(32), unique=False, nullable=False)
    sold = db.Column(db.Boolean, default=False)
    buying_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    country = db.Column(db.String(32), unique=False, nullable=False)
    state = db.Column(db.String(32), unique=False, nullable=False)
    city = db.Column(db.String(32), unique=False, nullable=False)
    item = db.relationship('Notification', backref='notification', \
    lazy='dynamic', primaryjoin="Item.id == Notification.item_id")

    def __repr__(self):
        return '<Item {}>'.format(self.title)


class Notification(db.Model):
    """Notification is the table to store Notifications"""
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return '<Notification {}>'.format(self.id)


class ItemSchema(ma.ModelSchema):
    """for flask_marshmallow to be able to jsonify Items"""
    class Meta:
        """let model be the Item class"""
        model = Item
