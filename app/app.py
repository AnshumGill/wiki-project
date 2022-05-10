from flask import Flask,request,jsonify
from logging.config import dictConfig
from sqlalchemy.exc import SQLAlchemyError, NoReferenceError
from models import db,Country,Continent,City
import logging
from celery import Celery
from celery.utils.log import get_task_logger
import time

# Make instance of Celery
def make_celery(app):
    celery = Celery(
        'app',
        result_backend=app.config['result_backend'],
        broker_url=app.config['broker_url']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

# Log Configuration
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '%(asctime)s %(levelname)s %(message)s',
    }},
    'handlers': {
    	'wsgi': {
	        'class': 'logging.StreamHandler',
	        'stream': 'ext://flask.logging.wsgi_errors_stream',
	        'formatter': 'default'
	    }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

# Flask app definition and configuration
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]="mysql+pymysql://root:password@db:3306/wiki"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]="False"
db.app=app
# Initializing DB now as it was created in models
db.init_app(app)
# Creating tables if not exists
db.create_all()

# Updating app.config with Celery configuration 
app.config.update(
    broker_url="amqp://guest:guest@broker_rabbitmq",
    result_backend="db+mysql://root:password@db:3306/celery"
)

# Celery instance
celery=make_celery(app)
# For logging inside celery tasks
logger=get_task_logger(__name__)

# Mapping of <type> with Object
obj_map={
    'continent':Continent,
    'country':Country,
    'city':City
}

# Celery Task for insertion
@celery.task(name="app.celeryInsert")
def celeryInsert(type,data):
    t=time.process_time()
    # List comprehension to get Object using map and pass the data dictionary into it's constructor
    objects=[obj_map[type](**obj) for obj in data] 
    try:
        db.session.add_all(objects)
        db.session.commit()    
        logger.info(f"Execution of task used {time.process_time() - t} seconds")
        return True
    except SQLAlchemyError as e:
        logging.error(f"Error occurred while inserting records, {e}")
        logger.info(f"Execution of task used {time.process_time() - t} seconds")
        return False

# Celery Task for Deletion
@celery.task(name="app.celeryDelete")
def celeryDelete(type,name):
    t=time.process_time()
    # Getting specific element for deletion
    obj=obj_map[type].query.filter_by(name=name).first()
    try:
        db.session.delete(obj)
        db.session.commit()    
        logger.info(f"Execution of task used {time.process_time() - t} seconds")
        return True
    except SQLAlchemyError as e:
        logging.error(f"Error occurred while deleting record, {e}")
        logger.info(f"Execution of task used {time.process_time() - t} seconds")
        return False

# Celery Task for Updating Continent
@celery.task(name="app.celeryUpdateContinent")
def celeryUpdateContinent(name,data):
    t=time.process_time()
    try:
        # Getting Object 
        obj=Continent.query.filter_by(name=name).first()
        # Setting it's attribute to data dictionary 
        setattr(obj,'population',data['population'])
        setattr(obj,'area',data['area'])
        db.session.commit()
        logger.info(f"Execution of task used {time.process_time() - t} seconds")
        return True
    except SQLAlchemyError as e:
        logging.error(f"Error occurred while updating record, {e}")
        logger.info(f"Execution of task used {time.process_time() - t} seconds")
        return False

# Celery Task for Updating Country
@celery.task(name="app.celeryUpdateCountry")
def celeryUpdateCountry(name,data):
    t=time.process_time()
    try:
        # Getting Object
        obj=Country.query.filter_by(name=name).first()
        # Setting it's attribute to data dictionary 
        setattr(obj,'population',data['population'])
        setattr(obj,'area',data['area'])
        setattr(obj,'hospitals_count',data['hospitals_count'])
        setattr(obj,'national_parks_count',data['national_parks_count'])
        continent=Continent.query.filter_by(name=data['continent']).first()
        if(continent == None):
            raise NoReferenceError("The continent name provided cannot be found")
        setattr(obj,'continent_id',continent.id)
        db.session.commit()
        logger.info(f"Execution of task used {time.process_time() - t} seconds")
        return True
    except SQLAlchemyError as e:
        logging.error(f"Error occurred while updating record, {e}")
        logger.info(f"Execution of task used {time.process_time() - t} seconds")
        return False

# Celery Task for Updating City
@celery.task(name="app.celeryUpdateCity")
def celeryUpdateCity(name,data):
    t=time.process_time()
    try:
        # Getting Object
        obj=Country.query.filter_by(name=name).first()
        # Setting it's attribute to data dictionary 
        setattr(obj,'population',data['population'])
        setattr(obj,'area',data['area'])
        setattr(obj,'road_count',data['road_count'])
        setattr(obj,'tree_count',data['tree_count'])
        country=Country.query.filter_by(name=data['country']).first()
        if(country == None):
            raise NoReferenceError("The country name provided cannot be found")
        setattr(obj,'country_id',country.id)
        db.session.commit()
        logger.info(f"Execution of task used {time.process_time() - t} seconds")
        return True
    except SQLAlchemyError as e:
        logging.error(f"Error occurred while updating record, {e}")
        logger.info(f"Execution of task used {time.process_time() - t} seconds")
        return False

# GET API for fetching all records as JSON
@app.route("/<type>",methods=['GET'])
def getRows(type):
    resp=[obj.get() for obj in obj_map[type].query.all()]
    if(len(resp)>0):
        return (jsonify(resp),200)
    else:
        return ('',204)

# GET API for fetching specifc record as JSON
@app.route("/<type>/<name>",methods=['GET'])
def getRow(type,name):
    obj=obj_map[type].query.filter_by(name=name).first()
    if(obj):
        obj=obj.get()
        return (jsonify(obj),200)
    else:
        return ('',204)


# POST API for inserting records passed as JSON
@app.route("/<type>",methods=["POST"])
def insertRecords(type):
    resp=celeryInsert.delay(type,request.json)
    return (f"Request with id {resp.id} received successfully.",200)

# POST API for deleting record passed as JSON
@app.route("/<type>/<name>",methods=["DELETE"])
def deleteRecord(type,name):
    resp=celeryDelete.delay(type,name)
    return (f"Request with id {resp.id} received successfully.",200)

# POST API for updating records passed as JSON
@app.route("/<type>/<name>",methods=["PUT"])
def updateRecord(type,name):
    if(type=="continent"):
        resp=celeryUpdateContinent.delay(name,request.json)
    elif(type=="country"):
        resp=celeryUpdateCountry.delay(name,request.json)
    elif(type=="city"):
        resp=celeryUpdateCity.delay(name,request.json)
    
    return (f"Request with id {resp.id} received successfully.",200)
    
# GET API to return status of task id specified
@app.route('/task/<id>',methods=["GET"])
def getTaskDetails(id):
    task=celery.AsyncResult(id)
    resp={
        'id':task.id,
        'state':task.state,
        'success':task.get()
    }

    return (jsonify(resp),200)

# Main function to execute Flask Server
if (__name__=="__main__"):
    app.run(debug=False,host="0.0.0.0",port=8080)
