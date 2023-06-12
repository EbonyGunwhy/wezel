import numpy as np
from dbdicom.wrappers import scipy

from wezel.displays import TableDisplay, PlotDisplay
from wezel.gui import Action, Menu


def _if_a_series_is_selected(app):
    return app.nr_selected('Series') != 0


def _if_a_database_is_open(app): 
    return app.database() is not None


def _roi_curve(app):
    all_series = app.database().series()
    cancel, f = app.dialog.input(
        {'label':"Region(s) of interest", "type":"select records", "options": all_series},
        {'label':"Series", "type":"select records", "options": all_series},
        {'label':'Curve along dimension..', 'type':'string', 'value':'AcquisitionTime'},
        title = "Please select input for ROI curves")
    if cancel:
        return
    dim = f[2]['value']
    data = scipy.mask_curve_3d(f[0], f[1], dim=dim) 
    app.addWidget(TableDisplay(data), 'ROI curves - data')
    for df in data:
        series = df['SeriesDescription'].values[0]
        region = df['Region of Interest'].values[0]
        plot = PlotDisplay(df[dim].values, df['Mean'].values)
        plot.set_xlabel(dim)
        plot.set_ylabel(series)
        plot.draw()
        title = 'ROI: ' + region
        app.addWidget(plot, title)
    app.status.hide()


def _roi_statistics(app):
    all_series = app.database().series()
    cancel, f = app.dialog.input(
        {'label':'Regions of interest', 'type':'select records', 'options': all_series},
        {'label':'Parameters', 'type':'select records', 'options': all_series},
        title = "Please select input for ROI statistics")
    if cancel:
        return
    df = scipy.mask_statistics(f[0], f[1])
    app.addWidget(TableDisplay(df), 'ROI statistics')
    app.status.hide()


def _function_of_one_series(app):
    operation = [
        '1 - series', 
        '- series',
        '1 / series',
        'exp(- series)',
        'exp(+ series)',
        'integer(series)',
        ]
    cancel, f = app.dialog.input(
        {"label":"Operation: ", "type":"dropdownlist", "list": operation, 'value':0},
        title = "Please select operation")
    if cancel:
        return
    operation = operation[f[0]["value"]]
    for series in app.selected('Series'):
        result = scipy.series_calculator(series, operation)
        app.display(result)
    app.refresh()


def _function_of_two_series(app):
    series = app.database().series()
    sel = app.selected('Series')
    if len(sel) == 0:
        sel = 2*[series[0]]
    elif len(sel) == 1:
        sel = 2*[sel[0]]
    else:
        sel = sel[:2]
    operation = [
        'series 1 + series 2', 
        'series 1 - series 2',
        'series 1 / series 2',
        'series 1 * series 2',
        '(series 1 - series 2)/series 2',
        'average(series 1, series 2)',
        ]
    cancel, f = app.dialog.input(
        {"label":"series 1", "type":"select record", "options": series, 'default':sel[0]},
        {"label":"series 2", "type":"select record", "options": series, 'default':sel[1]},
        {"label":"Operation: ", "type":"dropdownlist", "list": operation, 'value':1},
        title = "Please select factors and operation")
    if cancel:
        return
    result = scipy.image_calculator(f[0], f[1], operation[f[2]["value"]])
    app.display(result)
    app.refresh()


def _function_of_n_series(app):
    series = app.database().series()
    sel = app.selected('Series')
    operation = [
        'sum', 
        'mean',
        ]
    cancel, f = app.dialog.input(
        {"label":"series", "type":"select records", "options": series, 'default':sel},
        {"label":"Operation: ", "type":"dropdownlist", "list": operation, 'value':1},
        title = "Please select factors and operation")
    if cancel:
        return
    result = scipy.n_images_calculator(f[0], operation[f[1]["value"]])
    app.display(result)
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
        mapped = scipy.map_to(series, f[1])
        app.display(mapped)
        app.refresh()


