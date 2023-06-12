import os
import dbdicom as db
from wezel.gui import Menu, Action



def is_database_open(app): 
    if app.database() is None:
        return False
    return app.database().manager.is_open()

def is_series_selected(app):
    return app.nr_selected('Series') != 0


def new_database(app):
    """
    Create a new DICOM folder, open it and update display.
    """
    app.status.message("Opening a folder..")
    path = app.dialog.directory("Select a folder for the new database..")
    if path == '':
        app.status.message('') 
        return
    app.status.cursorToHourglass()
    app.close()
    folder = db.database(path=path, 
        status = app.status, 
        dialog = app.dialog)
    app.display(folder)
    app.status.hide()
    app.status.cursorToNormal()


def open_database(app):
    """
    Open a DICOM folder and update display.
    """
    app.status.message("Opening DICOM folder..")
    path = app.dialog.directory("Select a DICOM folder")
    if path == '':
        app.status.message('') 
        return
    app.status.cursorToHourglass()
    app.close()
    app.open(path)
    app.status.hide()
    app.status.cursorToNormal()


def read_database(app):
    """
    Read the open DICOM folder.
    """
    app.status.cursorToHourglass()
    app.central.closeAllSubWindows()
    app.database().scan()
    app.status.cursorToNormal() 
    app.refresh()


def save_database(app):
    """
    Saves the open DICOM folder.
    """
    app.database().save()
    app.status.message('Finished saving..')


def restore_database(app):
    """
    Restore the open DICOM folder.
    """
    app.database().restore()
    app.refresh()


def close_database(app):
    closed = app.database().close()
    if closed: 
        app.close()


def open_subfolders(app):
    """
    Open a DICOM folder and update display.
    """
    app.status.message("Opening DICOM folder..")
    path = app.dialog.directory("Select the top folder..")
    if path == '':
        app.status.message('') 
        return
    subfolders = next(os.walk(path))[1]
    subfolders = [os.path.join(path, f) for f in subfolders]
    app.close()
    app.status.cursorToHourglass()
    for i, path in enumerate(subfolders):
        msg = 'Reading folder ' + str(i+1) + ' of ' + str(len(subfolders))
        #app.open(path)
        app.status.message(msg)
        folder = db.database(path=path, 
            status = app.status, 
            dialog = app.dialog)
        folder.save()
    app.status.cursorToNormal()
    app.status.hide()
    app.display(folder)


def export_as_dicom(app):
    path = app.dialog.directory("Where do you want to export the data?")
    if path == '':
        return
    patients, studies, series = app.top_level_selected()
    selected = patients + studies + series
    if selected == []:
        app.dialog.information("Please select at least one series")
        return
    app.status.message('Exporting to ' + path)
    for i, record in enumerate(selected):
        app.status.progress(i, len(selected), 'Exporting to ' + path)
        record.export_as_dicom(path)
    app.status.hide()
    app.status.message('Finished exporting..')


def import_dicom_files(app):
    files = app.dialog.files("Please select DICOM files to import")
    if files == []:
        return
    dicom_found = app.database().import_dicom(files)
    if not dicom_found:
        msg = 'No DICOM data were detected. \n'
        msg += 'Nothing has been imported.'
        app.dialog.information(msg)
    app.status.hide()
    app.refresh()


def import_dicom_folder(app):
    path = app.dialog.directory("Please select DICOM folder to import.")
    if path == '':
        return
    files = db.utils.files.all_files(path)
    dicom_found = app.database().import_dicom(files)
    if not dicom_found:
        msg = 'No DICOM data were detected. \n'
        msg += 'Nothing has been imported.'
        app.dialog.information(msg)
    app.status.hide()
    app.refresh()


def export_as_png(app):
    path = app.dialog.directory("Where do you want to export the data?")
    if path == '':
        return
    patients, studies, series = app.top_level_selected()
    selected = patients + studies + series
    if selected == []:
        app.dialog.information("Please select at least one series")
        return
    app.status.message('Exporting to ' + path)
    for i, record in enumerate(selected):
        app.status.progress(i, len(selected), 'Exporting to ' + path)
        record.export_as_png(path)
    app.status.hide()
    app.status.message('Finished exporting..')


