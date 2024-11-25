from dbdicom.extensions import elastix
from wezel.gui import Action, Menu



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
    coregistered = elastix.coregister_2d_to_2d(f[0], f[1],
        transformation = transform[f[2]["value"]],
        metric = metric[f[3]["value"]],
        final_grid_spacing = f[4]["value"],
    )
    app.display(coregistered)
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
        {"label":"Apply transformation also to:", "type":"select records", "options": series, 'default':[]},
        {"label":"Transformation: ", "type":"dropdownlist", "list": transform, 'value':1},
        {"label":"Metric: ", "type":"dropdownlist", "list": metric, 'value':1},
        {"label":"Final grid spacing (mm)", "type":"float", 'value':25.0, 'minimum':1.0},
        title = "Please select coregistration settings")
    if cancel:
        return
    coregistered, followers = elastix.coregister_3d_to_3d(f[0], f[1],
        transformation = transform[f[3]["value"]],
        metric = metric[f[4]["value"]],
        final_grid_spacing = f[5]["value"],
        apply_to = f[2],
    )
    app.display(coregistered)
    for f in followers:
        app.display(f)
    app.refresh()



def _if_a_database_is_open(app):
    return app.database() is not None

def _never(app):
    return False


action_2d_to_2d = Action('Coregister 2D to 2D', on_clicked=_calculate_2d_to_2d, is_clickable=_if_a_database_is_open)
action_3d_to_3d = Action('Coregister 3D to 3D', on_clicked=_calculate_3d_to_3d, is_clickable=_if_a_database_is_open)


menu = Menu('Coregister (Elastix)')
menu.add(action_2d_to_2d)
menu.add(action_3d_to_3d)