def _resample_3d(app):
    for series in app.selected('Series'):
        cancel, f = app.dialog.input(
            {"label":"New voxel size in mm (height)", "type":"float", 'value':1.0, 'minimum':0.01}, 
            {"label":"New voxel size in mm (width)", "type":"float", 'value':1.0, 'minimum':0.01},
            {"label":"New voxel size in mm (depth)", "type":"float", 'value':1.0, 'minimum':0.01},
            title = "Please select new voxel size")
        if cancel:
            return
        voxel_size = [f[0]["value"], f[1]["value"], f[2]["value"]]
        resliced = scipy.resample(series, voxel_size=voxel_size)
        app.display(resliced)
    app.refresh()


def _resample_3d_isotropic(app):
    for series in app.selected('Series'):
        cancel, f = app.dialog.input(
            {"label":"New voxel size (mm)", "type":"float", 'value':1.0, 'minimum':0.01}, 
            title = "Please select new voxel size")
        if cancel:
            return
        voxel_size = [f[0]["value"], f[0]["value"], f[0]["value"]]
        resliced = scipy.resample(series, voxel_size=voxel_size)
        app.display(resliced)
    app.refresh()


def _reslice_axial(app):
    for series in app.selected('Series'):
        resliced = scipy.reslice(series, orientation='axial')
        app.display(resliced)
    app.refresh()


def _reslice_coronal(app):
    for series in app.selected('Series'):
        resliced = scipy.reslice(series, orientation='coronal')
        app.display(resliced)
    app.refresh()


def _reslice_sagittal(app):
    for series in app.selected('Series'):
        resliced = scipy.reslice(series, orientation='sagittal')
        app.display(resliced)
    app.refresh()


def _zoom(app):

    # Get user input
    cancel, f = app.dialog.input(
        {"type":"float", "label":"Resize with factor..", "value":2.0, "minimum": 0},
        title='Select parameter ranges')
    if cancel: 
        return
    factor = f[0]['value']

    # Resize series
    series = app.selected('Series')
    for sery in series:
        resized = scipy.zoom(sery, factor)
        app.display(resized)
    app.refresh()


def _fourier_shift(app):

    # Default settings
    hshift = 64
    vshift = 64

    # Get user input
    cancel, f = app.dialog.input(
        {"label":"horizontal shift", "type":"float", "value":hshift},
        {"label":"vertical shift", "type":"float", "value":vshift},
        title = 'Select Sobel Filter settings')
    if cancel: 
        return

    # update defaults
    hshift = f[0]['value']
    vshift = f[1]['value']

    # Filter series
    series = app.selected('Series')
    for sery in series:
        resized = scipy.fourier_shift(
            sery, [hshift, vshift],
        )
        app.display(resized)
    app.refresh()


def _distance_transform_edit_3d(app):
    series = app.selected('Series')
    for sery in series:
        transformed = scipy.distance_transform_edt_3d(sery)
        app.display(transformed)
    app.refresh()


def _binary_fill_holes(app):

    # Get user input
    cancel, f = app.dialog.input(
        {   "label": "Size of the structuring element", 
            "type": "dropdownlist", 
            "list": ['1 pixel', '3 pixels', '5 pixels'], 
            "value": 0,
        },
        title = 'Select settings for filling holes.')
    if cancel: 
        return

    # update defaults
    if f[0]['value'] == 0:
        structure = None
    elif f[0]['value'] == 1:
        structure = np.array([   
            [0,1,0],
            [1,1,1],
            [0,1,0]])
    elif f[0]['value'] == 2:
        structure = np.array([   
            [0,0,1,0,0],
            [0,1,1,1,0],
            [1,1,1,1,1],
            [0,1,1,1,0],
            [0,0,1,0,0]])
    
    # Filter series
    series = app.selected('Series')
    for sery in series:
        filtered = scipy.binary_fill_holes(
            sery, 
            structure=structure
        )
        app.display(filtered)
    app.refresh()


