import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time 
from datetime import datetime

import sys
sys.path.insert(1, '../python-scripts-c6fxKDJrSsWp1xCxON1Y7g')
from api_calls import *

def print_cp_overview(data):
    print('Number of CP files in selected upload:', len(data))
    if data:
        print('Timestamp first CP file:', data[0]["datetime"])
    
def get_cp_overview_dataframe(data):
    data.sort(key=lambda x: datetime.strptime(x.get('datetime'), "%Y-%m-%dT%H:%M:%S+%f:00"))
    time = []
    voltage = []
    current = []
    for d in data:
        expected_length = len(d.get('time', []))
        voltage.extend(d.get('voltage', [None]*expected_length))
        current.extend(d.get('current', [None]*expected_length))
        time_tmp = np.array(d.get('time', []), dtype=np.float64)
        time_tmp += np.max(time) if time else 0
        time.extend(time_tmp)  
    df = pd.DataFrame(data={'time': time, 'voltage': voltage, 'current': current},)
    return df

def plot_overview(df):
    plt.figure()
    plt.plot(np.array(df.time)/3600, df.voltage, linestyle='solid', color='darkblue',)
    #label="$E_{\mathrm{applied}} = 250\, \mathrm{mA\, cm^{-2}}$",)
    plt.title('Chronopotentiometry', fontsize=18)
    plt.xlabel('Time [hr]', loc='center', fontsize=14)
    plt.ylabel('Voltage [V]', loc='center', fontsize=14)
    plt.tick_params(axis='both', which='major', labelsize=12)
    plt.show()

def plot_interval(df):
    plt.figure()
    plt.plot(np.array(df.time), df.voltage, linestyle='solid', color='darkgreen',)
    plt.title('Chronopotentiometry', fontsize=18)
    plt.xlabel('Time [s]', loc='center', fontsize=14)
    plt.ylabel('Voltage [V]', loc='center', fontsize=14)
    plt.tick_params(axis='both', which='major', labelsize=12)
    plt.show()

def run_analysis(url, token, upload_name):
    data = get_specific_entrytype_of_uploads(url, token, [upload_name], 'CE_NOME_Chronopotentiometry', with_meta=False)
    print_cp_overview(data)
    df = get_cp_overview_dataframe(data)
    if df.empty:
        print('Please select another upload that contains entries of type CE_NOME_Chronopotentiometry.')
    else:
        plot_overview(df)
    return df

