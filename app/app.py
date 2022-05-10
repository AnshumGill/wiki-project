from flask import Flask,request,jsonify
from logging.config import dictConfig
from sqlalchemy.exc import SQLAlchemyError, NoReferenceError
from models import db,Country,Continent,City
import logging
from celery import Celery
from celery.utils.log import get_task_logger
import time

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

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]="mysql+pymysql://root:password@db:3306/wiki"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]="False"
db.app=app
db.init_app(app)
db.create_all()

app.config.update(
    broker_url="amqp://guest:guest@broker_rabbitmq",
    result_backend="db+mysql://root:password@db:3306/celery"
)

celery=make_celery(app)
logger=get_task_logger(__name__)

obj_map={
    'continent':Continent,
    'country':Country,
    'city':City
}

@celery.task(name="app.celeryInsert")
def celeryInsert(type,data):
    t=time.process_time()
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

@celery.task(name="app.celeryDelete")
def celeryDelete(type,name):
    t=time.process_time()
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

@celery.task(name="app.celeryUpdateContinent")
def celeryUpdateContinent(name,data):
    t=time.process_time()
    try:
        obj=Continent.query.filter_by(name=name).first()
        setattr(obj,'population',data['population'])
        setattr(obj,'area',data['area'])
        time.sleep(10)
        db.session.commit()
        logger.info(f"Execution of task used {time.process_time() - t} seconds")
        return True
    except SQLAlchemyError as e:
        logging.error(f"Error occurred while updating record, {e}")
        logger.info(f"Execution of task used {time.process_time() - t} seconds")
        return False

@celery.task(name="app.celeryUpdateCountry")
def celeryUpdateCountry(name,data):
    t=time.process_time()
    try:
        obj=Country.query.filter_by(name=name).first()
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

@celery.task(name="app.celeryUpdateCity")
def celeryUpdateCity(name,data):
    t=time.process_time()
    try:
        obj=Country.query.filter_by(name=name).first()
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

@app.route("/<type>",methods=['GET'])
def getRows(type):
    resp=[obj.get() for obj in obj_map[type].query.all()]
    if(len(resp)>0):
        return (jsonify(resp),200)
    else:
        return ('',204)

@app.route("/<type>",methods=["POST"])
def insertRecords(type):
    resp=celeryInsert.delay(type,request.json)
    return (f"Request with id {resp.id} received successfully.",200)

@app.route("/<type>/<name>",methods=["DELETE"])
def deleteRecord(type,name):
    resp=celeryDelete.delay(type,name)
    return (f"Request with id {resp.id} received successfully.",200)

@app.route("/<type>/<name>",methods=["PUT"])
def updateRecord(type,name):
    if(type=="continent"):
        resp=celeryUpdateContinent.delay(name,request.json)
    elif(type=="country"):
        resp=celeryUpdateCountry.delay(name,request.json)
    elif(type=="city"):
        resp=celeryUpdateCity.delay(name,request.json)
    
    return (f"Request with id {resp.id} received successfully.",200)
    
@app.route('/task/<id>',methods=["GET"])
def getTaskDetails(id):
    task=celery.AsyncResult(id)
    resp={
        'id':task.id,
        'state':task.state,
        'success':task.get()
    }

    return (jsonify(resp),200)

if (__name__=="__main__"):
    app.run(debug=False,host="0.0.0.0",port=8080)