def _label_2d(app):

    # Get user input
    cancel, f = app.dialog.input(
        {   "label": "Size of the structuring element", 
            "type": "dropdownlist", 
            "list": [
                    '3 pixels (plus)', 
                    '3 pixels (square)', 
                    '5 pixels (diamond)', 
                    '5 pixels (fat plus)',
                    '5 pixels (square)',
                    ], 
            "value": 0,
        },
        title = 'Select settings for image labelling.')
    if cancel: 
        return

    # update defaults
    if f[0]['value'] == 0:
        structure = np.array([   
            [0,1,0],
            [1,1,1],
            [0,1,0]])
    if f[0]['value'] == 1:
        structure = np.array([   
            [1,1,1],
            [1,1,1],
            [1,1,1]])
    elif f[0]['value'] == 2:
        structure = np.array([   
            [0,0,1,0,0],
            [0,1,1,1,0],
            [1,1,1,1,1],
            [0,1,1,1,0],
            [0,0,1,0,0]])
    elif f[0]['value'] == 3:
        structure = np.array([   
            [0,1,1,1,0],
            [1,1,1,1,1],
            [1,1,1,1,1],
            [1,1,1,1,1],
            [0,1,1,1,0]])
    elif f[0]['value'] == 4:
        structure = np.array([   
            [1,1,1,1,1],
            [1,1,1,1,1],
            [1,1,1,1,1],
            [1,1,1,1,1],
            [1,1,1,1,1]])
    
    # Filter series
    series = app.selected('Series')
    for sery in series:
        filtered = scipy.label_2d(
            sery, 
            structure=structure
        )
        app.display(filtered)
    app.refresh()


def _label_3d(app):
    series = app.selected('Series')
    for sery in series:
        result = scipy.label_3d(sery)
        app.display(result)
    app.refresh()


def _extract_largest_cluster_3d(app):
    series = app.selected('Series')
    for sery in series:
        result = scipy.extract_largest_cluster_3d(sery)
        app.display(result)
    app.refresh()


def _fourier_ellipsoid_filter(app):

    # Default settings
    size = 2.0

    # Get user input
    cancel, f = app.dialog.input(
        {"label":"size (of ellipsoid kernel)", "type":"float", "value":size, "minimum": 1.0},
        title = 'Select Fourier Ellipsoid Filter settings')
    if cancel: 
        return

    # update defaults
    size = f[0]['value']

    # Filter series
    series = app.selected('Series')
    for sery in series:
        resized = scipy.fourier_ellipsoid(
            sery, size,
        )
        app.display(resized)
    app.refresh()


def _fourier_uniform_filter(app):

    # Default settings
    size = 2.0

    # Get user input
    cancel, f = app.dialog.input(
        {"label":"size (of uniform kernel)", "type":"float", "value":size, "minimum": 1.0},
        title = 'Select Fourier Uniform Filter settings')
    if cancel: 
        return

    # update defaults
    size = f[0]['value']

    # Filter series
    series = app.selected('Series')
    for sery in series:
        resized = scipy.fourier_uniform(
            sery, size,
        )
        app.display(resized)
    app.refresh()


def _fourier_gaussian_filter(app):

    # Default settings
    sigma = 2.0

    # Get user input
    cancel, f = app.dialog.input(
        {"label":"sigma (standard deviation for Gaussian kernel)", "type":"float", "value":sigma, "minimum": 1.0},
        title = 'Select Fourier Gaussian Filter settings')
    if cancel: 
        return

    # update defaults
    sigma = f[0]['value']

    # Filter series
    series = app.selected('Series')
    for sery in series:
        resized = scipy.fourier_gaussian(
            sery, sigma,
        )
        app.display(resized)
    app.refresh()


def _gaussian_gradient_magnitude_filter(app):

    # Default settings
    modes = ['reflect', 'constant', 'nearest', 'mirror', 'wrap']
    sigma = 2.0
    mode = 0
    cval = 0.0

    # Get user input
    cancel, f = app.dialog.input(
        {"label":"sigma (standard deviation for Gaussian kernel)", "type":"float", "value":sigma, "minimum": 1.0},
        {"label":"mode (of extension at border)", "type":"dropdownlist", "list": modes, "value": mode},
        {"label":"cval (value past edges in constant mode)", "type":"float", "value":cval},
        title = 'Select Gaussian Gradient Magnitude Filter settings')
    if cancel: 
        return

    # update defaults
    sigma = f[0]['value']
    mode = f[1]['value']
    cval = f[2]['value']

    # Filter series
    series = app.selected('Series')
    for sery in series:
        resized = scipy.gaussian_gradient_magnitude(
            sery, sigma,
            mode = modes[mode],
            cval = cval,
        )
        app.display(resized)
    app.refresh()


