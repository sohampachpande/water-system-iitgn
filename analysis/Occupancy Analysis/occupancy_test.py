import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pymysql
import datetime

def getDatabaseConnection():
	# Open database connection
	conn = pymysql.connect("10.0.62.222", "root", "root", "CampusData")
	return conn


'''
area (str)		- denotes academic area within the campus
building (str)	- denotes academic building within the area
floor (str)		- denotes academic floor within the building
startTimeEpoch (int) - start of time to be monitored
endTimeEpoch (int) - end of time to be monitored
'''
def getData(area, building, floor, startTimeEpoch, endTimeEpoch):
	# get cursor to sql database
	conn = getDatabaseConnection()
	cursor = conn.cursor()

	# Execute SQL query to get count of unique devices at given location on given date 
	cursor.execute(
	    """ SELECT timeEpoch, COUNT(anonID) FROM occupancy WHERE area='{}' AND building='{}' AND floor='{}' AND timeEpoch > {} AND timeEpoch < {}  GROUP BY timeEpoch ORDER BY timeEpoch"""
	    .format(area, building, floor, startTimeEpoch, endTimeEpoch))

	results = cursor.fetchall()

	# close connection
	cursor.close()
	conn.close()

	return results

def plotOccupancyResults(area, building, floor, startTimeEpoch, endTimeEpoch):
	results = getData(area, building, floor, startTimeEpoch, endTimeEpoch)
	print(len(results))

	results_dictionary = {}
	for p in results:
		results_dictionary[p[0]]=p[1]

	timeStamps = []
	counts = []
	for t in range(int(startTimeEpoch), int(endTimeEpoch)+1, 600):
		timeStamps.append(datetime.datetime.fromtimestamp(t))
		if t in results_dictionary:
			counts.append(results_dictionary[t])
		else:
			counts.append(None)

	dateString = datetime.datetime.fromtimestamp(startTimeEpoch).strftime('%d-%m-%Y')		

	plt.plot(timeStamps, counts)
	plt.gcf().autofmt_xdate()
	myFmt = mdates.DateFormatter('%H:%M')
	plt.gca().xaxis.set_major_formatter(myFmt)
	
	plt.savefig("result_Date-{}_Location-{}-{}-{}".format(dateString, area, building, floor))
	print("Done for Date-{} and Location{}-{}-{}".format(dateString, area, building, floor))


def test():
	# Make sure that startTimeEpoch has minutes as 0,10,20,30,40,50
	date = datetime.datetime(2019, 11, 27)
	startTimeEpoch = ( date - datetime.datetime(1970,1,1)).total_seconds()
	endTimeEpoch = startTimeEpoch + 86400 # 1 day = 24*60*60 seconds

	area = "AC"
	building = "B7"
	floor = "FF"

	plotOccupancyResults(area, building, floor, startTimeEpoch, endTimeEpoch)

if __name__ == '__main__':

	area = "AC"
	building = "B7"

	for ddmm in [(27,11),(28,11),(29,11),(30,11),(1,12),(2,12),(3,12)]:
		for floor in ["FF", "GF"]:
			date = datetime.datetime(2019, ddmm[1], ddmm[0])
			startTimeEpoch = ( date - datetime.datetime(1970,1,1)).total_seconds()
			endTimeEpoch = startTimeEpoch + 86400 # 1 day = 24*60*60 seconds

			plotOccupancyResults(area, building, floor, startTimeEpoch, endTimeEpoch)