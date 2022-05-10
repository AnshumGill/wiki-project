from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import NoReferenceError

# Creating instance of SQLAlchemy. This is imported in app.py
db=SQLAlchemy()

# Continent Model
class Continent(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),unique=True,nullable=False)
    population=db.Column(db.Integer)
    area=db.Column(db.Integer)
    countries=db.relationship('Country',backref=db.backref('continent',lazy=True))

    # Constructor
    def __init__(self,name,population,area):
        self.name=name
        self.population=population
        self.area=area

    # Method to convert object to dictionary
    def get(self):
        return {
            'name':self.name,
            'population':self.population,
            'area':self.area
        }

# Country Model
class Country(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),unique=True,nullable=False)
    population=db.Column(db.Integer)
    area=db.Column(db.Integer)
    hospitals_count=db.Column(db.Integer)
    national_parks_count=db.Column(db.Integer)
    continent_id=db.Column(db.Integer,db.ForeignKey('continent.id'),nullable=False)
    cities=db.relationship('City',backref=db.backref('country',lazy=True))

    # Constructor
    def __init__(self,name,population,area,hospitals_count,national_parks_count,continent):
        self.name=name
        self.population=population
        self.area=area
        self.hospitals_count=hospitals_count
        self.national_parks_count=national_parks_count
        self.continent_id=Continent.query.filter_by(name=continent).first().id
        if(self.continent_id == None):
            raise NoReferenceError("The continent name provided cannot be found")

    # Method to convert object to dictionary
    def get(self):
        return {
            'name':self.name,
            'population':self.population,
            'area':self.area,
            'hospitals_count':self.hospitals_count,
            'national_parks_count':self.national_parks_count,
            'continent':Continent.query.get(self.continent_id).name
        }

# City Model
class City(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),unique=True,nullable=False)
    population=db.Column(db.Integer)
    area=db.Column(db.Integer)
    road_count=db.Column(db.Integer)
    tree_count=db.Column(db.Integer)
    country_id=db.Column(db.Integer,db.ForeignKey('country.id'),nullable=False)

    # Constructor
    def __init__(self,name,population,area,road_count,tree_count,country):
        self.name=name
        self.population=population
        self.area=area
        self.road_count=road_count
        self.tree_count=tree_count
        self.country_id=Country.query.filter_by(name=country).first().id
        if(self.country_id == None):
            raise NoReferenceError("The country name provided cannot be found")

    # Method to convert object to dictionary
    def get(self):
        return {
            'name':self.name,
            'population':self.population,
            'area':self.area,
            'road_count':self.road_count,
            'tree_count':self.tree_count,
            'continent':Country.query.get(self.country_id).name
        }
