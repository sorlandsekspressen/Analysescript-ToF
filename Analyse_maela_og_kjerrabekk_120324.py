
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import pandas as pd

#%% Valg

sommertid = True
glatting = 1 

Maelabekk = 1
Kjerrabekk = 0

period_plot = 0 # Bruke tidsbestemming på plot?


#%% Periode som skal plottes

#Fra
dag = 1
maaned = 4
aar = 2024

start = dt.datetime(aar,maaned,dag, hour = 0)   #yyyy,m,d
# stop = dt.datetime(2023,5,29, hour = 0)
stop = dt.datetime.now()

#%% import og laging av arrays

if Maelabekk:
    data = pd.read_csv('http://sensor.marin.ntnu.no/logs/BOX_2_maelabekk.txt', delimiter=',', skiprows=125) #Fikk ny plassering på stige etter 125 målinger
elif Kjerrabekk:
    data = pd.read_csv('http://sensor.marin.ntnu.no/logs/BOX_1_kjerrabekk.txt', delimiter=',', skiprows=5)

# Change the column names
data.columns =['filename', 'time', 'w_temp', 'dist', 'voltage','temperature','humidity','pressure','runTime','SD_check']


epochTime = data["time"].values
volt = data["voltage"].values
runTime = data['runTime'].values/1000 
temp = data['temperature'].values
w_temp = data['w_temp'].values
pressure = data['pressure'].values
hum = data['humidity'].values
distance = data['dist'].values 
SD_check = data['SD_check'].values 

#%% Bugfix for å fikse tider som er i fremtiden (kommer fra frakoblet rtc)
for i in range (1,len(epochTime)):
    if epochTime[i] > 1800000000:
        epochTime[i] = epochTime[i-1]

#%% Bugfix for å endre rare 17cm målinger fra kjerrabekk
if Kjerrabekk:
    for i in range (1,len(distance)):
        if distance[i] == 17:
            distance[i] = distance[i-1]

#%% Funksjon for å lage datetime-objeter fra epochTime

def epochToDatetime(x):
    liste=[]
    for i in range(len(x)):
        if sommertid:
            t=dt.datetime.utcfromtimestamp(x[i]) + dt.timedelta(hours=1)
        else:
            t=dt.datetime.utcfromtimestamp(x[i])
        liste.append(t)
    return liste 

timelist=epochToDatetime(epochTime)

#%% Regning av intervall og gjennomsnittlig intervall
 
interval=np.zeros(len(epochTime)) 
   
for i in range(len(epochTime)-1):
        interval[i]=int((epochTime[i+1]-epochTime[i]))

interval_mean=np.mean(interval[0:len(interval)-1])
#%% Rydder opp i feilmålinger (out of range)

for i in range(len(distance)):
    if int(distance[i])==0:
        distance[i] = distance[i-1]
        
#%% Fikser opp i distance for Mælabekken

if Maelabekk:
    feil = 4  #antall cm som HC-SR04 måler for langt
    distance = distance - feil

#%% Snur distance slik at nullpunkt blir hos måleren

distance = distance*-1

#%% Glattefunk

if glatting:
    
    vekting = 0.60  # vekting av ny vs gammel måling
    
    dist_glatt = np.zeros(len(distance),dtype='float')
    dist_glatt[0] = distance[0]
    
    for i in range(1,len(distance)):
        dist_glatt[i] = float((1-vekting) * distance[i-1] + vekting * distance[i])

#%% Regning av gj.snitt

runTime_mean=np.mean(runTime)
interval_mean=np.mean(interval)

#%% printStatements

print(dt.datetime.now()-timelist[-1],'-hh:mm:ss- siden siste sending')
print('Gj.snitt runTime er',round(runTime_mean,1),'s')
print('Gj.snitt intervall er',round(interval_mean,1),'s')

#%% Savedata

# Making array
saveArr = np.array([epochTime, distance, dist_glatt, w_temp, volt, runTime, interval],
                   dtype = 'object')
#Array into dataframe
saveData = pd.DataFrame(data = np.swapaxes(saveArr,0,1))
# Change the column names on dataframe
saveData.columns =['epochTime', 'vannstand', 'vannstand glattet', 'vannTemp', 'voltage','runTime', 'interval']
# export dataframe into csv-string
saveCSV = saveData.to_csv(index = False)
#print to file

if Kjerrabekk: filename = 'Loggfil behandlet Kjerrabekk.txt'
else: filename = 'Loggfil behandlet Mælabekk.txt'
text_file = open(filename, "w")    
text_file.write(saveCSV)
text_file.close()    

#%% Plotfunk

plt.figure(1,figsize=(10,7))
plt.plot(timelist,volt,'b.')
plt.ylabel('Spenning[V]')
plt.xlabel('Tid')
plt.title('Spenning 1S4P')
plt.ylim(2.5,4.2)
if period_plot:
    plt.xlim(start,stop)
plt.grid()

plt.figure(2,figsize=(10,7))
plt.plot(timelist[0:-2],interval[0:-2],'bo')
plt.xlabel('Tid')
plt.ylabel('Intervall mellom sending')
plt.title('Intervall')
plt.ylim(0,4000)
if period_plot:
    plt.xlim(start,stop)
plt.grid()

plt.figure(3,figsize=(10,7))
plt.plot(timelist,runTime,'bo')
plt.title('runTime')
plt.xlabel('Sendingsnr.')
plt.ylabel('RunTime for programmet [s]')
if period_plot:
    plt.xlim(start,stop)
plt.grid()

plt.figure(4,figsize=(10,7))
plt.plot(timelist,w_temp,'b-')
if Maelabekk:
    plt.title('Temperatur i Mælabekken')
elif Kjerrabekk:
    plt.title('Temperatur i Kjerrabekken')
plt.xlabel('Tid')
plt.ylabel('Temp[C]')
if period_plot:
    plt.xlim(start,stop)
plt.grid()


plt.figure(5,figsize=(10,7))
if glatting:
    plt.plot(timelist,dist_glatt,'b.-')
else: plt.plot(timelist,distance,'b.-')
if Maelabekk:
    plt.title('Vannstand i Mælabekken')
elif Kjerrabekk:
    plt.title('Vannstand i Kjerrabekken')
plt.xlabel('Tid')
plt.ylabel('Vannstand[cmoh]')
if period_plot:
    plt.xlim(start,stop)
plt.grid()


