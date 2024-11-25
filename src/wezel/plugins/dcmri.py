import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import dcmri
from wezel.gui import Action, Menu
from wezel.displays import TableDisplay, MatplotLibDisplay

def if_series_is_selected(app):
    return app.nr_selected('Series') != 0

def if_database_is_open(app):
    return app.database() is not None

def _load_roi(dce, roi):
    dce.message('Loading ROI curve..')
    z, t = 'SliceLocation', 'AcquisitionTime'
    #z, t = 'SliceLocation', 'TriggerTime'
    roi, roiloc = roi.pixel_values(z, return_coords=True)
    array, coord = dce.pixel_values((z,t), slice=roiloc, return_coords=True)
    time = coord[t][0,:]
    mask = roi > 0.5
    curve = [np.mean(array[...,k][mask]) for k in range(array.shape[-1])]
    return time-time[0], np.array(curve)



def check_params(app):

    series = app.selected('Series')
    frame = series[0].instance()
    # Using codes as pydicom does not recognize contrast agent keywords
    tags = ('PatientWeight', (0x0018,0x0010), (0x0018,0x1041), (0x0018,0x1046), 'RepetitionTime', 'FlipAngle')

    cancel, fields = app.dialog.input(
        {"label":"Patient weight (kg)", "type":"float", "value":frame[tags[0]], "minimum": 1.0, "maximum": 200.0},
        {'label':'Contrast agent', 'type':'string', 'value':frame[tags[1]]},
        {"label":"Contrast agent dose (mL)", "type":"float", "value":frame[tags[2]], "minimum": 0.0, "maximum": 100.0},
        {"label":"Contrast agent injection rate (mL/sec)", "type":"float", "value":frame[tags[3]], "minimum": 0.0, "maximum": 10.0},
        {"label":"Repetition time (msec)", "type":"float", "value":frame[tags[4]], "minimum": 0.1, "maximum": 100.0},
        {"label":"Flip angle (degrees)", "type":"float", "value":frame[tags[5]], "minimum": 1, "maximum": 90.0},
        title = 'Please check input parameters',
    )
    if cancel:
        return
    
    vals = tuple([f['value'] for f in fields])
    series[0].set_values(vals, tags)


def descriptives(app):

    # Get user input
    sel = app.selected('Series')
    all = app.database().series()
    cancel, f = app.dialog.input(
        {'label':'DCE data', 'type':'select record', 'options':all, 'default':sel},
        {'label':'Nr of precontrast dynamics', 'type':'integer', 'value':2, 'minimum':1},
        {'label':'Relative to baseline?', 'type':'dropdownlist', 'list':['Yes','No'], 'value':1},
    )
    if cancel:
        return
    
    # Load data
    z, t = 'SliceLocation', 'AcquisitionTime'
    #z, t = 'SliceLocation', 'InstanceNumber'
    array, header = f[0].array([z, t], pixels_first=True, first_volume=True)

    # Calculate maps
    f[0].message('Calculating descriptive parameters..')
    relative = f[2]['value']==0
    maps = dcmri.pixel_descriptives(array, baseline=f[1]['value'], relative=relative)
    if relative:
        desc = ["MAX (%)", "AUC (% * sec)", "ATT (sec)", "S0 (au)"]
    else:
        desc = ["MAX (au)", "AUC (au * sec)", "ATT (sec)", "S0 (au)"]

    # Save results as DICOM
    for m, map in enumerate(maps):
        series = f[0].new_sibling(SeriesDescription=desc[m])
        series.set_array(map, header[:,0], pixels_first=True)
        app.display(series)
    app.refresh()


def plot_roi(app):

    # Get user input
    sel = app.selected('Series')
    all = app.database().series()
    cancel, f = app.dialog.input(
        {'label':'DCE data', 'type':'select record', 'options':all, 'default':sel},
        {'label':'ROI mask', 'type':'select record', 'options':all, 'default':sel},
    )
    if cancel:
        return
    
    # Load data
    time, curve = _load_roi(f[0], f[1])

    # Create plot
    desc= f[1].instance().SeriesDescription
    fig, ax = plt.subplots(1,1,figsize=(5,5))
    ax.plot(time/60, curve, 'ro', label='Signal for ' + desc, markersize=3)
    ax.plot(time/60, curve, 'r-', linewidth=2)
    #ax.plot(time/60, fit, 'b-', label='Fit for aorta', linewidth=2)
    ax.set(xlabel='Time (min)', ylabel='Signal (a.u.)')
    ax.legend()
 
    app.addWidget(MatplotLibDisplay(fig), 'ROI signal')
    app.refresh()



