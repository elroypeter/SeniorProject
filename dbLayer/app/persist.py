from geoalchemy2 import func
from geoalchemy2.types import Geometry
from app import db
from app.models import PreCogRun, Prediction
import geojson, os, codecs
import pandas as pd


# Feed in PreCogRuns table query result
def geojsonConvert_PreCogRuns(queryResult):
	collection = []
	print(queryResult.size)
	for data in queryResult.itertuples(index=True, name='Pandas'):
		id = geojson.Point(( data[1] , data[2] ))
		feature = geojson.Feature(geometry= point , properties={"certainty": data.certainty} )
		collection.append(feature)
	dump = geojson.dumps(geojson.FeatureCollection(collection))
	print(dump)
	return dump


# Feed in a Predictions table query result
def geojsonConvert_Predictions(queryResult):
	collection = []
	print(queryResult.size)
	for data in queryResult.itertuples(index=True, name='Pandas'):
		point = geojson.Point(( data[1] , data[2] ))
		feature = geojson.Feature(geometry= point , properties={"certainty": data.certainty} )
		collection.append(feature)
	dump = geojson.dumps(geojson.FeatureCollection(collection))
	print(dump)
	return dump


# Persist a specific precog run from db
def persistRun(runID, filename):
	result = db.session.query( func.ST_X(Prediction.location), func.ST_Y(Prediction.location), Prediction.certainty ).filter(Prediction.precogrun == runID)
	data = pd.read_sql( result.statement , result.session.bind)
	geojson = geojsonConvert_Predictions(data)
	file_path = os.path.join("/app/app/static", filename + ".geojson")
	with codecs.open( file_path, 'w', encoding="utf8") as fo:
		fo.write(geojson)


# Persist all available precog runs from the db
def persist_all():
	return "success"


def persist_available_runs():
	result = db.session.query(PreCogRun)
	data = pd.read_sql( result.statement , result.session.bind)
	geojson = geojsonConvert_PreCogRuns(data)
	file_path = os.path.join("/app/app/static", "precogruns.json")
	with codecs.open( file_path, 'w', encoding="utf8") as fo:
		fo.write(geojson)


persistRun("6", "6")
