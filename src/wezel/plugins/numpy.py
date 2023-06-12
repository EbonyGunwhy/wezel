from dbdicom.wrappers import numpy
from wezel.gui import Action, Menu


def is_series_selected(app):
    return app.nr_selected('Series') != 0


def calculate_mean_intensity_projection(app):
    for series in app.selected('Series'):
        new_series = numpy.mean_intensity_projection(series)
        app.display(new_series)
    app.refresh()


def calculate_maximum_intensity_projection(app):
    for series in app.selected('Series'):
        new_series = numpy.maximum_intensity_projection(series)
        app.display(new_series)
    app.refresh()


def calculate_euclidian_norm_projection(app):
    for series in app.selected('Series'):
        new_series = numpy.norm_projection(series)
        app.display(new_series)
    app.refresh()


def calculate_absolute_threshold(app):
    # Get user input
    cancel, f = app.dialog.input(
        {"label":"low threshold (signal units)", "type":"float", "value": 0},
        {"label":"high threshold (signal units)", "type":"float", "value": 100},
        title = 'Select Thresholding settings')
    if cancel: 
        return
    # Filter series
    series = app.selected('Series')
    for sery in series:
        filtered = numpy.threshold(
            sery, 
            low_threshold = f[0]['value'],
            high_threshold = f[1]['value'],
            method = 'absolute',
        )
        app.display(filtered)
    app.refresh()


def calculate_relative_threshold(app):
    # Get user input
    cancel, f = app.dialog.input(
        {"label":"low threshold (%)", "type":"float", "value": 25.0, "minimum": 0.0, 'maximum':100.0},
        {"label":"high threshold (%)", "type":"float", "value": 75.0, "minimum": 0.0, 'maximum':100.0},
        {"label":"thresholding method", "type":"dropdownlist", "list": ['Range', 'Percentile'], "value": 1},
        title = 'Select Thresholding settings')
    if cancel: 
        return
    if f[2]['value'] == 1:
        method = 'quantiles'
    else:
        method = 'range'

    # Filter series
    series = app.selected('Series')
    for sery in series:
        filtered = numpy.threshold(
            sery, 
            low_threshold = f[0]['value']/100,
            high_threshold = f[1]['value']/100,
            method = method,
        )
        app.display(filtered)
    app.refresh()


action_mean_intensity_projection = Action('Mean Intensity Projection', on_clicked=calculate_mean_intensity_projection, is_clickable=is_series_selected)
action_maximum_intensity_projection = Action('Maximum Intensity Projection', on_clicked=calculate_maximum_intensity_projection, is_clickable=is_series_selected)
action_euclidian_norm_projection = Action('Euclidian Norm Projection', on_clicked=calculate_euclidian_norm_projection, is_clickable=is_series_selected)
action_absolute_threshold = Action('Thresholding (absolute values)', on_clicked=calculate_absolute_threshold, is_clickable=is_series_selected)
action_relative_threshold = Action('Thresholding (relative values)', on_clicked=calculate_relative_threshold, is_clickable=is_series_selected)


menu_all = Menu('numpy')
menu_all.add(action_maximum_intensity_projection)
menu_all.add(action_mean_intensity_projection)
menu_all.add(action_euclidian_norm_projection)
menu_all.add(action_absolute_threshold)
menu_all.add(action_relative_threshold)


menu_project = Menu('Project on slices..')
menu_project.add(action_maximum_intensity_projection)
menu_project.add(action_mean_intensity_projection)
menu_project.add(action_euclidian_norm_projection)

