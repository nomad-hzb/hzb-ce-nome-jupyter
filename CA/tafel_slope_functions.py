import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from api_calls import *

def get_environment_info(url, token, entry_id):
    try:
        env = get_environment(url, token, entry_id)
    except:
        env = {}
    return env


def get_ca_env_upload(url, token, upload_names):
    if not upload_names:
        return []
    data_with_meta = get_specific_entrytype_of_uploads(url, token, upload_names, 'CE_NOME_Chronoamperometry', with_meta=True)
    # get environment (needed later to get pH)
    data = [
        (
            {**tupel[0], 
             "environment_info": get_environment_info(url, token, tupel[1].get('entry_id')),
             "upload_name": tupel[1].get('upload_name'),
            },
            tupel[1]
        )
        for tupel in data_with_meta
    ]
    # only keep data without meta_data
    data = [entry[0] for entry in data]
    # order data by date
    data = sorted(data, key=lambda entry: entry.get('datetime'))
    return data

def get_overview_df(data, avg_points=40):
    # make a list to store the data for each data file
    time_list = []
    current_list = []
    current_average_list = []
    potential_list = []
    environment_ph_list = []
    upload_name_list = []

    # iterate over all files
    for file in data:
        # navigate inside the data and get the values you are interested in
        # change this depending on your use case
        time = file.get('time')
        current = file.get('current')   # in mA
        potential = file.get('properties').get('step_1_potential')  # in V
        # calculate the average of the last 40 current values (avg_points)
        current_avg = np.mean(current[-avg_points:])
        # append the values to the lists for later usage
        time_list.append(time)
        current_list.append(current)
        potential_list.append(potential)
        current_average_list.append(current_avg)
        environment_ph = file.get('environment_info', {'ph_value': 0}).get('ph_value')
        environment_ph_list.append(environment_ph)
        upload_name_list.append(file.get('upload_name'))
        
    overview_table = pd.DataFrame({
        'time': time_list,
        'current': current_list,
        'potential': potential_list,
        f'avg last {avg_points} current (mA)': current_average_list,
        'j (A/cm²)': (np.array(current_average_list)/1000)/6,
        'environment_ph': environment_ph_list,
        'upload_name': upload_name_list,
      })
    #overview_table['log(j (A/cm²))'] = np.log10(overview_table['j (A/cm²)'])
    mask = overview_table['j (A/cm²)'] > 0
    overview_table.loc[mask, 'log(j (A/cm²))'] = np.log10(overview_table.loc[mask, 'j (A/cm²)'])
    return overview_table

def show_tafel_slope_plot(overview_table):
    if overview_table.empty:
        return
    plt.figure(figsize=(12, 5))
    for upload_name, group in overview_table.groupby('upload_name'):
        plt.plot(
            group['log(j (A/cm²))'], 
            group['potential'], 
            marker='o', 
            linestyle='-', 
            label=f'{upload_name}'
        )
    plt.xlabel('log(j (A/cm²))')
    plt.ylabel('Potential (V)')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    # show whole plot width including legend
    plt.tight_layout()
    plt.show()

def plot_avg_current_calculation(df, avg_points):
    if df.empty:
        return
    for idx, row in df.iterrows():
        plt.figure()
        plt.plot(row['time'], row['current'], color='blue', label='current (mA)')
        plt.plot(row['time'][-avg_points:], [row[f'avg last {avg_points} current (mA)']]*avg_points, color='red', linestyle='--', label=f"average = {round(row[f'avg last {avg_points} current (mA)'],4)}mA")
    
        plt.xlabel('Time (s)')
        plt.ylabel('Current (mA)')
        plt.title(f"voltage = {row['potential']}V, pH {row['environment_ph']}, {row['upload_name']}")
    
        plt.legend(title=f"voltage = {row['potential']}V")
    
        plt.show()