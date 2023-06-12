import dbdicom as db
from wezel.gui import Menu, Action


#
# is_clickable functions
#


def is_database_open(app): 
    if app.database() is None:
        return False
    return app.database().manager.is_open()

def is_series_selected(app):
    return app.nr_selected('Series') != 0  

def is_study_selected(app):
    return app.nr_selected('Studies') != 0 

def is_patient_selected(app):
    return app.nr_selected('Patients') != 0


#
# on_clicked functions
#
 
 
def delete(app, generation):
    records = app.selected(generation)        
    for j, record in enumerate(records):
        app.status.progress(j, len(records), 'Deleting..')
        record.remove()
    app.refresh()


def copy(app, generation):

    app.status.message("Copying..")
    records = app.selected(generation)   
    # This can be faster - copy all in one go     
    for j, record in enumerate(records):
        #app.status.progress(j, len(records), 'Copying..')
        record.copy()               
    app.refresh()


def copy_series(app):
    studies = app.database().studies()
    labels = [s.label() for s in studies]
    cancel, f = app.dialog.input(
        {'type':'dropdownlist', 'label':'Copy to study: ', 'list': labels, 'value': 0},
        title = 'Copy to which study?')
    if cancel:
        return
    study = studies[f[0]['value']]
    series = app.selected('Series')        
    for j, sery in enumerate(series):
        app.status.progress(j, len(series), 'Moving..')
        sery.copy_to(study)               
    app.refresh()


def copy_studies(app):
    patients = app.database().patients()
    labels = [p.label() for p in patients]
    cancel, f = app.dialog.input(
        {'type':'dropdownlist', 'label':'Copy to patient: ', 'list': labels, 'value': 0},
        title = 'Copy to which patient?')
    if cancel:
        return
    patient = patients[f[0]['value']]
    studies = app.selected('Studies')
    for j, study in enumerate(studies):
        app.status.progress(j, len(studies), 'Copying..')
        study.copy_to(patient)
    app.refresh()


def move_series(app):
    studies = app.database().studies()
    labels = [s.label() for s in studies]
    cancel, f = app.dialog.input(
        {'type':'dropdownlist', 'label':'Move to study: ', 'list': labels, 'value': 0},
        title = 'Move to which study?')
    if cancel:
        return
    study = studies[f[0]['value']]
    series = app.selected('Series')        
    for j, sery in enumerate(series):
        app.status.progress(j, len(series), 'Moving..')
        sery.move_to(study)               
    app.refresh()


def move_studies(app):
    patients = app.database().patients()
    labels = [p.label() for p in patients]
    cancel, f = app.dialog.input(
        {'type':'dropdownlist', 'label':'Move to patient: ', 'list': labels, 'value': 0},
        title = 'Move to which patient?')
    if cancel:
        return
    patient = patients[f[0]['value']]
    studies = app.selected('Studies')        
    for j, study in enumerate(studies):
        app.status.progress(j, len(studies), 'Moving..')
        study.move_to(patient)               
    app.refresh()


def new_series(app): 
    app.status.message('Creating new series..')
    studies = app.selected('Studies')
    for study in studies:
        study.new_series(SeriesDescription='New series')
    app.refresh()


def new_study(app): 
    app.status.message('Creating new study..')
    patients = app.selected('Patients')
    for patient in patients:
        patient.new_study(StudyDescription='New study')
    app.refresh()


def new_patient(app): 
    app.status.message('Creating new patient..')
    app.database().new_patient(PatientName='New patient')
    app.refresh()


def split_series(app): 
    series = app.database().series()
    sel = app.selected('Series')  
    sel = series[0] if sel==[] else sel[0]      
    cancel, f = app.dialog.input(
        {"label":"Split series..", "type":"select record", "options": series, 'default': sel},
        {"label":"Split by which DICOM keyword?", "type":"string", "value": "ImageType"},
        title = "Input for series splitting")
    if cancel:
        return
    try:
        split = f[0].split_by(f[1]['value'])
    except Exception as e:
        app.dialog.information(e)
    else:
        for s in split:
            app.display(s)
        app.refresh()


def merge_series(app): 
    app.status.message('Merging..')
    records = app.selected('Series')
    study = records[0].parent()
    series = study.new_series(SeriesDescription='Merged series')
    db.merge(records, series)
    app.refresh()


def merge_studies(app): 
    app.status.message('Merging..')
    studies = app.selected('Studies')
    patient = studies[0].new_pibling(PatientName='Merger')
    db.merge(studies, patient.new_study(StudyDescription='Merged studies'))
    app.refresh()


