import io
import ipywidgets as widgets
import urllib
import zipfile


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
        f'<a download="xas_{folder_name}_data.zip" href="data:application/zip;charset=utf-8,{zip_encoded}" target="_blank">'
        f'<button>Download {folder_name} (ZIP folder)</button></a>'
    )
    display(download_button)