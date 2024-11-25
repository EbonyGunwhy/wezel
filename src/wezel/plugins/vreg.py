import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from dbdicom.extensions import vreg
from wezel.gui import Action, Menu
from wezel.displays import TableDisplay, MatplotLibDisplay


def _if_a_series_is_selected(app):
    return app.nr_selected('Series') != 0

def _if_a_database_is_open(app):
    return app.database() is not None


def _translation(app):
    series = app.database().series()
    sel = app.selected('Series')
    metric = ['sum of squares', 'mutual information', 'interaction']
    cancel, f = app.dialog.input(
        {"label":"Moving series", "type":"select record", "options": series, 'default':sel},
        {"label":"Static series", "type":"select record", "options": series, 'default':sel},
        {"label":"Target region", "type":"select optional record", "options": series},
        {"label":"Apply transformation to:", "type":"select records", "options": series, 'default':[]},
        {"label":"Apply passive transformation?", "type":"dropdownlist", 'list':['Yes', 'No'], 'value':1},
        {"label":"Tolerance (smaller = slower but more accurate)", "type":"float", 'value':0.1, 'minimum':0.001}, 
        {"label":"Cost function", "type":"dropdownlist", 'list':metric, 'value':1}, 
        {"label":"Margin around target (mm)", "type":"float", 'value':0.0, 'minimum':0.0},
        title = "Please select coregistration parameters (translation)")
    if cancel:
        return
    params = vreg.find_translation(f[0], f[1], 
            tolerance=f[5]["value"], 
            metric=metric[f[6]["value"]], 
            region=f[2],
            margin=f[7]['value'])

    # Save results as new dicom series
    f[0].message('Applying translations..')
    to_move = f[3] if f[0] in f[3] else [f[0]] + f[3]
    for series in to_move:
        if f[4]['value'] == 1:
            series_moved = vreg.apply_translation(series, params, target=f[1])
        else:
            series_moved = vreg.apply_passive_translation(series, params)
        app.display(series_moved)
    app.refresh()


def _rigid(app):
    series = app.database().series()
    sel = app.selected('Series')
    metric = ['sum of squares', 'mutual information','interaction']
    cancel, f = app.dialog.input(
        {"label":"Moving series", "type":"select record", "options": series, 'default':sel},
        {"label":"Static series", "type":"select record", "options": series, 'default':sel},
        {"label":"Target region", "type":"select optional record", "options": series},
        {"label":"Apply transformation to:", "type":"select records", "options": series, 'default':[]},
        {"label":"Apply passive transformation?", "type":"dropdownlist", 'list':['Yes', 'No'], 'value':0},
        {"label":"Tolerance (smaller = slower but more accurate)", "type":"float", 'value':0.1, 'minimum':0.001}, 
        {"label":"Cost function", "type":"dropdownlist", 'list':metric, 'value':1}, 
        {"label":"Margin around target (mm)", "type":"float", 'value':0.0, 'minimum':0.0},
        {"label":"Preregister with 3D translation?", "type":"dropdownlist", 'list':['Yes', 'No'], 'value':0},
        title = "Please select coregistration parameters (rigid transformation)")
    if cancel:
        return
    params = vreg.find_rigid_transformation(f[0], f[1], 
            tolerance=f[5]["value"], 
            metric=metric[f[6]["value"]], 
            region=f[2],
            margin=f[7]['value'],
            prereg=f[8]['value']==0)

    # Save results as new dicom series
    f[0].message('Applying rigid transformation..')
    to_move = f[3] if f[0] in f[3] else [f[0]] + f[3]
    for series in to_move:
        if f[4]['value'] == 1:
            series_moved = vreg.apply_rigid_transformation(
                series, params, target=f[1])
        else:
            series_moved = vreg.apply_passive_rigid_transformation(
                series, params)
        app.display(series_moved)
    app.refresh()


def _sbs_translation(app):
    series = app.database().series()
    sel = app.selected('Series')
    metric = ['sum of squares', 'mutual information', 'interaction']
    cancel, f = app.dialog.input(
        {"label":"Moving series", "type":"select record", "options": series, 'default':sel},
        {"label":"Static series", "type":"select record", "options": series, 'default':sel},
        {"label":"Target region", "type":"select optional record", "options": series},
        {"label":"Apply transformation to:", "type":"select records", "options": series, 'default':[]},
        {"label":"Apply passive transformation?", "type":"dropdownlist", 'list':['Yes', 'No'], 'value':0},
        {"label":"Tolerance (smaller = slower but more accurate)", "type":"float", 'value':0.1, 'minimum':0.001}, 
        {"label":"Cost function", "type":"dropdownlist", 'list':metric, 'value':1}, 
        {"label":"Margin around target (mm)", "type":"float", 'value':0.0, 'minimum':0.0},
        {"label":"Preregister with 3D translation?", "type":"dropdownlist", 'list':['Yes', 'No'], 'value':0},
        title = "Please select coregistration parameters (slice-by-slice translation)")
    if cancel:
        return
    params = vreg.find_sbs_translation(f[0], f[1], 
            tolerance=f[5]["value"], 
            metric=metric[f[6]["value"]], 
            region=f[2],
            margin=f[7]['value'],
            prereg=f[8]['value']==0)

    # Save results as new dicom series
    f[0].message('Applying slice-by-slice translation..')
    to_move = f[3] if f[0] in f[3] else [f[0]] + f[3]
    for series in to_move:
        if f[4]['value'] == 1:
            series_moved = vreg.apply_sbs_translation(series, params, target=f[1])
        else:
            series_moved = vreg.apply_sbs_passive_translation(series, params)
        app.display(series_moved)
    app.refresh()