def merge_patients(app): 
    app.status.message('Merging..')
    records = app.selected('Patients')
    patient = records[0].new_sibling(PatientName='Merged Patients')
    db.merge(records, patient)
    app.refresh()


def group_series(app): 
    app.status.message('Grouping..')
    records = app.selected('Series')
    study = records[0].new_pibling(StudyDescription='Grouped')
    db.group(records, study)
    app.status.hide()
    app.refresh()


def group_studies(app): 
    app.status.message('Grouping..')
    records = app.selected('Studies')
    patient = records[0].new_pibling(PatientName='Grouped')
    db.group(records, patient)
    app.status.hide()
    app.refresh()


def rename_series(app): 
    series_list = app.selected('Series')
    for s in series_list:
        cancel, f = app.dialog.input(
            {"type":"string", "label":"New series name:", "value": s.SeriesDescription},
            title = 'Enter new series name')
        if cancel:
            return
        s.SeriesDescription = f[0]['value']
    app.refresh()


def rename_studies(app): 
    for s in app.selected('Studies'):
        cancel, f = app.dialog.input(
            {"type":"string", "label":"New study name:", "value": s.StudyDescription},
            title = 'Enter new study name')
        if cancel:
            return
        s.StudyDescription = f[0]['value']
    app.refresh()


def rename_patients(app): 
    for patient in app.selected('Patients'):
        cancel, f = app.dialog.input(
            {"type":"string", "label":"New patient name:", "value": patient.PatientName},
            title = 'Enter new patient name')
        if cancel:
            return
        patient.PatientName = f[0]['value']
    app.refresh()


def series_extract_by_index(app):

    # Get source data
    series = app.selected('Series')[0]
    _, slices = series.get_pixel_array(['SliceLocation', 'AcquisitionTime'])
    series.status.hide()
    nz, nt = slices.shape[0], slices.shape[1]
    x0, x1, t0, t1 = 0, nz, 0, nt

    # Get user input
    invalid = True
    while invalid:
        cancel, f = app.dialog.input(
            {"type":"integer", "label":"Slice location from index..", "value":x0, "minimum": 0, "maximum": nz},
            {"type":"integer", "label":"Slice location to index..", "value":x1, "minimum": 0, "maximum": nz},
            {"type":"integer", "label":"Acquisition time from index..", "value":t0, "minimum": 0, "maximum": nt},
            {"type":"integer", "label":"Acquisition time to index..", "value":t1, "minimum": 0, "maximum": nt},
            title='Select parameter ranges')
        if cancel: 
            return
        x0, x1, t0, t1 = f[0]['value'], f[1]['value'], f[2]['value'], f[3]['value']
        invalid = (x0 >= x1) or (t0 >= t1)
        if invalid:
            app.dialog.information("Invalid selection - first index must be lower than second")

    # Extract series and save
    #study = series.parent().new_sibling(StudyDescription='Extracted Series')
    indices = ' [' + str(x0) + ':' + str(x1) 
    indices += ', ' + str(t0) + ':' + str(t1) + ']'
    #new_series = study.new_child(SeriesDescription = series.SeriesDescription + indices)
    new_series = series.new_sibling(SeriesDescription = slices[0,0,0].SeriesDescription + indices)
    #db.copy_to(slices[x0:x1,t0:t1,:], new_series)
    #new_series.adopt(np.ravel(slices[x0:x1,t0:t1,:]).tolist())
    new_series.adopt(slices[x0:x1,t0:t1,:].flatten().tolist())
    app.display(new_series)
    app.refresh()


def series_extract_by_value(app):

    # Get source data
    series = app.selected('Series')[0]
    slice_locations = series.SliceLocation
    if not isinstance(slice_locations, list):
        slice_locations = [slice_locations]
    acquisition_times = series.AcquisitionTime
    if not isinstance(acquisition_times, list):
        acquisition_times = [acquisition_times]
    series.status.hide()

    # Get user input
    cancel, f = app.dialog.input(
        {"type":"listview", "label":"Slice locations..", 'list': slice_locations},
        {"type":"listview", "label":"Acquisition times..", 'list': acquisition_times},
        title='Select parameter ranges')
    if cancel: 
        return
    if f[0]['value'] != []:
        slice_locations = [slice_locations[i] for i in f[0]['value']]
    if f[1]['value'] != []:
        acquisition_times = [acquisition_times[i] for i in f[1]['value']]

    # Find matching instances
    all = series.instances()
    instances = []
    for i, instance in enumerate(all):
        series.status.progress(i, len(all), 'Finding instances..')
        v = instance[['SliceLocation', 'AcquisitionTime']]
        if (v[0] in slice_locations) and (v[1] in acquisition_times):
            instances.append(instance)
    series.status.hide()
    if instances == []:
        return

    # Copy matching instances into new series
    series.status.message('Çopying to series..')
    desc = instances[0].SeriesDescription + ' [subseries]'
    new_series = series.new_sibling(SeriesDescription = desc)
    new_series.adopt(instances)
    series.status.hide()
    app.display(new_series)
    app.refresh()




