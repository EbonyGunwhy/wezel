from dbdicom.extensions import skimage
from wezel.gui import Action, Menu
from wezel.displays import TableDisplay


def _if_a_series_is_selected(app):
    return app.nr_selected('Series') != 0

def _if_a_database_is_open(app):
    return app.database() is not None


def _volume_features(app):
    # df = None
    # for series in app.selected('Series'):
    #     df_series = skimage.volume_features(series)
    #     if df is None:
    #         df = df_series
    #     else:
    #         df = pd.concat([df, df_series], ignore_index=True)
    series = app.selected('Series')
    df = skimage.volume_features(series)
    viewer = TableDisplay(df)
    app.addWidget(viewer, 'Volume features')
    app.status.hide()


def _area_opening_2d(app):
    cancel, f = app.dialog.input(
        {"label":"Remove bright structures with an area less than.. (in pixels)", "type":"integer", "value": 9, "minimum": 1},
        {"label":"Connectivity (in pixels)", "type":"integer", "value": 1, "minimum": 1},
        title = 'Select area opening settings')
    if cancel: 
        return
    for series in app.selected('Series'):
        result = skimage.area_opening_2d(
            series, 
            area_threshold = f[0]['value'],
            connectivity = f[1]['value'])
        app.display(result)
    app.refresh()


def _area_opening_3d(app):
    cancel, f = app.dialog.input(
        {"label":"Remove bright structures with a volume less than.. (in pixels)", "type":"integer", "value": 9, "minimum": 1},
        {"label":"Connectivity (in pixels)", "type":"integer", "value": 1, "minimum": 1},
        title = 'Select area opening settings')
    if cancel: 
        return
    for series in app.selected('Series'):
        result = skimage.area_opening_3d(
            series, 
            area_threshold = f[0]['value'],
            connectivity = f[1]['value'])
        app.display(result)
    app.refresh()


def _area_closing_2d(app):
    cancel, f = app.dialog.input(
        {"label":"Remove dark structures with an area less than.. (in pixels)", "type":"integer", "value": 27, "minimum": 1},
        {"label":"Connectivity (in pixels)", "type":"integer", "value": 1, "minimum": 1},
        title = 'Select area opening settings')
    if cancel: 
        return
    for series in app.selected('Series'):
        result = skimage.area_closing_2d(
            series, 
            area_threshold = f[0]['value'],
            connectivity = f[1]['value'])
        app.display(result)
    app.refresh()


def _area_closing_3d(app):
    cancel, f = app.dialog.input(
        {"label":"Remove dark structures with volume less than.. (in pixels)", "type":"integer", "value": 27, "minimum": 1},
        {"label":"Connectivity (in pixels)", "type":"integer", "value": 1, "minimum": 1},
        title = 'Select area opening settings')
    if cancel: 
        return
    for series in app.selected('Series'):
        result = skimage.area_closing_3d(
            series, 
            area_threshold = f[0]['value'],
            connectivity = f[1]['value'])
        app.display(result)
    app.refresh()


def _opening_2d(app):
    for series in app.selected('Series'):
        result = skimage.opening_2d(series)
        app.display(result)
    app.refresh()


def _opening_3d(app):
    for series in app.selected('Series'):
        result = skimage.opening_3d(series)
        app.display(result)
    app.refresh()


def _closing_2d(app):
    for series in app.selected('Series'):
        result = skimage.closing_2d(series)
        app.display(result)
    app.refresh()


def _closing_3d(app):
    for series in app.selected('Series'):
        result = skimage.closing_3d(series)
        app.display(result)
    app.refresh()


def _remove_small_holes_2d(app):
    cancel, f = app.dialog.input(
        {"label":"Remove dark structures with an area less than.. (in pixels)", "type":"integer", "value": 9, "minimum": 1},
        {"label":"Connectivity (in pixels)", "type":"integer", "value": 1, "minimum": 1},
        title = 'Select area opening settings')
    if cancel: 
        return
    for series in app.selected('Series'):
        result = skimage.remove_small_holes_2d(
            series, 
            area_threshold = f[0]['value'],
            connectivity = f[1]['value'])
        app.display(result)
    app.refresh()


def _remove_small_holes_3d(app):
    cancel, f = app.dialog.input(
        {"label":"Remove dark structures with volume less than.. (in pixels)", "type":"integer", "value": 27, "minimum": 1},
        {"label":"Connectivity (in pixels)", "type":"integer", "value": 1, "minimum": 1},
        title = 'Select area opening settings')
    if cancel: 
        return
    for series in app.selected('Series'):
        result = skimage.remove_small_holes_3d(
            series, 
            area_threshold = f[0]['value'],
            connectivity = f[1]['value'])
        app.display(result)
    app.refresh()