def _sbs_inslice_translation(app):
    series = app.database().series()
    sel = app.selected('Series')
    metric = ['sum of squares', 'mutual information', 'interaction']
    cancel, f = app.dialog.input(
        {"label":"Moving series", "type":"select record", "options": series, 'default':sel},
        {"label":"Static series", "type":"select record", "options": series, 'default':sel},
        {"label":"Target region", "type":"select optional record", "options": series},
        {"label":"Apply transformation to:", "type":"select records", "options": series, 'default':[]},
        {"label":"Apply passive transformation?", "type":"dropdownlist", 'list':['Yes', 'No'], 'value':0},
        {"label":"Tolerance (smaller = slower but more accurate)", "type":"float", 'value':0.1, 'minimum':0.001}, 
        {"label":"Cost function", "type":"dropdownlist", 'list':metric, 'value':1}, 
        {"label":"Margin around target (mm)", "type":"float", 'value':0.0, 'minimum':0.0},
        title = "Please select coregistration parameters (slice-by-slice inslice translation)")
    if cancel:
        return
    params = vreg.find_sbs_inslice_translation(f[0], f[1], 
            tolerance=f[5]["value"], 
            metric=metric[f[6]["value"]], 
            region=f[2],
            margin=f[7]['value'])

    # Save results as new dicom series
    f[0].message('Applying slice-by-slice translation..')
    to_move = f[3] if f[0] in f[3] else [f[0]] + f[3]
    for series in to_move:
        if f[4]['value'] == 1:
            series_moved = vreg.apply_sbs_inslice_translation(series, params, target=f[1])
        else:
            series_moved = vreg.apply_sbs_passive_inslice_translation(series, params)
        app.display(series_moved)
    app.refresh()



def _sbs_rigid(app):
    series = app.database().series()
    sel = app.selected('Series')
    metric = ['sum of squares', 'mutual information', 'interaction']
    cancel, f = app.dialog.input(
        {"label":"Moving series", "type":"select record", "options": series, 'default':sel},
        {"label":"Static series", "type":"select record", "options": series, 'default':sel},
        {"label":"Target region", "type":"select optional record", "options": series},
        {"label":"Apply transformation to:", "type":"select records", "options": series, 'default':[]},
        {"label":"Apply passive transformation?", "type":"dropdownlist", 'list':['Yes', 'No'], 'value':0},
        {"label":"Tolerance (smaller = slower but more accurate)", "type":"float", 'value':0.1, 'minimum':0.001}, 
        {"label":"Cost function", "type":"dropdownlist", 'list':metric, 'value':1}, 
        {"label":"Margin around target (mm)", "type":"float", 'value':0.0, 'minimum':0.0}, 
        {"label":"Prealign with 3D rigid registration?", "type":"dropdownlist", 'list':['Yes', 'No'], 'value':0},
        title = "Please select coregistration parameters (slice-by-slice rigid transformation)")
    if cancel:
        return
    
    if f[8]['value'] == 1:
        find_sbs_rigid = vreg.find_sbs_rigid_transformation
    else:
        find_sbs_rigid = vreg.find_sbs_rigid_transformation_with_prealign
    
    params = find_sbs_rigid(f[0], f[1], 
            tolerance=f[5]["value"], 
            metric=metric[f[6]["value"]], 
            resolutions=[1], 
            region=f[2],
            margin=f[7]['value'])
      
    # Save results as new dicom series
    f[0].message('Applying slice-by-slice translation..')
    to_move = f[3] if f[0] in f[3] else [f[0]] + f[3]
    for series in to_move:
        if f[4]['value'] == 1:
            series_moved = vreg.apply_sbs_rigid_transformation(series, params, target=f[1])
        else:
            series_moved = vreg.apply_sbs_passive_rigid_transformation(series, params)
        app.display(series_moved)
    app.refresh()


def _rigid_around_com_sos(app):
    series = app.database().series()
    sel = app.selected('Series')
    cancel, f = app.dialog.input(
        {"label":"Moving series", "type":"select record", "options": series, 'default':sel},
        {"label":"Static series", "type":"select record", "options": series, 'default':sel},
        {"label":"Tolerance (smaller = slower but more accurate)", "type":"float", 'value':0.1, 'minimum':0.001}, 
        title = "Please select coregistration parameters")
    if cancel:
        return
    coregistered = vreg.rigid_around_com_sos(f[0], f[1], tolerance=f[2]["value"])
    app.display(coregistered)
    app.refresh()