def deconvolve(app):

    # Get user input
    sel = app.selected('Series')
    all = app.database().series()
    cancel, f = app.dialog.input(
        {'label':'DCE data', 'type':'select record', 'options':all, 'default':sel},
        {'label':'AIF', 'type':'select record', 'options':all, 'default':sel},
        {'label':'Nr of precontrast dynamics', 'type':'integer', 'default':2, 'minimum':1},
    )
    if cancel:
        return
    
    # Load data
    z, t = 'SliceLocation', 'AcquisitionTime'
    #z, t = 'SliceLocation', 'InstanceNumber'
    array, header = f[0].array([z, t], pixels_first=True, first_volume=True)
    time, aif = _load_roi(f[0], f[1])

    # Calculate maps
    f[0].message('Deconvolving..')
    maps = dcmri.pixel_deconvolve(array, aif, time[2]-time[1], baseline=f[2]['value'])
    desc = ["PF (mL/min/100mL)", "VD (mL/100mL)", "TT (sec)"]

    # Save results as DICOM
    for m, map in enumerate(maps):
        series = f[0].new_sibling(SeriesDescription=desc[m])
        series.set_array(map, header[:,0], pixels_first=True)
        app.display(series)
    app.refresh()


def fit_aif(app):

    # Get user input
    sel = app.selected('Series')
    all = app.database().series()
    cancel, f = app.dialog.input(
        {'label':'DCE data', 'type':'select record', 'options':all, 'default':sel},
        {'label':'AIF', 'type':'select record', 'options':all, 'default':sel},
        {'label':'Nr of precontrast dynamics', 'type':'integer', 'default':2, 'minimum':1},
        {"label":"Blood T1 (msec)", "type":"float", "value":1000*dcmri.T1(), "minimum": 0.0, "maximum": 3000.0},
    )
    if cancel:
        return
    
    # Get data
    time, aif = _load_roi(f[0], f[1])

    frame = f[0].instance()
    kwargs = {
        'R10': 1000/f[3]['value'], #1/sec
        'weight': frame.PatientWeight,
        'agent': frame[(0x0018,0x0010)],
        'dose': frame[(0x0018,0x1041)]/frame.PatientWeight,
        'rate': frame[(0x0018,0x1046)],
        'TR': frame.RepetitionTime/1000,
        'FA': frame.FlipAngle,
    }
    
    # Calculate fit
    pars, _, fit = dcmri.fit_aorta_signal_8(time, aif, parset='TRISTAN', baseline=f[2]['value'], **kwargs)
    t, ca = dcmri.aorta_signal_8(time, *pars, return_conc=True, **kwargs)

    # Show parameters
    params = [
        'Bolus arrival time (sec)', 
        'Cardiac output (mL/sec)', 
        'Heart & Lung mean transit time (sec)', 
        'Heart & Lung transit time dispersion', 
        'Organs extraction fraction', 
        'Organs blood transit time (sec)', 
        'Organs extracellular transit time (sec)', 
        'Body extraction fraction',
    #    'Residence time (sec)',
    ]
    data = {
        'Parameter': params,
        'Value': pars,
    }
    app.addWidget(TableDisplay(data), 'AIF model fit')

    # Plot fit
    desc = f[1].instance().SeriesDescription
    fig, ax = plt.subplots(1,1,figsize=(5,5))
    ax.plot(time/60, aif, 'ro', label='Signal for ' + desc, markersize=3)
    ax.plot(time/60, fit, 'b-', label='Fit for aorta', linewidth=2)
    ax.set(xlabel='Time (min)', ylabel='Signal (a.u.)')
    ax.legend()    
    app.addWidget(MatplotLibDisplay(fig), 'AIF model fit')

    # Plot concentration
    fig, ax = plt.subplots(1,1,figsize=(5,5))
    ax.plot(t/60, ca*1000, 'r-', label='Signal for ' + desc, linewidth=2)
    ax.set(xlabel='Time (min)', ylabel='Concentration (mM)')
    ax.legend()    
    app.addWidget(MatplotLibDisplay(fig), 'AIF reconstructed concentrations')

    app.refresh()


