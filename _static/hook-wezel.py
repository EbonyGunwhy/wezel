from PyInstaller.utils.hooks import collect_data_files
datas = collect_data_files('wezel')

# Check if this is needed for python < 3.9
# hiddenimports = ['importlib_resources']