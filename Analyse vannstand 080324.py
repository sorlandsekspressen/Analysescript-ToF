import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import pandas as pd

#%% Plassering av sensorene
placement_dist_sensor = 278  #antall cmoh logger står plassert. (Bryggekant 4.3moh)
placement_dyb_sensor = 278-224 #antall cmoh dist sensor står plassert

#%% Valg

sommertid = True
glatting = True
period_plot = False # Bruke tidsbestemming på plot?


#%% Periode som skal plottes

#Fra
dag = 18
maaned = 3
aar = 2024

start = dt.datetime(aar,maaned,dag, hour = 0)   #yyyy,m,d
# stop = dt.datetime(2023,5,29, hour = 0)
stop = dt.datetime.now()

#%% import og laging av arrays

#Henter inn fila som en dataframe i pandas
data = pd.read_csv('http://sensor.marin.ntnu.no/logs/vannstand_skien2.txt', delimiter=',', skiprows=28)


# Change the column names
data.columns =['filename', 'time', 'temp', 'dist', 'dyb', 'voltage','runTime']


epochTime = data['time'].values    
volt = data['voltage'].values
runTime = data['runTime'].values/1000 
temp = data['temp'].values
dyb = data['dyb'].values
distance = data['dist'].values 

#%% Bugfix for å fikse tider som er i fremtiden (kommer fra frakoblet rtc)
for i in range (1,len(epochTime)):
    if epochTime[i] > 1800000000:
        epochTime[i] = epochTime[i-1]

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
        
#%% Feilvisning på avstanden til HC-SR04
feil = 7  #antall cm som HC-SR04 måler for langt

distance = distance - feil

#%% Kalibrerer inn avstander for begge sensorer

cmoh_dist = placement_dist_sensor - distance  #sensor står placement cmoh. Kalibrert mot statens kartverk bryggekant på 4.3moh
cmoh_dyb = placement_dyb_sensor + dyb 

#%% Lager gjennomsnitt fra begge målerne

cmoh_mean = np.zeros(len(cmoh_dist))

for i in range(len(cmoh_dist)):
    if int(cmoh_dist[i]) == 0:
        cmoh_mean[i] = cmoh_dyb[i]
    else:
        cmoh_mean[i] = int(cmoh_dist[i] + cmoh_dyb[i])/2

#%% Glattefunk

if glatting:
    
    vekting = 0.60  # vekting av ny vs gammel måling

    for i in range(1,len(cmoh_mean)):
        cmoh_mean[i] = (1-vekting) * cmoh_mean[i-1] + vekting * cmoh_mean[i]

#%% Regning av gj.snitt

runTime_mean=np.mean(runTime)
interval_mean=np.mean(interval)

#%% printStatements

print(dt.datetime.now()-timelist[-1],'-hh:mm:ss- siden siste sending')
print('Gj.snitt runTime er',round(runTime_mean,1),'s')
print('Gj.snitt intervall er',round(interval_mean,1),'s')

#%% Savedata

# Making array
saveArr = np.array([epochTime,cmoh_mean,cmoh_dist, cmoh_dyb, temp, volt, runTime, interval],
                   dtype = 'object')
#Array into dataframe
saveData = pd.DataFrame(data = np.swapaxes(saveArr,0,1))
# Change the column names on dataframe
saveData.columns =['epochTime', 'cmoh_mean', 'cmoh_dist', 'cmoh_dyb', 'luftTemp', 'voltage','runTime', 'interval']
# export dataframe into csv-string
saveCSV = saveData.to_csv(index = False)
#print to file
text_file = open("Loggfil vannstand skiensvassdrag 2024.txt", "w")
text_file.write(saveCSV)
text_file.close()

#%% Plotfunk

plt.figure(1,figsize=(10,7))
plt.plot(timelist,volt,'b.')
plt.ylabel('Spenning[V]')
plt.xlabel('Tid')
plt.title('Spenning 1S4P PLS MKR V1.4')
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
plt.plot(timelist,temp,'b-')
plt.title('Lufttemperatur')
plt.xlabel('Tid')
plt.ylabel('Temp[C]')
if period_plot:
    plt.xlim(start,stop)
plt.grid()

plt.figure(5,figsize=(10,7))
plt.plot(timelist,cmoh_dist,'b.-')
plt.plot(timelist,cmoh_dyb,'r.-')
plt.title('Vannstand i skiensvassdraget - begge sensorer')
plt.xlabel('Tid')
plt.ylabel('Vannstand[cmoh]')
plt.legend(labels=('Ultrasonisk','Trykkmåler'))
if period_plot:
    plt.xlim(start,stop)
plt.grid()

plt.figure(6,figsize=(10,7))
plt.plot(timelist,cmoh_mean,'g.-')
plt.title('Vannstand i skiensvassdraget - gjennomsnitt av begge sensorer')
plt.xlabel('Tid')
plt.ylabel('Vannstand[cmoh]')
if period_plot:
    plt.xlim(start,stop)
plt.grid()