def fit_roi(app):

    # Get user input
    sel = app.selected('Series')
    all = app.database().series()
    cancel, f = app.dialog.input(
        {'label':'DCE data', 'type':'select record', 'options':all, 'default':sel},
        {'label':'AIF', 'type':'select record', 'options':all, 'default':sel},
        {'label':'ROI', 'type':'select record', 'options':all, 'default':sel},
        {'label':'Nr of precontrast dynamics', 'type':'integer', 'default':2, 'minimum':2},
        {"label":"Blood T1 (msec)", "type":"float", "value":1000*dcmri.T1(), "minimum": 0.0, "maximum": 3000.0},
        {"label":"Tissue T1 (msec)", "type":"float", "value":1000, "minimum": 0.0, "maximum": 3000.0},
    )
    if cancel:
        return
    
    # Read constants and ask the user to check the values
    time, aif = _load_roi(f[0], f[1])
    frame = f[0].instance()
    kwargs = {
        'R10': 1000/f[4]['value'], #1/sec
        'weight': frame.PatientWeight,
        'agent': frame[(0x0018,0x0010)],
        'dose': frame[(0x0018,0x1041)]/frame.PatientWeight,
        'rate': frame[(0x0018,0x1046)],
        'TR': frame.RepetitionTime/1000,
        'FA': frame.FlipAngle,
    }
    # Fit AIF concentration
    pars, _, _ = dcmri.fit_aorta_signal_8(time, aif, parset='TRISTAN', baseline=f[3]['value'], **kwargs)
    aif = dcmri.aorta_signal_8(time, *pars, return_conc=True, **kwargs)

    # Calculate tissue fit
    time, roi = _load_roi(f[0], f[2])
    kwargs = {
        'aif': aif,
        'R10': 1000/f[5]['value'], #1/sec
        'agent': frame[(0x0018,0x0010)],
        'TR': frame.RepetitionTime/1000, #sec
        'FA': frame.FlipAngle, #deg
    }
    pars, _, fit = dcmri.fit_tissue_signal_3(time, roi, parset='bladder', baseline=f[3]['value'], **kwargs)
    roiconc = dcmri.tissue_signal_3(time, *pars, return_conc=True, **kwargs)

    # Show parameters
    params = [
        'Plasma volume vp (mL/100mL)', 
        'Transfer constant Ktrans (mL/min/100mL)', 
        'Extracellular volume ve (mL/100mL)', 
    ]
    data = {
        'Parameter': params,
        'Value': [pars[0]*100, pars[1]*6000, pars[2]*100],
    }
    app.addWidget(TableDisplay(data), 'ROI model fit')

    # Plot AIF concentrations
    desc = f[1].instance().SeriesDescription
    fig, ax = plt.subplots(1,1,figsize=(5,5))
    ax.plot(aif[0]/60, aif[1]*1000, 'r-', label='Concentration for ' + desc, linewidth=2)
    ax.set(xlabel='Time (min)', ylabel='Concentration (mM)')
    ax.legend()    
    app.addWidget(MatplotLibDisplay(fig), 'AIF reconstructed concentrations')

    # Plot tissue concentrations
    desc = f[2].instance().SeriesDescription
    fig, ax = plt.subplots(1,1,figsize=(5,5))
    ax.plot(roiconc[0]/60, roiconc[1]*1000, 'r-', label='Concentration for ' + desc, linewidth=2)
    ax.set(xlabel='Time (min)', ylabel='Concentration (mM)')
    ax.legend()    
    app.addWidget(MatplotLibDisplay(fig), 'ROI reconstructed concentrations')

    # Plot fit
    fig, ax = plt.subplots(1,1,figsize=(5,5))
    ax.plot(time/60, roi, 'ro', label='Signal for ' + desc, markersize=3)
    ax.plot(time/60, fit, 'b-', label='Fit for ROI', linewidth=2)
    ax.set(xlabel='Time (min)', ylabel='Signal (a.u.)')
    ax.legend()    
    app.addWidget(MatplotLibDisplay(fig), 'ROI model fit')

    app.refresh()


action_check_params = Action('Check parameters..', on_clicked=check_params, is_clickable=if_series_is_selected)
action_descriptives = Action('Descriptives..', on_clicked=descriptives, is_clickable=if_database_is_open)
action_plot_roi = Action('Plot ROI..', on_clicked=plot_roi, is_clickable=if_database_is_open)
action_deconvolve = Action('Model-free mapping..', on_clicked=deconvolve, is_clickable=if_database_is_open)
action_fit_aif = Action('Fit AIF..', on_clicked=fit_aif, is_clickable=if_database_is_open)
action_fit_roi = Action('Fit ROI..', on_clicked=fit_roi, is_clickable=if_database_is_open)


menu = Menu('dcMRI')
menu.add(action_check_params)
menu.add(action_descriptives)
menu.add(action_plot_roi)
menu.add(action_deconvolve)
menu.add(action_fit_aif)
menu.add(action_fit_roi)