def _gaussian_laplace_filter(app):

    # Default settings
    modes = ['reflect', 'constant', 'nearest', 'mirror', 'wrap']
    sigma = 2.0
    mode = 1
    cval = 0.0

    # Get user input
    cancel, f = app.dialog.input(
        {"label":"sigma (standard deviation for Gaussian kernel)", "type":"float", "value":sigma, "minimum": 1.0},
        {"label":"mode (of extension at border)", "type":"dropdownlist", "list": modes, "value": mode},
        {"label":"cval (value past edges in constant mode)", "type":"float", "value":cval},
        title = 'Select Gaussian Laplace Filter settings')
    if cancel: 
        return

    # update defaults
    sigma = f[0]['value']
    mode = f[1]['value']
    cval = f[2]['value']

    # Filter series
    series = app.selected('Series')
    for sery in series:
        resized = scipy.gaussian_laplace(
            sery, sigma,
            mode = modes[mode],
            cval = cval,
        )
        app.display(resized)
    app.refresh()


def _laplace_filter(app):

    # Default settings
    modes = ['reflect', 'constant', 'nearest', 'mirror', 'wrap']
    mode = 1
    cval = 0.0

    # Get user input
    cancel, f = app.dialog.input(
        {"label":"mode (of extension at border)", "type":"dropdownlist", "list": modes, "value": mode},
        {"label":"cval (value past edges in constant mode)", "type":"float", "value":cval},
        title = 'Select Laplace Filter settings')
    if cancel: 
        return

    # update defaults
    mode = f[0]['value']
    cval = f[1]['value']

    # Filter series
    series = app.selected('Series')
    for sery in series:
        resized = scipy.laplace(
            sery,
            mode = modes[mode],
            cval = cval,
        )
        app.display(resized)
    app.refresh()


def _sobel_filter(app):

    # Default settings
    modes = ['reflect', 'constant', 'nearest', 'mirror', 'wrap']
    axis = 0
    mode = 1
    cval = 0.0

    # Get user input
    cancel, f = app.dialog.input(
        {"label":"axis", "type":"dropdownlist", "list":['Horizontal', 'Vertical'], "value":axis},
        {"label":"mode (of extension at border)", "type":"dropdownlist", "list": modes, "value": mode},
        {"label":"cval (value past edges in constant mode)", "type":"float", "value":cval},
        title = 'Select Sobel Filter settings')
    if cancel: 
        return

    # update defaults
    axis = f[0]['value']
    mode = f[1]['value']
    cval = f[2]['value']

    # Filter series
    series = app.selected('Series')
    for sery in series:
        resized = scipy.sobel_filter(
            sery,
            axis = axis,
            mode = modes[mode],
            cval = cval,
        )
        app.display(resized)
    app.refresh()


def _prewitt_filter(app):

    # Default settings
    modes = ['reflect', 'constant', 'nearest', 'mirror', 'wrap']
    axis = 0
    mode = 1
    cval = 0.0

    # Get user input
    cancel, f = app.dialog.input(
        {"label":"axis", "type":"dropdownlist", "list":['Horizontal', 'Vertical'], "value":axis},
        {"label":"mode (of extension at border)", "type":"dropdownlist", "list": modes, "value": mode},
        {"label":"cval (value past edges in constant mode)", "type":"float", "value":cval},
        title = 'Select Prewitt Filter settings')
    if cancel: 
        return

    # update defaults
    axis = f[0]['value']
    mode = f[1]['value']
    cval = f[2]['value']

    # Filter series
    series = app.selected('Series')
    for sery in series:
        resized = scipy.prewitt_filter(
            sery,
            axis = axis,
            mode = modes[mode],
            cval = cval,
        )
        app.display(resized)
    app.refresh()


