from app import db
from app.models import Prediction, Incident
from flask_sqlalchemy import SQLAlchemy
import os
import datetime
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import make_regression
from sqlalchemy import and_
from sqlalchemy import *
from sqlalchemy import func
import time
from sklearn import *
import sklearn

def runStats():
        curDT = datetime.datetime.now() 
        
        years = [2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]
        months = range(1,13)
        days = range(1, 366)
        weekdays = range(1,7)
        originLat = float(os.environ['LATORG'])
        originLong = float(os.environ['LONORG'])
        limitLat = float(os.environ['LATSTOP'])
        limitLong = float(os.environ['LONSTOP'])
        bbsize = float(os.environ['BBSIZE'])
        bbsize=0.007
        NSBoxes = ( originLat - limitLat ) / bbsize
        EWBoxes = ( originLong - limitLong ) / bbsize
        crimeCounts = []
        boxes = []
        #X, y = make_regression(n_features=4, n_informative=4,random_state=42, shuffle=False)
        NSBoxes = ( originLat - limitLat ) / bbsize
        EWBoxes = ( originLong - limitLong ) / bbsize
        crimeCounts = []
        boxes = []
        totalCrimes=0
        j =0
        maxCrimes = 0
        start = time.time()
        for x in np.arange(0, np.absolute(NSBoxes)):
                # X loop
                for y in np.arange(0, np.absolute(EWBoxes)):
                    j+=1
                    p1x = originLat - (x*bbsize)
                    p1y = originLong + (y*bbsize)
                    p2x = originLat - (x*bbsize)  - bbsize
                    p2y = originLong + (y*bbsize)
                    p3x = originLat - (x*bbsize) - bbsize
                    p3y = originLong + (y*bbsize) + bbsize
                    p4x = originLat - (x*bbsize)
                    p4y = originLong + (y*bbsize) + bbsize
                    # Create a selection box to get all crimes in a certain region
                    box = "POLYGON((" + str(p1x) + " " + str(p1y) + ", " + str(p2x) + " " + str(p2y) + ", " + str(p3x) + " " + str(p3y) \
                            + ", " + str(p4x) + " " + str(p4y) + ", " + str(p1x) + " " + str(p1y) +  "))"
                    x = ((originLat - (x*bbsize)) + (originLat - (x*bbsize)  - bbsize))/ 2
                    y = ((originLong + (y*bbsize)) + (originLong + (y*bbsize) + bbsize))/ 2
                    print("box number ", j)
                    print("max count ", maxCrimes/15)
                    print("total crimes ",totalCrimes)
                    boxResult = db.session.query(Incident).filter(Incident.location.contained(box))
                    if(boxResult.count()==0):
                        continue
                    for year in years:
                        yearResult = boxResult.filter(Incident.year==year)
                        for day in days:
                                
                            
                            # Y loop

                            #1310 max per year
                            #result = db.session.query(Incident).filter(and_(Incident.location.contained(box),Incident.year==year))#,func.extract('month',Incident.date)==month))#, Incident.date.type.python_type.month==month)).count()
                            #result = db.session.query(Incident).filter(Incident.location.contained(box)).filter(Incident.year==year).filter(func.extract('month',Incident.date)==month)
                            #result = db.session.query(Incident).filter(and_((Incident.year==year),(func.extract('month',Incident.date)==month),Incident.FBIcode=="06",Incident.location.contained(box)))
                            #print("db says month is ",result[0].date.type.python_type.month)
                            dayResult = yearResult.filter(and_(func.extract('day',Incident.date)==day),Incident.FBIcode=="06")
                            count = dayResult.count()
                            #if count>0:
                                #print("db says month is ",result[0].date.month)
                                #print("python says month is ", month)
    #                        if result==0:
    #                            continue
                            #print(Incident.date)

                            boxes.append([x,y,year,day])
                            crimeCounts.append(count/15)
                            if count>maxCrimes:
                                maxCrimes=count
#                            print("maxcrimes so far is ",maxCrimes)
#                            print("box number ", j)
#                            print("number of crimes is ")
#                            print(count/15)
#                            print("year is ", year, "day is ", day)
                            totalCrimes= totalCrimes + count
#                            print("total crimes ", totalCrimes)
#                            
#                        current = time.time()
                        #print("time remaining: ",(((current-start)/totalCrimes)*6600000)-(current-start))
                        



        # Run stats over the array, most likely just find max for normalization heat map
        #maxCrimes = max(crimeCounts)
        regr = RandomForestRegressor()
        features = np.array(boxes[:int(len(boxes)/2)])
        output = np.array(crimeCounts[:int(len(crimeCounts)/2)])
        testFeatures = np.array(boxes[int(len(boxes)/2):])
        testOutput = np.array(crimeCounts[int(len(crimeCounts)/2):])
        regr.fit(features, output)
        regr.predict(testFeatures)
        variance = sklearn.metrics.explained_variance_score(testOutput, regr.predict(testFeatures), sample_weight=None, multioutput='uniform_average')
        print("variance ", variance)
        print("score ", regr.score(testFeatures,testOutput))

        countIndex = 0
    
#        for x in np.arange(0, np.absolute(NSBoxes)):
#                # X loop
#                for y in np.arange(0, np.absolute(EWBoxes)):
#                    for year in years:
#                        # Y loop
#                        # Create predictions for each grid location
#                        # Create central point
#                        x = ((originLat - (x*bbsize)) + (originLat - (x*bbsize)  - bbsize))/ 2
#                        y = ((originLong + (y*bbsize)) + (originLong + (y*bbsize) + bbsize))/ 2
#                        pred = Prediction()
#                        predic = regr.predict([[x,y,year,day]])[0]
#                        #print(predic)
#                        pred.certainty = predic
#                        pred.countIndex =  countIndex + 1
#                        pred.type = 'general'
#                        pred.precog = 'ml_daytimeslots'
#                        pred.datetime = curDT
#                        pred.location = "POINT( " + str(x) + " " + str(y) + " )"
#                        db.session.add(pred)
##                       print("POINT( " + str(x) + " " + str(y) + " )")
##                       print(crimeCounts[countIndex] / maxCrimes)
#                        countIndex = countIndex + 1
#        db.session.commit()

runStats()
print("Stats pre cog finished running")
