import matplotlib.pyplot as plt
import time
import requests
import pandas as pd
import numpy as np
import datetime
import plotly.graph_objects as go
from scipy.signal import find_peaks

import sys
sys.path.insert(1, '../python-scripts-c6fxKDJrSsWp1xCxON1Y7g')
sys.path.insert(1, '../../python-scripts-c6fxKDJrSsWp1xCxON1Y7g')
from api_calls import *

url = "https://nomad-hzb-ce.de/nomad-oasis/api/v1"

import os
token = os.environ['NOMAD_CLIENT_ACCESS_TOKEN']


def get_photoactivity_data(url, token):
    row = {"entry_type":'CE_NOME_Chronoamperometry',
           "authors.name:any": ["Abdelrahman Ishmael", "Maddalena Zoli", "Felipe Mata mata"]
        }
    query = {
        'required': {
            'metadata': '*',
            'data': '*',
        },
        'owner': 'visible',
        'query': row,
        'pagination': {
            'page_size': 10000
        }
    }
    response = requests.post(f'{url}/entries/archive/query',
                             headers={'Authorization': f'Bearer {token}'}, json=query)
    # photoactivity_entries = [s for s in response.json()["data"] if 'CA_chopped_#1' or 'CA_chopped_#2' in s["archive"]["data"].get("data_file")]
    photoactivity_entries = [
        s for s in response.json()["data"]
        if any(chopped in s["archive"]["data"].get("data_file", "") for chopped in ["CA_chopped_#1", "CA_chopped_#2"])
    ]
    return photoactivity_entries

def get_photoactivity_data_for_samples(url, token, sample_entry_ids):
    row = {'entry_type':'CE_NOME_Chronoamperometry',
           'entry_references.target_entry_id:any': sample_entry_ids,
        }
    query = {
        'required': {
            'metadata': '*',
            'data': '*',
        },
        'owner': 'visible',
        'query': row,
        'pagination': {
            'page_size': 10000
        }
    }
    response = requests.post(f'{url}/entries/archive/query',
                             headers={'Authorization': f'Bearer {token}'}, json=query)
    # photoactivity_entries = [s for s in response.json()["data"] if 'CA_chopped_#1' or 'CA_chopped_#2' in s["archive"]["data"].get("data_file")]
    photoactivity_entries = [
        s for s in response.json()["data"]
        if any(chopped in s["archive"]["data"].get("data_file", "") for chopped in ["CA_chopped_#1", "CA_chopped_#2"])
    ]
    return photoactivity_entries

def get_stability_data_for_samples(url, token, sample_entry_ids):
    row = {'entry_type':'CE_NOME_Chronopotentiometry',
           'entry_references.target_entry_id:any': sample_entry_ids,
        }
    query = {
        'required': {
            'metadata': '*',
            'data': '*',
        },
        'owner': 'visible',
        'query': row,
        'pagination': {
            'page_size': 10000
        }
    }
    response = requests.post(f'{url}/entries/archive/query',
                             headers={'Authorization': f'Bearer {token}'}, json=query)
    stability_entries = [s for s in response.json()["data"] if 'Chronopot' in s["archive"]["data"].get("data_file")]
    return stability_entries

def get_stability_data(url, token):
    row = {"entry_type":'CE_NOME_Chronopotentiometry',
           "authors.name:any": ["Abdelrahman Ishmael", "Maddalena Zoli"],
           "results.eln.methods": 'Chronopotentiometry'
        }
    query = {
        'required': {
            'metadata': '*',
            'data': '*',
        },
        'owner': 'visible',
        'query': row,
        'pagination': {
            'page_size': 10000
        }
    }
    response = requests.post(f'{url}/entries/archive/query',
                             headers={'Authorization': f'Bearer {token}'}, json=query)
    stability_entries = [s for s in response.json()["data"] if 'Chronopot' in s["archive"]["data"].get("data_file")]
    return stability_entries

def get_specific_data_of_sample_entry_id(url, token, entry_id, entry_type, with_meta=False):
      
    query = {
        'required': {
            'metadata': '*',
            'data': '*',
        },
        'owner': 'visible',
        'query': {'entry_references.target_entry_id': entry_id},
        'pagination': {
            'page_size': 1000
        }
    }
    response = requests.post(f'{url}/entries/archive/query',
                             headers={'Authorization': f'Bearer {token}'}, json=query)
    linked_data = response.json()["data"]
    res = []
    for ldata in linked_data:
        if entry_type not in ldata["archive"]["metadata"].get('entry_type', ""):
            continue
        if with_meta:
            res.append((ldata["archive"]["data"],ldata["archive"]["metadata"]))
        else:
            res.append(ldata["archive"]["data"])
    return res 