def _skeletonize_3d(app):
    for sery in app.selected('Series'):
        result = skimage.skeletonize_3d(sery)
        app.display(result)
    app.refresh()


def _skeletonize_2d(app):
    for sery in app.selected('Series'):
        result = skimage.skeletonize(sery)
        app.display(result)
    app.refresh()


def _convex_hull_image_2d(app):
    for sery in app.selected('Series'):
        result = skimage.convex_hull_image(sery)
        app.display(result)
    app.refresh()


def _convex_hull_image_3d(app):
    for sery in app.selected('Series'):
        result = skimage.convex_hull_image_3d(sery)
        app.display(result)
    app.refresh()


def _canny(app):

    # Default settings
    modes = ['reflect', 'constant', 'nearest', 'mirror', 'wrap']
    sigma = 1.0
    low_threshold = 25.
    high_threshold = 75.
    mode = 1
    cval = 0.0

    # Get user input
    cancel, f = app.dialog.input(
        {"label":"sigma (standard deviation for Gaussian kernel)", "type":"float", "value":sigma, "minimum": 1.0},
        {"label":"low threshold (%)", "type":"float", "value": low_threshold, "minimum": 0.0, 'maximum':100.0},
        {"label":"high threshold (%)", "type":"float", "value": high_threshold, "minimum": 0.0, 'maximum':100.0},
        {"label":"mode (of extension at border)", "type":"dropdownlist", "list": modes, "value": mode},
        {"label":"cval (value past edges in constant mode)", "type":"float", "value":cval},
        title = 'Select Canny Edge Filter settings')
    if cancel: 
        return

    # update defaults
    sigma = f[0]['value']
    low_threshold = f[1]['value']/100
    high_threshold = f[2]['value']/100
    mode = f[3]['value']
    cval = f[4]['value']

    # Filter series
    for sery in app.selected('Series'):
        filtered = skimage.canny(
            sery, 
            sigma = sigma,
            low_threshold = low_threshold,
            high_threshold = high_threshold,
            use_quantiles = True,
            mode = modes[mode],
            cval = cval,
        )
        app.display(filtered)
    app.refresh()


def _peak_local_max_3d(app):

    selected = app.selected('Series')
    series_list = selected[0].parent().children()
    series_labels = [s.instance().SeriesDescription for s in series_list]

    # Get user input
    cancel, f = app.dialog.input(
        {"label":"Find local maxima of series..", "type":"dropdownlist", "list": series_labels, "value": series_list.index(selected[0])},
        {"label":"Region to search for peaks", "type":"dropdownlist", "list": ['Entire image'] + series_labels, "value": 0},
        {"label":"Minimal distance between peaks (in pixels)", "type":"integer", "value": 1, "minimum": 1},
        {"label":"Size of the image border (in pixels)", "type":"integer", "value": 2, "minimum": 0},
        title = 'Select Local Maximum settings')
    if cancel: 
        return

    if f[1]['value'] == 0:
        labels = None
    else:
        labels = series_list[f[1]['value']-1]

    # Filter series
    filtered = skimage.peak_local_max_3d(
        series_list[f[0]['value']], 
        labels = labels,
        min_distance = f[2]['value'],
        exclude_border = f[3]['value'],
    )
    app.display(filtered)
    app.refresh()




def _watershed_2d(app):

    # Filter series
    series = app.selected('Series')
    for sery in series:

        # Get user input
        desc = sery.label()
        all_series = sery.parent().children()
        all_series_desc = [s.label() for s in all_series]
        siblings = sery.siblings()
        sibling_desc = [s.label() for s in siblings]
        cancel, f = app.dialog.input(
            {   "label": "Landscape for watershed: ", 
                "type": "dropdownlist", 
                "list": all_series_desc, 
                "value": all_series.index(sery),
            },
            {   "label": "Initial labels: ", 
                "type": "dropdownlist", 
                "list": ['use local minima'] + sibling_desc, 
                "value": 0,
            },
            {   "label": "Label pixels in: ", 
                "type": "dropdownlist", 
                "list": ['Entire image'] + sibling_desc, 
                "value": 0,
            },
            {   'label': 'Compactness: ',
                'type': 'float',
                'value': 0.0, 
            },
            {   'label': 'Include watershed line?',
                'type': 'dropdownlist',
                'list': ['Yes', 'No'],
                'value': 1,
            },
            title = 'Select settings for watershed segmentation of ' + desc)
        if cancel: 
            return

            # Calculate watershed
        result = skimage.watershed_2d(
            all_series[f[0]['value']], 
            markers = None if f[1]['value']==0 else siblings[f[1]['value']-1],
            mask = None if f[2]['value']==0 else siblings[f[2]['value']-1],
            compactness = f[3]['value'],
            watershed_line = f[4]['value'] == 0,
        )
        app.display(result)
    app.refresh()