def _median_filter(app):

    # Default settings
    modes = ['reflect', 'constant', 'nearest', 'mirror', 'wrap']
    size = 3
    mode = 1
    cval = 0.0
    hshift = 0
    vshift = 0

    # Get user input & check if valid
    valid = False
    while not valid:
        # Get input
        cancel, f = app.dialog.input(
            {"label":"size (of the median filter)", "type":"integer", "value":size, "minimum": 1},
            {"label":"mode (of extension at border)", "type":"dropdownlist", "list": modes, "value": mode},
            {"label":"cval (value past edges in constant mode)", "type":"float", "value":cval},
            {"label":"horizontal shift (positive = to the left)", "type":"integer", "value":hshift},
            {"label":"vertical shift (positive = downwards)", "type":"integer", "value":vshift},
            title = 'Select Median Filter settings')
        if cancel: 
            return
        # update defaults
        size = f[0]['value']
        mode = f[1]['value']
        cval = f[2]['value']
        hshift = f[3]['value']
        vshift = f[4]['value']
        # check validity
        valid = (abs(hshift) < size/2.0) and (abs(vshift) < size/2.0)
        if not valid:
            msg = 'Invalid shift value: shifts must be less than half of the size'
            app.dialog.information(msg, 'Invalid input value')

    # Filter series
    series = app.selected('Series')
    for sery in series:
        resized = scipy.median_filter(
            sery,
            size = size,
            mode = modes[mode],
            cval = cval,
            origin = [hshift, vshift],
        )
        app.display(resized)
    app.refresh()


def _percentile_filter(app):

    # Default settings
    modes = ['reflect', 'constant', 'nearest', 'mirror', 'wrap']
    percentile = 50
    size = 3
    mode = 1
    cval = 0.0
    hshift = 0
    vshift = 0

    # Get user input & check if valid
    valid = False
    while not valid:
        # Get input
        cancel, f = app.dialog.input(
            {"label":"percentile", "type":"float", "value":percentile, 'minimum':0, 'maximum':100},
            {"label":"size (of the percentile filter)", "type":"integer", "value":size, "minimum": 1},
            {"label":"mode (of extension at border)", "type":"dropdownlist", "list": modes, "value": mode},
            {"label":"cval (value past edges in constant mode)", "type":"float", "value":cval},
            {"label":"horizontal shift (positive = to the left)", "type":"integer", "value":hshift},
            {"label":"vertical shift (positive = downwards)", "type":"integer", "value":vshift},
            title = 'Select Percentile Filter settings')
        if cancel: 
            return
        # update defaults
        percentile = f[0]['value']
        size = f[1]['value']
        mode = f[2]['value']
        cval = f[3]['value']
        hshift = f[4]['value']
        vshift = f[5]['value']
        # check validity
        valid = (abs(hshift) < size/2.0) and (abs(vshift) < size/2.0)
        if not valid:
            msg = 'Invalid shift value: shifts must be less than half of the size'
            app.dialog.information(msg, 'Invalid input value')

    # Filter series
    series = app.selected('Series')
    for sery in series:
        resized = scipy.percentile_filter(
            sery, percentile,
            size = size,
            mode = modes[mode],
            cval = cval,
            origin = [hshift, vshift],
        )
        app.display(resized)
    app.refresh()


def _rank_filter(app):

    # Default settings
    modes = ['reflect', 'constant', 'nearest', 'mirror', 'wrap']
    rank = 3
    size = 6
    mode = 1
    cval = 0.0
    hshift = 0
    vshift = 0

    # Get user input & check if valid
    valid = False
    while not valid:
        # Get input
        cancel, f = app.dialog.input(
            {"label":"rank", "type":"integer", "value":rank},
            {"label":"size (of the rank filter)", "type":"integer", "value":size, "minimum": 1},
            {"label":"mode (of extension at border)", "type":"dropdownlist", "list": modes, "value": mode},
            {"label":"cval (value past edges in constant mode)", "type":"float", "value":cval},
            {"label":"horizontal shift (positive = to the left)", "type":"integer", "value":hshift},
            {"label":"vertical shift (positive = downwards)", "type":"integer", "value":vshift},
            title = 'Select Rank Filter settings')
        if cancel: 
            return
        # update defaults
        rank = f[0]['value']
        size = f[1]['value']
        mode = f[2]['value']
        cval = f[3]['value']
        hshift = f[4]['value']
        vshift = f[5]['value']
        # check validity
        valid = (abs(hshift) < size/2.0) and (abs(vshift) < size/2.0)
        if not valid:
            msg = 'Invalid shift value: shifts must be less than half of the size'
            app.dialog.information(msg, 'Invalid input value')

    # Filter series
    series = app.selected('Series')
    for sery in series:
        try:
            resized = scipy.rank_filter(
                sery, rank,
                size = size,
                mode = modes[mode],
                cval = cval,
                origin = [hshift, vshift],
            )
        except Exception as e:
            msg = str(e) + '\n Please try again with different parameters'
            app.dialog.information(msg)
        else:
            app.display(resized)
    app.refresh()