def show_photoactivity_plots(photoactivity_entries):
    for entry in photoactivity_entries:
        time = entry['archive']['data'].get('time')
        current = entry['archive']['data'].get('current')
        
        plt.figure()  # make new figure for each plot
        plt.plot(time, current, color='b')

        plt.xlabel('Time (s)')
        plt.ylabel('Current (A)')
        plt.title(entry['archive']['metadata'].get('upload_name') + ', ' + entry['archive']['data'].get('data_file'))

        plt.show()
        
def show_stability_plots(stability_entries):
    for entry in stability_entries:
        time = entry['archive']['data'].get('time')
        voltage = entry['archive']['data'].get('voltage')
        mean_voltage = np.mean(voltage)
        
        voltage_series = pd.Series(voltage)
        window_size = 300
        smoothed_voltage_mean = voltage_series.rolling(window=window_size, center=True).mean()
        
        plt.figure()  # make new figure for each plot
        plt.plot(time, voltage, label='Original Voltage', color='gray')
        plt.plot(time, smoothed_voltage_mean, label=f'Smoothed Voltage (window size {window_size})', color='blue')            
        plt.axhline(y=mean_voltage, color='r', linestyle='--', label=f'Mean Voltage = {mean_voltage:.2f} V')

        plt.xlabel('Time (s)')
        plt.ylabel('Voltage (V)')
        plt.title(entry['archive']['metadata'].get('upload_name') + ', ' + entry['archive']['data'].get('data_file'))
        
        plt.legend()
        plt.show()
        
def get_photoactivity_info(photoactivity_entries):
    for entry in photoactivity_entries:
        time = np.array(entry['archive']['data'].get('time'))
        current = np.array(entry['archive']['data'].get('current'))
        
        peak_finding_threshold = np.mean(current)

        peaks, peak_properties = find_peaks(current, height=peak_finding_threshold)  # peaks over threshold
        valleys, valley_properties = find_peaks(-current, height=-peak_finding_threshold)  # "negative peaks"
        
        upper_plateau_mean = np.mean(current[peaks]) if len(peaks) > 0 else 0
        lower_plateau_mean = np.mean(current[valleys]) if len(valleys) > 0 else 0

        height_difference = upper_plateau_mean - lower_plateau_mean
                
        plt.figure()
        plt.plot(time, current, label='Original Current (A)', color='gray')
        plt.scatter(time[peaks], peak_properties.get('peak_heights'), color='blue')
        plt.scatter(time[valleys], -valley_properties.get('peak_heights'), color='blue')
        plt.axhline(y=upper_plateau_mean, color='r', linestyle='--', label=f'Upper Plateau Mean = {upper_plateau_mean:.2f} A')
        plt.axhline(y=lower_plateau_mean, color='r', linestyle='--', label=f'Lower Plateau Mean = {lower_plateau_mean:.2f} A')

        plt.xlabel('Time (s)')
        plt.ylabel('Current (A)')
        plt.title(entry['archive']['metadata'].get('upload_name') + ', ' + entry['archive']['data'].get('data_file'))

        plt.legend(title=f'Height Difference: {height_difference:.4f} A')
        plt.show()
        
def show_cleaned_stability_plots(stability_entries):
    for entry in stability_entries:
        time = entry['archive']['data'].get('time')
        voltage = np.array(entry['archive']['data'].get('voltage'))
        
        # add padding
        window_size = 131
        pad_width = window_size // 2
        padded_data = np.pad(voltage, pad_width, mode='reflect')  # fill edges with symmetry

        moving_avg = np.convolve(padded_data, np.ones(window_size) / window_size, mode='valid')

        threshold = 0.005
        filtered_data = np.where(np.abs(voltage - moving_avg) > threshold, moving_avg, voltage)

        plt.figure()
        plt.plot(voltage, label="Original Data", color='gray')
        plt.plot(moving_avg, label="Moving Average", linestyle="--")
        plt.plot(filtered_data, label="Filtered Data", linestyle="-.")
        plt.legend()
        plt.title("Moving Average with Padding (Reflect)")
        plt.show()