action_series_delete = Action('Series > Delete', on_clicked=lambda app: delete(app, 'Series'), is_clickable=is_series_selected)
action_series_copy = Action('Series > Copy', on_clicked=lambda app: copy(app, 'Series'), is_clickable=is_series_selected)
action_series_copy_to = Action('Series > Copy to..', on_clicked=copy_series, is_clickable=is_series_selected)
action_series_move_to = Action('Series > Move to..', on_clicked=move_series, is_clickable=is_series_selected)
action_series_merge = Action('Series > Merge', on_clicked=merge_series, is_clickable=is_series_selected)
action_series_group = Action('Series > Group', on_clicked=group_series, is_clickable=is_series_selected)
action_series_split = Action('Series > Split by..', on_clicked=split_series, is_clickable=is_series_selected)
action_series_rename = Action('Series > Rename', on_clicked=rename_series, is_clickable=is_series_selected)
action_series_extract_by_index = Action('Series > Extract subseries (by index)', on_clicked=series_extract_by_index, is_clickable=is_series_selected)
action_series_extract_by_value = Action('Series > Extract subseries (by value)', on_clicked=series_extract_by_value, is_clickable=is_series_selected)
action_studies_delete = Action('Studies > Delete', on_clicked=lambda app: delete(app, 'Studies'), is_clickable=is_study_selected)
action_studies_copy = Action('Studies > Copy', on_clicked=lambda app: copy(app, 'Studies'), is_clickable=is_study_selected)
action_studies_copy_to = Action('Studies > Copy to..', on_clicked=copy_studies, is_clickable=is_study_selected)
action_studies_move_to = Action('Studies > Move to..', on_clicked=move_studies, is_clickable=is_study_selected)
action_studies_merge = Action('Studies > Merge', on_clicked=merge_studies, is_clickable=is_study_selected)
action_studies_group = Action('Studies > Group', on_clicked=group_studies, is_clickable=is_study_selected)
action_studies_rename = Action('Studies > Rename', on_clicked=rename_studies, is_clickable=is_study_selected)
action_studies_new_series = Action('Studies > New series', on_clicked=new_series, is_clickable=is_study_selected)
action_patients_delete = Action('Patients > Delete', on_clicked=lambda app: delete(app, 'Patients'), is_clickable=is_patient_selected)
action_patients_copy = Action('Patients > Copy', on_clicked=lambda app: copy(app, 'Patients'), is_clickable=is_patient_selected)
action_patients_merge = Action('Patients > Merge', on_clicked=merge_patients, is_clickable=is_patient_selected)
action_patients_rename = Action('Patients > Rename', on_clicked=rename_patients, is_clickable=is_patient_selected)
action_patients_new_study = Action('Patients > New study', on_clicked=new_study, is_clickable=is_patient_selected)
action_database_new_patient = Action('Database > New patient', on_clicked=new_patient, is_clickable=is_database_open)



menu = Menu('Edit')
menu_series = menu.add_menu('Series')
menu_series.add(action_series_delete)
menu_series.add(action_series_copy)
menu_series.add(action_series_copy_to)
menu_series.add(action_series_move_to)
menu_series.add(action_series_merge)
menu_series.add(action_series_group)
menu_series.add(action_series_split)
menu_series.add(action_series_rename)
menu_series.add(action_series_extract_by_index)
menu_series.add(action_series_extract_by_value)
menu_study = menu.add_menu('Studies')
menu_study.add(action_studies_delete)
menu_study.add(action_studies_copy)
menu_study.add(action_studies_copy_to)
menu_study.add(action_studies_move_to)
menu_study.add(action_studies_merge)
menu_study.add(action_studies_group)
menu_study.add(action_studies_rename)
menu_study.add(action_studies_new_series)
menu_patient = menu.add_menu('Patient')
menu_patient.add(action_patients_delete)
menu_patient.add(action_patients_copy)
menu_patient.add(action_patients_merge)
menu_patient.add(action_patients_rename)
menu_patient.add(action_patients_new_study)
menu_database = menu.add_menu('Database')
menu_database.add(action_database_new_patient)