def _maximum_filter(app):

    # Default settings
    modes = ['reflect', 'constant', 'nearest', 'mirror', 'wrap']
    size = 3
    mode = 1
    cval = 0.0
    hshift = 0
    vshift = 0

    # Get user input & check if valid
    valid = False
    while not valid:
        # Get input
        cancel, f = app.dialog.input(
            {"label":"size (of the maximum filter)", "type":"integer", "value":size, "minimum": 1},
            {"label":"mode (of extension at border)", "type":"dropdownlist", "list": modes, "value": mode},
            {"label":"cval (value past edges in constant mode)", "type":"float", "value":cval},
            {"label":"horizontal shift (positive = to the left)", "type":"integer", "value":hshift},
            {"label":"vertical shift (positive = downwards)", "type":"integer", "value":vshift},
            title = 'Select Maximum Filter settings')
        if cancel: 
            return
        # update defaults
        size = f[0]['value']
        mode = f[1]['value']
        cval = f[2]['value']
        hshift = f[3]['value']
        vshift = f[4]['value']
        # check validity
        valid = (abs(hshift) < size/2.0) and (abs(vshift) < size/2.0)
        if not valid:
            msg = 'Invalid shift value: shifts must be less than half of the size'
            app.dialog.information(msg, 'Invalid input value')

    # Filter series
    series = app.selected('Series')
    for sery in series:
        resized = scipy.maximum_filter(
            sery, 
            size = size,
            mode = modes[mode],
            cval = cval,
            origin = [hshift, vshift],
        )
        app.display(resized)
    app.refresh()


def _minimum_filter(app):

    # Default settings
    modes = ['reflect', 'constant', 'nearest', 'mirror', 'wrap']
    size = 3
    mode = 1
    cval = 0.0
    hshift = 0
    vshift = 0

    # Get user input & check if valid
    valid = False
    while not valid:
        # Get input
        cancel, f = app.dialog.input(
            {"label":"size (of the minimum filter)", "type":"integer", "value":size, "minimum": 1},
            {"label":"mode (of extension at border)", "type":"dropdownlist", "list": modes, "value": mode},
            {"label":"cval (value past edges in constant mode)", "type":"float", "value":cval},
            {"label":"horizontal shift (positive = to the left)", "type":"integer", "value":hshift},
            {"label":"vertical shift (positive = downwards)", "type":"integer", "value":vshift},
            title = 'Select Minimum Filter settings')
        if cancel: 
            return
        # update defaults
        size = f[0]['value']
        mode = f[1]['value']
        cval = f[2]['value']
        hshift = f[3]['value']
        vshift = f[4]['value']
        # check validity
        valid = (abs(hshift) < size/2.0) and (abs(vshift) < size/2.0)
        if not valid:
            msg = 'Invalid shift value: shifts must be less than half of the size'
            app.dialog.information(msg, 'Invalid input value')

    # Filter series
    series = app.selected('Series')
    for sery in series:
        resized = scipy.minimum_filter(
            sery, 
            size = size,
            mode = modes[mode],
            cval = cval,
            origin = [hshift, vshift],
        )
        app.display(resized)
    app.refresh()


def _uniform_filter(app):

    # Default settings
    modes = ['reflect', 'constant', 'nearest', 'mirror', 'wrap']
    size = 3
    mode = 1
    cval = 0.0
    hshift = 0
    vshift = 0

    # Get user input & check if valid
    valid = False
    while not valid:
        # Get input
        cancel, f = app.dialog.input(
            {"label":"size (of the uniform filter)", "type":"integer", "value":size, "minimum": 1},
            {"label":"mode (of extension at border)", "type":"dropdownlist", "list": modes, "value": mode},
            {"label":"cval (value past edges in constant mode)", "type":"float", "value":cval},
            {"label":"horizontal shift (positive = to the left)", "type":"integer", "value":hshift},
            {"label":"vertical shift (positive = downwards)", "type":"integer", "value":vshift},
            title = 'Select Uniform Filter settings')
        if cancel: 
            return
        # update defaults
        size = f[0]['value']
        mode = f[1]['value']
        cval = f[2]['value']
        hshift = f[3]['value']
        vshift = f[4]['value']
        # check validity
        valid = (abs(hshift) < size/2.0) and (abs(vshift) < size/2.0)
        if not valid:
            msg = 'Invalid shift value: shifts must be less than half of the size'
            app.dialog.information(msg, 'Invalid input value')

    # Filter series
    series = app.selected('Series')
    for sery in series:
        resized = scipy.uniform_filter(
            sery, 
            size = size,
            mode = modes[mode],
            cval = cval,
            origin = [hshift, vshift],
        )
        app.display(resized)
    app.refresh()