def analyse_photoactivity(current, time, prominence=0.02, distance=5):
    # this it the newer version of the peak finding (August 2025)
    peaks, _ = find_peaks(current, prominence=prominence, distance=distance)
    valleys, _ = find_peaks(-current, prominence=prominence, distance=distance)
    
    delta_I_list = []
    for v in valleys:
        next_peaks = peaks[peaks > v]
        if len(next_peaks) > 0:
            p = next_peaks[0]
            ΔI = current[p] - current[v]
            delta_I_list.append((v, p, ΔI))
    
    mean_delta_I = np.mean([d[2] for d in delta_I_list])*1000 if delta_I_list else None  #mA

    # we do not want values where there is only 1 or 2 glitches in the data
    if len(delta_I_list) < 3:
        mean_delta_I = -1
        
    return {
        'peaks': peaks,
        'valleys': valleys,
        'delta_I': delta_I_list,
        'mean_delta_I': mean_delta_I
    }

def get_photoactivity_plot(time, current, results):
    # results are given by analyse_photoactivity funtion
    peaks = results['peaks']
    valleys = results['valleys']
    delta_I_list = results['delta_I']
    
    fig = go.Figure()
    
    # Signal
    fig.add_trace(go.Scatter(x=time, y=current, mode='lines', name='Signal', line=dict(color='black')))
    # Peaks
    fig.add_trace(go.Scatter(x=time[peaks], y=current[peaks], mode='markers', name='Peaks', marker=dict(color='red', size=8)))
    # Valleys
    fig.add_trace(go.Scatter(x=time[valleys], y=current[valleys], mode='markers', name='Valleys', marker=dict(color='blue', size=8)))
    
    # ΔI
    for v, p, delta_i in delta_I_list:
        fig.add_trace(go.Scatter(
            x=[time[v], time[p]],
            y=[current[v], current[p]],
            mode='lines',
            line=dict(color='green', dash='dash'),
            showlegend=False
        ))
        mid_t = (time[v] + time[p]) / 2
        fig.add_trace(go.Scatter(
            x=[mid_t],
            y=[current[p]],
            mode='text',
            text=[f'{delta_i:.3f}'],
            showlegend=False,
            textposition='top center',
            textfont=dict(color='green')
        ))
    # for ΔI in legend
    fig.add_trace(go.Scatter(x=[time[0]], y=[current[0]], mode='lines', name='ΔI', line=dict(color='green')))
    
    fig.update_layout(
        xaxis_title='Time (s)',
        yaxis_title='Current (A)',
        title=f'Photoactivity (mean ΔI={results["mean_delta_I"]} mA)',
        template='plotly_white'
    )
    
    return fig
    

def analyse_stability(time, voltage):
    max_volt_idx = np.argmax(voltage)
    time_interval_start = (time > time[max_volt_idx]) & (time <= time[max_volt_idx] + 600)
    mean_voltage_start = voltage[time_interval_start].mean()

    time_interval_end = time >= time.max() - 1000
    mean_voltage_end = voltage[time_interval_end].mean()

    voltage_diff = mean_voltage_start - mean_voltage_end
    percentage_of_loss = voltage_diff / mean_voltage_start * 100

    return {
        'time_interval_start': time_interval_start,
        'time_interval_end': time_interval_end,
        'mean_voltage_start': mean_voltage_start,
        'mean_voltage_end': mean_voltage_end,
        'voltage_diff': voltage_diff,
        'percentage_of_loss': percentage_of_loss
    }


def get_stability_plot(time, voltage, stability_analysis_result):
    time_interval_start = stability_analysis_result['time_interval_start']
    time_interval_end = stability_analysis_result['time_interval_end']
    mean_voltage_start = stability_analysis_result['mean_voltage_start']
    mean_voltage_end = stability_analysis_result['mean_voltage_end']

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=time, y=voltage,
        mode='lines',
        name='Original Voltage',
        line=dict(color='gray')
    ))
    fig.add_trace(go.Scatter(
        x=time[time_interval_start],
        y=[mean_voltage_start]*time_interval_start.sum(),
        mode='lines',
        name=f'Mean Voltage Start = {mean_voltage_start*1000:.2f} mV',
        line=dict(color='red') #, dash='dash')
    ))
    fig.add_trace(go.Scatter(
        x=time[time_interval_end],
        y=[mean_voltage_end]*time_interval_end.sum(),
        mode='lines',
        name=f'Mean Voltage End = {mean_voltage_end*1000:.2f} mV',
        line=dict(color='red') #, dash='dot')
    ))

    fig.update_layout(
        title=f'Stability (percentage of loss: {stability_analysis_result['percentage_of_loss']:.3f})',
        xaxis_title='Time (s)',
        yaxis_title='Voltage (V)',
        legend_title=f'Difference: {stability_analysis_result['voltage_diff']*1000:.3f} mV -> {stability_analysis_result['percentage_of_loss']:.3f} %',
        template='plotly_white',
    )
    return fig
