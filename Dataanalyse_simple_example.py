import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import pandas as pd

#%% Vintertid - Om den gir feil tid, så endre verdi på timedelta i linje 33 og 35

vintertid=False

#%% import og laging av arrays

#Henter inn fila som en dataframe i pandas. legg inn url til datafil
data = pd.read_csv('url til fil.no', delimiter=',')

# Tar ut de kolonnonene som jeg vil bruke fra data og lager egne arrays (numpy lister) av dem data blir lagret som float
# Kolonnene hentes ut ved overskrift (første data i kolonnen). Dette må justeres til hvilke data som ligger i din fil.

epochTime = data["1686171837"].values
templuft = data['23.7'].values
volt = data["2.52"].values

#%% Funksjon for å lage datetime-objeter fra epochTime

def epochToDatetime(x):
    liste=[]
    for i in range(len(x)):
        if vintertid:
            t=dt.datetime.utcfromtimestamp(x[i]) + dt.timedelta(hours=1)
        else:
            t=dt.datetime.utcfromtimestamp(x[i]) + dt.timedelta(hours=2)
        liste.append(t)
    return liste 

#%% Anvender funksjonen ovenfor

timelist=epochToDatetime(epochTime)

#%% Regning av gjennomsnittlig intervall

interval=np.zeros(len(timelist))
    
for i in range(len(epochTime)-1):
        interval[i]=int((epochTime[i+1]-epochTime[i]))

interval_mean=np.mean(interval[0:len(interval)-1])

#%% printStatements

print(dt.datetime.now()-timelist[-1],'-hh:mm:ss- siden siste sending')
#%% Plotfunk

plt.figure(1,figsize=(11,8))
plt.plot(timelist,volt,'b.')
plt.ylabel('Spenning[V]')
plt.xlabel('Tid')
plt.title('Spenning (1S3P 2500mah liPo)')
plt.ylim(3.2,4.2)
plt.grid()

plt.figure(3,figsize=(11,8))
plt.plot(timelist,templuft,'r.')
plt.xlabel('Tid')
plt.ylabel('Temperatur')
plt.title('Temperaturmålinger')
plt.grid()





