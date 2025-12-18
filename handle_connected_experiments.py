def get_reference_link(calibration_entry):
    upload_id = calibration_entry.get('upload_id')
    entry_id = calibration_entry.get('entry_id')
    return f'../uploads/{upload_id}/archive/{entry_id}#data'

def get_entry_id_from_ref_link(entry_link):
    if "archive/" not in entry_link or "#/data" not in entry_link:
        return None
    return entry_link.split("archive/")[1].split("#/data")[0]

def get_entry_method(url, nomad_request_session, entry_link):
    entry_id = get_entry_id_from_ref_link(entry_link)
    response = nomad_request_session.post(
        f'{url}/entries/{entry_id}/archive/query',
        json={
            'required': {
                'data': {
                    'method': '*',
                },
            },
        },
    )
    return response.json().get('data', {}).get('archive', {}).get('data', {}).get('method', [])

def get_connected_experiments(url, nomad_request_session, entry_id):
    response = nomad_request_session.post(
        f'{url}/entries/{entry_id}/archive/query',
        json={
            'required': {
                'data': {
                    'connected_experiments': '*',
                },
            },
        },
    )
    return response.json().get('data', {}).get('archive', {}).get('data', {}).get('connected_experiments', [])

def get_connected_experiments_filtered_by_method(url, nomad_request_session, connected_entries_list, measurement_method):
    same_method_list = []
    other_refs_list = []
    for entry in connected_entries_list:
        method = get_entry_method(url, nomad_request_session, entry)
        if method == measurement_method:
            same_method_list.append(entry)
        else:
            other_refs_list.append(entry)
    return same_method_list, other_refs_list

def get_nome_entryids_from_upload(url, nomad_request_session, upload_id, owner='visible'):   
    query = {
        'required': {
            'metadata': {
                'entry_id': '*',
            }
        },
        'owner': owner,
        'query': {
            'upload_id': upload_id,
            'entry_type:any': [
                'CE_NOME_Chronoamperometry',
                'CE_NOME_Chronopotentiometry',
                'CE_NOME_LinearSweepVoltammetry',
                'CE_NOME_GalvanodynamicSweep',
                'CE_NOME_CyclicVoltammetry',
            ]
        },
        'pagination': {
            'page_size': 10000
        }
    }
    response = nomad_request_session.post(f'{url}/entries/archive/query', json=query)
    linked_data = response.json()["data"]
    res = []
    for ldata in linked_data:
        res.append(ldata.get('entry_id'))
    return res   

def write_calibration_to_nomad(url, nomad_request_session, entry_id, path, value, connected_experiments):
    query = {
      "changes": [
          {
              "path": path,
              "new_value": value,
              "action": "upsert"
          },
          {
              "path": "data/connected_experiments",
              "new_value": connected_experiments,
              "action": "upsert"
          }
      ]
    }
    response = nomad_request_session.post(f'{url}/entries/{entry_id}/edit', json=query)
    return response.json()

