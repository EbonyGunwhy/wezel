from dbdicom.wrappers import elastix
from wezel.gui import Action, Menu


def _invert_deformation_field(app):
    series = app.database().series()
    sel = app.selected('Series')
    #sel = series[0] if sel==[] else sel[0]
    cancel, f = app.dialog.input(
        {"label":"Deformation field", "type":"select record", "options": series, 'default': sel},
        {"label":"Smooth? ", "type":"dropdownlist", "list": ['Yes', 'No'], 'value':1},
        title = "Invert deformation field")
    if cancel:
        return
    smooth = f[1]["value"]==0
    deform_inv = elastix.invert_deformation_field(f[0], smooth=smooth)
    app.display(deform_inv)
    app.refresh()

# Wrapper is not working
def _warp(app):
    series = app.database().series()
    sel = app.selected('Series')
    cancel, f = app.dialog.input(
        {"label":"Image to deform", "type":"select record", "options": series, 'default':sel},
        {"label":"Deformation field", "type":"select record", "options": series, 'default':sel},
        title = "Please select warping parameters")
    if cancel:
        return
    try:
        deformed = elastix.warp(f[0], f[1])
        app.display(deformed)
        app.refresh()
    except ValueError as e:
        app.dialog.information(str(e))


def _calculate_2d_to_2d(app):
    series = app.database().series()
    sel = app.selected('Series')
    #sel = series[0] if sel==[] else sel[0]
    transform = ['Rigid', 'Affine', 'Freeform']
    metric = ["AdvancedMeanSquares", "NormalizedMutualInformation", "AdvancedMattesMutualInformation"]
    cancel, f = app.dialog.input(
        {"label":"Moving image (2D)", "type":"select record", "options": series, 'default': sel},
        {"label":"Fixed image (2D)", "type":"select record", "options": series, 'default': sel},
        {"label":"Transformation: ", "type":"dropdownlist", "list": transform, 'value':1},
        {"label":"Metric: ", "type":"dropdownlist", "list": metric, 'value':1},
        {"label":"Final grid spacing (mm)", "type":"float", 'value':25.0, 'minimum':1.0},
        title = "Please select coregistration settings")
    if cancel:
        return
    coregistered, deformation_field = elastix.coregister_2d_to_2d(f[0], f[1],
        transformation = transform[f[2]["value"]],
        metric = metric[f[3]["value"]],
        final_grid_spacing = f[4]["value"],
    )
    app.display(coregistered)
    app.display(deformation_field)
    app.refresh()


def _calculate_3d_to_3d(app):
    series = app.database().series()
    sel = app.selected('Series')
    #sel = series[0] if sel==[] else sel[0]
    transform = ['Rigid', 'Affine', 'Freeform']
    metric = ["AdvancedMeanSquares", "NormalizedMutualInformation", "AdvancedMattesMutualInformation"]
    cancel, f = app.dialog.input(
        {"label":"Moving image (3D)", "type":"select record", "options": series, 'default': sel},
        {"label":"Fixed image (3D)", "type":"select record", "options": series, 'default': sel},
        {"label":"Transformation: ", "type":"dropdownlist", "list": transform, 'value':1},
        {"label":"Metric: ", "type":"dropdownlist", "list": metric, 'value':1},
        {"label":"Final grid spacing (mm)", "type":"float", 'value':25.0, 'minimum':1.0},
        title = "Please select coregistration settings")
    if cancel:
        return
    coregistered, deformation_field = elastix.coregister_3d_to_3d(f[0], f[1],
        transformation = transform[f[2]["value"]],
        metric = metric[f[3]["value"]],
        final_grid_spacing = f[4]["value"],
    )
    app.display(coregistered)
    app.display(deformation_field)
    app.refresh()


def _calculate_3d_to_2d(app):
    series = app.database().series()
    sel = app.selected('Series')
    #sel = series[0] if sel==[] else sel[0]
    #transform = ['Rigid', 'Affine', 'Freeform'] # Affine and Freeform not working for 3d to 2d
    metric = ["AdvancedMeanSquares", "NormalizedMutualInformation", "AdvancedMattesMutualInformation"]
    cancel, f = app.dialog.input(
        {"label":"Moving image (3D)", "type":"select record", "options": series, 'default': sel},
        {"label":"Fixed image (2D)", "type":"select record", "options": series, 'default': sel},
    #    {"label":"Transformation: ", "type":"dropdownlist", "list": transform, 'value':1},
        {"label":"Metric: ", "type":"dropdownlist", "list": metric, 'value':1},
        {"label":"Final grid spacing (mm)", "type":"float", 'value':25.0, 'minimum':1.0},
        title = "Please select coregistration settings")
    if cancel:
        return
    coregistered, deformation_field = elastix.coregister_3d_to_2d(f[0], f[1],
#        transformation = transform[f[2]["value"]],
        transformation = 'Rigid',
        metric = metric[f[2]["value"]],
        final_grid_spacing = f[3]["value"],
    )
    app.display(coregistered)
    app.display(deformation_field)
    app.refresh()


def _calculate_2d_to_3d(app):
    # This does not work
    series = app.database().series()
    sel = app.selected('Series')
    #sel = series[0] if sel==[] else sel[0]
    #transform = ['Rigid', 'Affine', 'Freeform'] # Affine and Freeform not working for 3d to 2d
    metric = ["AdvancedMeanSquares", "NormalizedMutualInformation", "AdvancedMattesMutualInformation"]
    cancel, f = app.dialog.input(
        {"label":"Moving image (2D)", "type":"select record", "options": series, 'default': sel},
        {"label":"Fixed image (3D)", "type":"select record", "options": series, 'default': sel},
    #    {"label":"Transformation: ", "type":"dropdownlist", "list": transform, 'value':1},
        {"label":"Metric: ", "type":"dropdownlist", "list": metric, 'value':1},
        {"label":"Final grid spacing (mm)", "type":"float", 'value':25.0, 'minimum':1.0},
        title = "Please select coregistration settings")
    if cancel:
        return
    coregistered, deformation_field = elastix.coregister_2d_to_3d(f[0], f[1],
#        transformation = transform[f[2]["value"]],
        transformation = 'Rigid',
        metric = metric[f[2]["value"]],
        final_grid_spacing = f[3]["value"],
    )
    app.display(coregistered)
    app.display(deformation_field)
    app.refresh()



def _if_a_series_is_selected(app):
    return app.nr_selected('Series') != 0

def _if_a_database_is_open(app):
    return app.database() is not None

def _never(app):
    return False


action_2d_to_2d = Action('Coregister 2D to 2D', on_clicked=_calculate_2d_to_2d, is_clickable=_if_a_database_is_open)
action_3d_to_3d = Action('Coregister 3D to 3D', on_clicked=_calculate_3d_to_3d, is_clickable=_if_a_database_is_open)
action_3d_to_2d = Action('Coregister 3D to 2D', on_clicked=_calculate_3d_to_2d, is_clickable=_if_a_database_is_open)
action_2d_to_3d = Action('Coregister 2D to 3D', on_clicked=_calculate_2d_to_3d, is_clickable=_never)
action_warp = Action('Warp', on_clicked=_warp, is_clickable=_if_a_database_is_open)
action_invert_deformation = Action('Invert deformation field', on_clicked=_invert_deformation_field, is_clickable=_if_a_database_is_open)


menu = Menu('Coregister (Elastix)')
menu.add(action_2d_to_2d)
menu.add(action_3d_to_3d)
menu.add(action_3d_to_2d)
menu.add_separator()
menu.add(action_warp)
menu.add(action_invert_deformation)