def _watershed_3d(app):

    # Filter series
    series = app.selected('Series')
    for sery in series:

        # Get user input
        desc = sery.label()
        all_series = sery.parent().children()
        all_series_desc = [s.label() for s in all_series]
        siblings = sery.siblings()
        sibling_desc = [s.label() for s in siblings]
        cancel, f = app.dialog.input(
            {   "label": "Landscape for watershed: ", 
                "type": "dropdownlist", 
                "list": all_series_desc, 
                "value": all_series.index(sery),
            },
            {   "label": "Initial labels: ", 
                "type": "dropdownlist", 
                "list": ['use local minima'] + sibling_desc, 
                "value": 0,
            },
            {   "label": "Label pixels in: ", 
                "type": "dropdownlist", 
                "list": ['Entire image'] + sibling_desc, 
                "value": 0,
            },
            {   'label': 'Compactness: ',
                'type': 'float',
                'value': 0.0, 
            },
            {   'label': 'Include watershed line?',
                'type': 'dropdownlist',
                'list': ['Yes', 'No'],
                'value': 1,
            },
            title = 'Select settings for watershed segmentation of ' + desc)
        if cancel: 
            return

            # Calculate watershed
        result = skimage.watershed_3d(
            all_series[f[0]['value']], 
            markers = None if f[1]['value']==0 else siblings[f[1]['value']-1],
            mask = None if f[2]['value']==0 else siblings[f[2]['value']-1],
            compactness = f[3]['value'],
            watershed_line = f[4]['value'] == 0,
        )
        app.display(result)

    app.refresh()


def _warp(app):
    series = app.database().series()
    sel = app.selected('Series')
    #sel = series[0] if sel==[] else sel[0]
    cancel, f = app.dialog.input(
        {"label":"Image to deform", "type":"select record", "options": series, 'default':sel},
        {"label":"Deformation field", "type":"select record", "options": series, 'default':sel},
        title = "Please select warping parameters")
    if cancel:
        return
    try:
        deformed = skimage.warp(f[0], f[1])
        app.display(deformed)
        app.refresh()
    except ValueError as e:
        app.dialog.information(str(e))


def _coregistration_2d_to_2d(app):
    series = app.database().series()
    sel = app.selected('Series')
    #sel = series[0] if sel==[] else sel[0]
    cancel, f = app.dialog.input(
        {"label":"Moving series", "type":"select record", "options": series, 'default':sel},
        {"label":"Fixed series", "type":"select record", "options": series, 'default':sel},
        {"label":"Attachment (smaller = smoother)", "type":"float", 'value':0.01, 'minimum':0.0}, 
        title = "Please select 2D-2D coregistration parameters")
    if cancel:
        return
    coregistered, deformation = skimage.coregister_2d_to_2d(f[0], f[1], attachment=f[2]["value"])
    app.display(coregistered)
    app.display(deformation)
    app.refresh()


def _coregistration_3d_to_3d(app):
    series = app.database().series()
    sel = app.selected('Series')
    #sel = series[0] if sel==[] else sel[0]
    cancel, f = app.dialog.input(
        {"label":"Moving series", "type":"select record", "options": series, 'default':sel},
        {"label":"Fixed series", "type":"select record", "options": series, 'default':sel},
        {"label":"Attachment (smaller = smoother)", "type":"float", 'value':0.01, 'minimum':0.0}, 
        title = "Please select 3D to 3D coregistration parameters")
    if cancel:
        return
    coregistered, deformation = skimage.coregister_3d_to_3d(f[0], f[1], attachment=f[2]["value"])
    app.display(coregistered)
    app.display(deformation)
    app.refresh()


