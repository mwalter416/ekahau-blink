#!/usr/bin/python

from bottle import route, run, template, static_file, jinja2_view, post, request
import ekahau,getpass,os,sys,textfsm,wlcTools

def getCiscoBaseRadioMac(apId,ekp):
 for measuredRadio in ekp.jsonMeasuredRadios['measuredRadios']:
  if apId == measuredRadio["accessPointId"]:
   for accessPointMeasurementId in measuredRadio["accessPointMeasurementIds"]:
    for accessPointMeasurement in ekp.jsonAccessPointMeasurements["accessPointMeasurements"]:
     if accessPointMeasurementId == accessPointMeasurement["id"]:
      #print accessPointMeasurement["mac"], accessPointMeasurement["channel"], accessPointMeasurement["security"]
      return accessPointMeasurement["mac"][:-1]+"0"

def parseApJoinStatusSummaryAll(cmdoutput):
 with open("showApJoinStatusSummaryAll.fsm","r") as templateFile:
  re_table = textfsm.TextFSM(templateFile)
  return re_table.ParseText(cmdoutput)

def getCiscoAPNameFromBaseMac(baseMac,apJoinList):
 for row in apJoinList:
  if baseMac == row[0]:
   return row[2]

##Bottle STUFF
##STATIC FILES
@route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='/tmp/ekahau-blink')

##AP DEBUGGING
@route('/aps')
@jinja2_view('aps.html')
def aps():
  print ekahauProject
  print ekahauProject.jsonAccessPoints
  return {'jsonAccessPoints' : ekahauProject.jsonAccessPoints
          }

##AP Association DEBUGGING
@route('/apAssocs')
@jinja2_view('apAssocs.html')
def aps():
  apAssocs=[]
  for ap in ekahauProject.jsonAccessPoints["accessPoints"]:
    apAssocs.append([ap["id"],getCiscoAPNameFromBaseMac(getCiscoBaseRadioMac(ap["id"],ekahauProject),apJoinStatusList)])
  return {'apAssocs' : apAssocs
          }

##FP DEBUGGING
@route('/fps')
@jinja2_view('fps.html')
def fps():
  return {
          'jsonFloorPlans' : ekahauProject.jsonFloorPlans
          }

##MAP DEBUGGING
@route('/map')
@jinja2_view('map.html')
def map():
  return {'jsonAccessPoints' : ekahauProject.jsonAccessPoints,
          'jsonFloorPlans' : ekahauProject.jsonFloorPlans
          }


##Blink
@post('/blink')
def blink():
  postdata = request.body.read()
  #print postdata #this goes to log file only, not to client
  baseMac= getCiscoBaseRadioMac(postdata,ekahauProject)
  print baseMac
  apName= getCiscoAPNameFromBaseMac(baseMac,apJoinStatusList)
  print apName
  print mywlc.getCmdOutput('config ap led-state flash 10 {0}'.format(apName))


##JINJA Testing
@route('/')
@jinja2_view('home.html')
def home():
  return {'my_word' : [0,1,2,3,4]}


ekahauProject=ekahau.project(sys.argv[1])
try:
  os.mkdir('/tmp/ekahau-blink')
except:
  pass
for id, data in ekahauProject.fpImage.iteritems():
  with open('/tmp/ekahau-blink/image-'+id+'.png','w') as f:
    f.write(data)

wlcip=raw_input("WLC IP: ")
username=raw_input("Username: ")
password=getpass.getpass()

mywlc = wlcTools.wlc(wlcip, username, password)
cmdoutput=mywlc.getApJoinStats()
#mywlc.disconnect()

apJoinStatusList=parseApJoinStatusSummaryAll(cmdoutput)

##RUN WEBSERVER
run(host='localhost', port=8080)