def _sbs_rigid_around_com_sos(app):
    series = app.database().series()
    sel = app.selected('Series')
    cancel, f = app.dialog.input(
        {"label":"Moving series", "type":"select record", "options": series, 'default':sel},
        {"label":"Static series", "type":"select record", "options": series, 'default':sel},
        {"label":"Tolerance (smaller = slower but more accurate)", "type":"float", 'value':0.1, 'minimum':0.001}, 
        title = "Please select coregistration parameters")
    if cancel:
        return
    coregistered = vreg.sbs_rigid_around_com_sos(f[0], f[1], tolerance=f[2]["value"])
    app.display(coregistered)
    app.refresh()


def _overlay_on(app):
    series = app.database().series()
    sel = app.selected('Series')
    cancel, f = app.dialog.input(
        {"label":"Overlay series..", "type":"select records", "options": series, 'default':sel},
        {"label":"On series..", "type":"select record", "options": series, 'default':sel}, 
        title = "Overlay series")
    if cancel:
        return
    for series in f[0]:
        mapped = vreg.map_to(series, f[1])
        app.display(mapped)
        app.refresh()


def _roi_statistics(app):
    all_series = app.database().series()
    cancel, f = app.dialog.input(
        {'label':'Regions of interest', 'type':'select records', 'options': all_series},
        {'label':'Parameters', 'type':'select records', 'options': all_series},
        title = "Please select input for ROI statistics")
    if cancel:
        return
    df = vreg.mask_statistics(f[0], f[1])
    app.addWidget(TableDisplay(df), 'ROI statistics')
    app.status.hide()


def _roi_histogram(app):
    all_series = app.database().series()
    cancel, f = app.dialog.input(
        {'label':"Region(s) of interest", "type":"select record", "options": all_series},
        {'label':"Series", "type":"select record", "options": all_series},
        {'label':'Number of bins', 'type': 'integer', 'value': 20},
        title = "Please select input for ROI histogram")
    if cancel:
        return
    data = vreg.mask_values(f[0], f[1]) 
    fig, ax = plt.subplots(1,1,figsize=(5,5))
    ax.hist(data, bins=f[2]['value'])
    app.addWidget(MatplotLibDisplay(fig), 'ROI histogram')
    app.status.hide()


action_overlay_on = Action('Overlay on..', on_clicked=_overlay_on, is_clickable=_if_a_database_is_open)
action_roi_statistics = Action('ROI statistics', on_clicked=_roi_statistics, is_clickable=_if_a_database_is_open)
action_roi_histogram = Action('ROI histogram', on_clicked=_roi_histogram, is_clickable=_if_a_database_is_open)

action_translation = Action('Translation', on_clicked=_translation, is_clickable=_if_a_database_is_open)
action_rigid = Action('Rigid transformation', on_clicked=_rigid, is_clickable=_if_a_database_is_open)
action_rigid_around_com_sos = Action('Rigid around center of mass (cost = sum of squares)', on_clicked=_rigid_around_com_sos, is_clickable=_if_a_database_is_open)

action_sbs_inslice_translation = Action('Slice-by-slice in-slice translation', on_clicked=_sbs_inslice_translation, is_clickable=_if_a_database_is_open)
action_sbs_translation = Action('Slice-by-slice translation', on_clicked=_sbs_translation, is_clickable=_if_a_database_is_open)
action_sbs_rigid = Action('Slice-by-slice rigid transformation', on_clicked=_sbs_rigid, is_clickable=_if_a_database_is_open)
action_sbs_rigid_around_com_sos = Action('Slice-by-slice rigid around center of mass (cost = sum of squares)', on_clicked=_sbs_rigid_around_com_sos, is_clickable=_if_a_database_is_open)


menu_meas = Menu('Measure (vreg)')
menu_meas.add(action_roi_statistics)
menu_meas.add(action_roi_histogram)

menu_coreg = Menu('Coregister (vreg)')
menu_coreg.add(action_overlay_on)
menu_coreg.add_separator()
menu_coreg.add(action_translation)

menu_coreg.add(action_sbs_translation)
menu_coreg.add_separator()
menu_coreg.add(action_rigid)
menu_coreg.add(action_sbs_rigid)
menu_coreg.add_separator()
menu_coreg.add(action_rigid_around_com_sos)
menu_coreg.add(action_sbs_rigid_around_com_sos)

menu_coreg_wip = Menu('Coregister (vreg)')
menu_coreg_wip.add(action_rigid_around_com_sos)
menu_coreg_wip.add(action_sbs_rigid_around_com_sos)
menu_coreg_wip.add(action_sbs_inslice_translation)