def _coregister_series_2d_to_2d(app):
    series = app.database().series()
    sel = app.selected('Series')
    #sel = series[0] if sel==[] else sel[0]
    cancel, f = app.dialog.input(
        {"label":"Moving series", "type":"select record", "options": series, 'default':sel},
        {"label":"Fixed series", "type":"select record", "options": series, 'default':sel},
        {"label":"Attachment (smaller = smoother)", "type":"float", 'value':0.01, 'minimum':0.0}, 
        title = "Please select 2D to 2D coregistration parameters")
    if cancel:
        return
    coregistered, deformation = skimage.coregister_2d_to_2d(f[0], f[1], attachment=f[2]["value"])
    app.display(coregistered)
    app.display(deformation)
    app.refresh()


def _mdr_constant_2d(app):
    cancel, f = app.dialog.input(
        {"label":"Attachment (smaller = smoother)", "type":"float", 'value':0.1, 'minimum':0.0}, 
        {"label":"Stop when improvement is less than (pixelsizes):", "type":"float", 'value':1.0, 'minimum':0},
        {"label":"Maximum number of iterations", "type":"integer", 'value':10, 'minimum':1}, 
        title = "Please select coregistration settings")
    if cancel:
        return
    for series in app.selected('Series'):
        coregistered = skimage.mdreg_constant_2d(series, 
            attachment = f[0]["value"],
            max_improvement = f[1]["value"],
            max_iter = f[2]["value"])
        app.display(coregistered)
    app.refresh()


def _mdr_constant_3d(app):
    cancel, f = app.dialog.input(
        {"label":"Attachment (smaller = smoother)", "type":"float", 'value':0.1, 'minimum':0.0}, 
        {"label":"Stop when improvement is less than (pixelsizes):", "type":"float", 'value':1.0, 'minimum':0},
        {"label":"Maximum number of iterations", "type":"integer", 'value':10, 'minimum':1}, 
        title = "Please select coregistration settings")
    if cancel:
        return
    for series in app.selected('Series'):
        coregistered = skimage.mdreg_constant_3d(series, 
            attachment = f[0]["value"],
            max_improvement = f[1]["value"],
            max_iter = f[2]["value"])
        app.display(coregistered)
    app.refresh()


action_volume_features = Action('3D volume features', on_clicked=_volume_features, is_clickable=_if_a_series_is_selected)
action_area_opening_2d = Action('Remove bright spots with area less than.. (2D)', on_clicked=_area_opening_2d, is_clickable=_if_a_series_is_selected)
action_area_opening_3d = Action('Remove bright spots with area less than.. (3D)', on_clicked=_area_opening_3d, is_clickable=_if_a_series_is_selected)
action_area_closing_2d = Action('Remove dark spots with area less than.. (2D)', on_clicked=_area_closing_2d, is_clickable=_if_a_series_is_selected)
action_area_closing_3d = Action('Remove dark spots with area less than.. (3D)', on_clicked=_area_closing_3d, is_clickable=_if_a_series_is_selected)
action_opening_2d = Action('Remove bright spots (2D)', on_clicked=_opening_2d, is_clickable=_if_a_series_is_selected)
action_opening_3d = Action('Remove bright spots (3D)', on_clicked=_opening_3d, is_clickable=_if_a_series_is_selected)
action_closing_2d = Action('Remove dark spots (2D)', on_clicked=_closing_2d, is_clickable=_if_a_series_is_selected)
action_closing_3d = Action('Remove dark spots (3D)', on_clicked=_closing_3d, is_clickable=_if_a_series_is_selected)
action_remove_small_holes_2d = Action('Remove small holes (2D)', on_clicked=_remove_small_holes_2d, is_clickable=_if_a_series_is_selected)
action_remove_small_holes_3d = Action('Remove small holes (3D)', on_clicked=_remove_small_holes_3d, is_clickable=_if_a_series_is_selected)
action_skeletonize_2d = Action('Skeletonize (2D)', on_clicked=_skeletonize_2d, is_clickable=_if_a_series_is_selected)
action_skeletonize_3d = Action('Skeletonize (3D)', on_clicked=_skeletonize_3d, is_clickable=_if_a_series_is_selected)
action_convex_hull_image_2d = Action('Convex Hull (2D)', on_clicked=_convex_hull_image_2d, is_clickable=_if_a_series_is_selected)
action_convex_hull_image_3d = Action('Convex Hull (3D)', on_clicked=_convex_hull_image_3d, is_clickable=_if_a_series_is_selected)
action_canny = Action('Canny Edge Detection', on_clicked=_canny, is_clickable=_if_a_series_is_selected)
action_peak_local_max_3d = Action('Peak local maximum (3D)', on_clicked=_peak_local_max_3d, is_clickable=_if_a_series_is_selected)
action_watershed_2d = Action('Watershed (2D)', on_clicked=_watershed_2d, is_clickable=_if_a_series_is_selected)
action_watershed_3d = Action('Watershed (3D)', on_clicked=_watershed_3d, is_clickable=_if_a_series_is_selected)
action_warp = Action('Warp', on_clicked=_warp, is_clickable=_if_a_database_is_open)
action_coregistration_2d_to_2d = Action('Coregister (2D to 2D)', on_clicked=_coregistration_2d_to_2d, is_clickable=_if_a_database_is_open)
action_coregistration_3d_to_3d = Action('Coregister (3D to 3D)', on_clicked=_coregistration_3d_to_3d, is_clickable=_if_a_database_is_open)
action_coregister_series_2d_to_2d = Action('Coregister series to mean (2D)', on_clicked=_coregister_series_2d_to_2d, is_clickable=_if_a_series_is_selected)
action_mdr_constant_2d = Action('Model-driven registration (constant - 2D)', on_clicked=_mdr_constant_2d, is_clickable=_if_a_series_is_selected)
action_mdr_constant_3d = Action('Model-driven registration (constant - 3D)', on_clicked=_mdr_constant_3d, is_clickable=_if_a_series_is_selected)