def _gaussian_filter(app):

    # Get user input
    modes = ['reflect', 'constant', 'nearest', 'mirror', 'wrap']
    cancel, f = app.dialog.input(
        {"label":"sigma (standard deviation for Gaussian kernel)", "type":"float", "value":2.0, "minimum": 1.0},
        {"label":"order (0 = Gaussian, n = nth derivative of Gaussian)", "type":"integer", "value":0, "minimum": 0},
        {"label":"mode (of extension at border)", "type":"dropdownlist", "list": modes, "value": 1},
        {"label":"cval (value past edges in constant mode)", "type":"float", "value":0.0},
        {"label":"truncate (at this many standard deviations)", "type":"float", "value":4.0, "minimum": 1.0},
        title = 'Select Gaussian Filter settings')
    if cancel: 
        return

    # Filter series
    series = app.selected('Series')
    for sery in series:
        resized = scipy.gaussian_filter(
            sery, f[0]['value'],
            order = f[1]['value'],
            mode = modes[f[2]['value']],
            cval = f[3]['value'],
            truncate = f[4]['value'],
        )
        app.display(resized)
    app.refresh()





action_roi_curve = Action('ROI curve', on_clicked=_roi_curve, is_clickable=_if_a_database_is_open)
action_roi_statistics = Action('ROI statistics', on_clicked=_roi_statistics, is_clickable=_if_a_database_is_open)

action_function_of_one_series = Action('y = f(series)', on_clicked=_function_of_one_series, is_clickable=_if_a_series_is_selected)
action_function_of_two_series = Action('y = f(series 1, series 2)', on_clicked=_function_of_two_series, is_clickable=_if_a_database_is_open)
action_function_of_n_series = Action('y = f(series 1, ..., series n)', on_clicked=_function_of_n_series, is_clickable=_if_a_database_is_open)

action_fourier_shift = Action('Shift (2D)', on_clicked=_fourier_shift, is_clickable=_if_a_series_is_selected)
action_distance_transform_edit_3d = Action('Distance transform (3D)', on_clicked=_distance_transform_edit_3d, is_clickable=_if_a_series_is_selected)
action_binary_fill_holes = Action('Fill holes', on_clicked=_binary_fill_holes, is_clickable=_if_a_series_is_selected)
action_label_2d = Action('Label clusters (2D)', on_clicked=_label_2d, is_clickable=_if_a_series_is_selected)
action_label_3d = Action('Label clusters (3D)', on_clicked=_label_3d, is_clickable=_if_a_series_is_selected)
action_extract_largest_cluster_3d = Action('Extract largest cluster (3D)', on_clicked=_extract_largest_cluster_3d, is_clickable=_if_a_series_is_selected)

action_overlay_on = Action('Overlay on..', on_clicked=_overlay_on, is_clickable=_if_a_database_is_open)
action_zoom = Action('Resample (2D)', on_clicked=_zoom, is_clickable=_if_a_series_is_selected)
action_resample_3d = Action('Resample (3D)', on_clicked=_resample_3d, is_clickable=_if_a_series_is_selected)
action_resample_3d_isotropic = Action('Resample isotropic (3D)', on_clicked=_resample_3d_isotropic, is_clickable=_if_a_series_is_selected)
action_reslice_axial = Action('Reslice (axial)', on_clicked=_reslice_axial, is_clickable=_if_a_series_is_selected)
action_reslice_coronal = Action('Reslice (coronal)', on_clicked=_reslice_coronal, is_clickable=_if_a_series_is_selected)
action_reslice_sagittal = Action('Reslice (sagittal)', on_clicked=_reslice_sagittal, is_clickable=_if_a_series_is_selected)