def export_as_csv(app):
    path = app.dialog.directory("Where do you want to export the data?")
    if path == '':
        return
    patients, studies, series = app.top_level_selected()
    selected = patients + studies + series
    if selected == []:
        app.dialog.information("Please select at least one series")
        return
    app.status.message('Exporting to ' + path)
    for i, record in enumerate(selected):
        app.status.progress(i, len(selected), 'Exporting to ' + path)
        record.export_as_csv(path)
    app.status.hide()
    app.status.message('Finished exporting..')


def export_as_nifti(app):
    path = app.dialog.directory("Where do you want to export the data?")
    if path == '':
        return
    patients, studies, series = app.top_level_selected()
    selected = patients + studies + series
    if selected == []:
        app.dialog.information("Please select at least one series")
        return
    app.status.message('Exporting to ' + path)
    for i, record in enumerate(selected):
        app.status.progress(i, len(selected), 'Exporting to ' + path)
        record.export_as_nifti(path)
    app.status.hide()
    app.status.message('Finished exporting..')


def export_as_npy(app):
    path = app.dialog.directory("Where do you want to export the data?")
    if path == '':
        return
    selected = app.selected('Series')
    if selected == []:
        app.dialog.information("Please select at least one series")
        return
    app.status.message('Exporting to ' + path)
    for i, record in enumerate(selected):
        app.status.progress(i, len(selected), 'Exporting to ' + path)
        record.export_as_npy(path, sortby=['SliceLocation', 'AcquisitionTime'], pixels_first=True)
    app.status.hide()
    app.status.message('Finished exporting..')


def import_nifti(app):
    files = app.dialog.files("Select NIfTI files to import")
    if files == []:
        return
    try:
        app.database().import_nifti(files)
    except:
        app.dialog.error()
    app.status.hide()
    app.refresh()


def import_gif(app):
    files = app.dialog.files("Select GIF files to import")
    if files == []:
        return
    try:
        app.status.message('Reading gif file(s)')
        study = app.database().import_gif(files)
        for series in study.series():
            app.display(series)
    except:
        app.dialog.error()
    app.status.hide()
    app.refresh()



action_new_database = Action('New', shortcut='Ctrl+N', on_clicked=new_database)
action_open_database = Action('Open', shortcut='Ctrl+O', on_clicked=open_database)
action_read_database = Action('Read', on_clicked=read_database, is_clickable=is_database_open)
action_save_database = Action('Save', shortcut='Ctrl+S', on_clicked=save_database, is_clickable=is_database_open)
action_restore_database = Action('Restore', shortcut='Ctrl+R', on_clicked=restore_database, is_clickable=is_database_open)
action_close_database = Action('Close', shortcut='Ctrl+C', on_clicked=close_database, is_clickable=is_database_open)
action_open_subfolders = Action('Open subfolders', on_clicked=open_subfolders)
action_export_as_dicom = Action('Export as DICOM', on_clicked=export_as_dicom, is_clickable=is_series_selected)
action_export_as_csv = Action('Export as CSV', on_clicked=export_as_csv, is_clickable=is_series_selected)
action_export_as_png = Action('Export as PNG', on_clicked=export_as_png, is_clickable=is_series_selected)
action_export_as_nifti = Action('Export as NIfTI', on_clicked=export_as_nifti, is_clickable=is_series_selected)
action_export_as_numpy = Action('Export as numpy', on_clicked=export_as_npy, is_clickable=is_series_selected)
action_import_dicom_files = Action('Import DICOM files', on_clicked=import_dicom_files, is_clickable=is_database_open)
action_import_dicom_folder = Action('Import DICOM folder', on_clicked=import_dicom_folder, is_clickable=is_database_open)
action_import_nifti = Action('Import NIfTI files', on_clicked=import_nifti, is_clickable=is_database_open)
action_import_gif = Action('Import GIF file', on_clicked=import_gif, is_clickable=is_database_open)



menu = Menu('File')
# Commented out for now
# Needs testing and debugging
# In current form risks deleting data
# menu.add(action_new_database) 
menu.add(action_open_database)
menu.add(action_read_database)
menu.add(action_save_database)
menu.add(action_restore_database)
menu.add(action_close_database)
menu.add_separator()
menu.add(action_open_subfolders)
menu.add_separator()
menu.add(action_export_as_dicom)
menu.add(action_export_as_csv)
menu.add(action_export_as_png)
menu.add(action_export_as_nifti)
menu.add(action_export_as_numpy)
menu.add_separator()
menu.add(action_import_dicom_files)
menu.add(action_import_dicom_folder)
menu.add(action_import_nifti)
menu.add(action_import_gif)