menu_edit = Menu('Edit mask')
menu_edit.add(action_area_opening_2d)
menu_edit.add(action_area_opening_3d)
menu_edit.add(action_area_closing_2d)
menu_edit.add(action_area_closing_3d)
menu_edit.add(action_closing_2d)
menu_edit.add(action_closing_3d)
menu_edit.add(action_remove_small_holes_2d)
menu_edit.add(action_remove_small_holes_3d)

menu_create = Menu('Create mask')
menu_create.add(action_skeletonize_2d)
menu_create.add(action_skeletonize_3d)
menu_create.add(action_convex_hull_image_2d)
menu_create.add(action_convex_hull_image_3d)
menu_create.add(action_watershed_2d)
menu_create.add(action_watershed_3d)
menu_create.add(action_canny)

menu_coreg = Menu('Coregister (skimage)')
menu_coreg.add(action_coregistration_2d_to_2d)
menu_coreg.add(action_coregistration_3d_to_3d)
menu_coreg.add_separator()
menu_coreg.add(action_warp)
menu_coreg.add_separator()
menu_coreg.add(action_coregister_series_2d_to_2d)
menu_coreg.add(action_mdr_constant_2d)
menu_coreg.add(action_mdr_constant_3d)

menu_all = Menu('skimage')
menu_all.add(action_volume_features)
menu_all.add(action_peak_local_max_3d)
menu_all.add(action_warp)
menu_all.add_separator()
menu_all.add(menu_edit)
menu_all.add(menu_create)
menu_all.add(menu_coreg)

menu_edit_2d = Menu('Edit mask (2D)')
menu_edit_2d.add(action_area_opening_2d)
menu_edit_2d.add(action_area_closing_2d)
menu_edit_2d.add(action_closing_2d)
menu_edit_2d.add(action_remove_small_holes_2d)

menu_edit_3d = Menu('Edit mask (3D)')
menu_edit_3d.add(action_area_opening_3d)
menu_edit_3d.add(action_area_closing_3d)
menu_edit_3d.add(action_closing_3d)
menu_edit_3d.add(action_remove_small_holes_3d)

menu_create_2d = Menu('Create mask (2D)')
menu_create_2d.add(action_skeletonize_2d)
menu_create_2d.add(action_convex_hull_image_2d)
menu_create_2d.add(action_watershed_2d)
menu_create_2d.add(action_canny)

menu_create_3d = Menu('Create mask (3D)')
menu_create_3d.add(action_skeletonize_3d)
menu_create_3d.add(action_convex_hull_image_3d)
menu_create_3d.add(action_watershed_3d)

menu_dark_spots = Menu('Remove dark spots')
menu_dark_spots.add(action_closing_2d)
menu_dark_spots.add(action_closing_3d)
menu_dark_spots.add_separator()
menu_dark_spots.add(action_area_closing_2d)
menu_dark_spots.add(action_area_closing_3d)

menu_bright_spots = Menu('Remove bright spots')
menu_bright_spots.add(action_opening_2d)
menu_bright_spots.add(action_opening_3d)
menu_bright_spots.add_separator()
menu_bright_spots.add(action_area_opening_2d)
menu_bright_spots.add(action_area_opening_3d)
menu_bright_spots.add_separator()
menu_bright_spots.add(action_remove_small_holes_2d)
menu_bright_spots.add(action_remove_small_holes_3d)