action_fourier_ellipsoid_filter = Action('Fourier filter (ellipsoid)', on_clicked=_fourier_ellipsoid_filter, is_clickable=_if_a_series_is_selected)
action_fourier_uniform_filter = Action('Fourier filter (uniform)', on_clicked=_fourier_uniform_filter, is_clickable=_if_a_series_is_selected)
action_fourier_gaussian_filter = Action('Fourier filter (Gaussian)', on_clicked=_fourier_gaussian_filter, is_clickable=_if_a_series_is_selected)
action_gaussian_gradient_magnitude_filter = Action('Gaussian gradient magnitude filter', on_clicked=_gaussian_gradient_magnitude_filter, is_clickable=_if_a_series_is_selected)
action_gaussian_laplace_filter = Action('Gaussian Laplace filter', on_clicked=_gaussian_laplace_filter, is_clickable=_if_a_series_is_selected)
action_laplace_filter = Action('Laplace filter', on_clicked=_laplace_filter, is_clickable=_if_a_series_is_selected)
action_sobel_filter = Action('Sobel filter', on_clicked=_sobel_filter, is_clickable=_if_a_series_is_selected)
action_prewitt_filter = Action('Prewitt filter', on_clicked=_prewitt_filter, is_clickable=_if_a_series_is_selected)
action_median_filter = Action('Median filter', on_clicked=_median_filter, is_clickable=_if_a_series_is_selected)
action_percentile_filter = Action('Percentile filter', on_clicked=_percentile_filter, is_clickable=_if_a_series_is_selected)
action_rank_filter = Action('Rank filter', on_clicked=_rank_filter, is_clickable=_if_a_series_is_selected)
action_maximum_filter = Action('Maximum filter', on_clicked=_maximum_filter, is_clickable=_if_a_series_is_selected)
action_minimum_filter = Action('Minimum filter', on_clicked=_minimum_filter, is_clickable=_if_a_series_is_selected)
action_uniform_filter = Action('Uniform filter', on_clicked=_uniform_filter, is_clickable=_if_a_series_is_selected)
action_gaussian_filter = Action('Gaussian filter', on_clicked=_gaussian_filter, is_clickable=_if_a_series_is_selected)

menu_roi = Menu('Region')
menu_roi.add(action_roi_curve)
menu_roi.add(action_roi_statistics)

menu_edit = Menu('Edit')
menu_edit.add(action_function_of_one_series)
menu_edit.add(action_function_of_two_series)
menu_edit.add(action_function_of_n_series)
menu_edit.add(action_fourier_shift)
menu_edit.add(action_distance_transform_edit_3d)
menu_edit.add(action_binary_fill_holes)
menu_edit.add(action_label_2d)
menu_edit.add(action_label_3d)
menu_edit.add(action_extract_largest_cluster_3d)

menu_reslice = Menu('Reslice')
menu_reslice.add(action_overlay_on)
menu_reslice.add(action_zoom)
menu_reslice.add(action_resample_3d)
menu_reslice.add(action_resample_3d_isotropic)
menu_reslice.add(action_reslice_axial)
menu_reslice.add(action_reslice_coronal)
menu_reslice.add(action_reslice_sagittal)

menu_filter = Menu('Filter')
menu_filter.add(action_gaussian_filter)
menu_filter.add_separator()
menu_filter.add(action_median_filter)
menu_filter.add(action_percentile_filter)
menu_filter.add(action_rank_filter)
menu_filter.add(action_maximum_filter)
menu_filter.add(action_minimum_filter)
menu_filter.add(action_uniform_filter)
menu_filter.add_separator()
menu_filter.add(action_gaussian_gradient_magnitude_filter)
menu_filter.add(action_gaussian_laplace_filter)
menu_filter.add(action_laplace_filter)
menu_filter.add(action_sobel_filter)
menu_filter.add(action_prewitt_filter)
menu_filter.add_separator()
menu_filter.add(action_fourier_ellipsoid_filter)
menu_filter.add(action_fourier_uniform_filter)
menu_filter.add(action_fourier_gaussian_filter)

menu_all = Menu('scipy')
menu_all.add(menu_roi)
menu_all.add(menu_edit)
menu_all.add(menu_reslice)
menu_all.add(menu_filter)