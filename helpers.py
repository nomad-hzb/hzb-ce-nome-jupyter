import io
import ipywidgets as widgets
import urllib
import zipfile
import plotly.graph_objects as go

def create_zip_download_link(dfs, file_names, folder_name=''):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for df, file_name in zip(dfs, file_names):
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, header=True)
            zf.writestr(file_name, csv_buffer.getvalue())
    zip_buffer.seek(0)
    zip_encoded = urllib.parse.quote(zip_buffer.getvalue())

    download_button = widgets.HTML(
        f'<a download="nomad_{folder_name}_data.zip" href="data:application/zip;charset=utf-8,{zip_encoded}" target="_blank">'
        f'<button>Download {folder_name} (ZIP folder)</button></a>'
    )
    display(download_button)

def create_zip_plots_link(plot_list, file_names, folder_name=''):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for fig, file_name in zip(plot_list, file_names):
            img_buffer = io.BytesIO()
            fig.savefig(img_buffer, format='png')
            img_buffer.seek(0)  # back to beginning
            zf.writestr(f'{file_name}.png', img_buffer.read()) 
    zip_buffer.seek(0)
    zip_encoded = urllib.parse.quote(zip_buffer.getvalue())

    download_button = widgets.HTML(
        f'<a download="nomad_{folder_name}_plots.zip" href="data:application/zip;charset=utf-8,{zip_encoded}" target="_blank">'
        f'<button>Download {folder_name} (ZIP folder)</button></a>'
    )
    display(download_button)

def get_line_plot(plot_title, x_axis_label, y_axis_label, traces_label_list, x_data_traces_list, y_data_traces_list,):
    fig = go.Figure()
    for x_data, y_data, label in zip(x_data_traces_list, y_data_traces_list, traces_label_list):
        fig.add_trace(go.Scatter(
            x=x_data,
            y=y_data,
            mode='lines',
            name=label,
            line=dict(width=2),
        ))
    
    fig.update_layout(
        title=plot_title,
        xaxis_title=x_axis_label,
        yaxis_title=y_axis_label,
        template="plotly_white"
    )
    return fig