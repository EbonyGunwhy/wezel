from dbdicom.extensions import dipy
from wezel.gui import Action, Menu


def _if_a_series_is_selected(app):
    return app.nr_selected('Series') != 0

def _if_a_database_is_open(app):
    return app.database() is not None

def _never(app):
    return False


def median_otsu(app):

    # Get user input
    cancel, f = app.dialog.input(
        {"label":"Median Radius", "type":"integer", "value": 2, 'minimum':1},
        {"label":"Numpass", "type":"integer", "value": 1, 'minimum':1},
        title = 'Select Thresholding settings')
    if cancel: 
        return

    # Filter series
    series = app.selected('Series')
    for sery in series:
        mask_series, mask = dipy.median_otsu(
            sery, 
            median_radius=f[0]['value'], 
            numpass=f[1]['value'],
        )
        mask_series.remove()
        app.display(mask)
    app.refresh()


def _invert_deformation_field(app):
    series = app.database().series()
    sel = app.selected('Series')
    cancel, f = app.dialog.input(
        {"label":"Deformation field", "type":"select record", "options": series, 'default': sel},
        {"label":"Maximum number of iterations", "type":"integer", "value": 10, 'minimum':1},
        {"label":"Tolerance", "type":"float", "value":0.1, 'minimum':0.001},
        title = "Invert deformation field")
    if cancel:
        return
    deform_inv = dipy.invert_deformation_field(f[0], max_iter=f[1]['value'], tolerance=f[2]['value'])
    app.display(deform_inv)
    app.refresh()


def warp(app):
    series = app.database().series()
    sel = app.selected('Series')
    cancel, f = app.dialog.input(
        {"label":"Series to warp", "type":"select record", "options":series, 'default':sel},
        {"label":"Deformation field", "type":"select record", "options":series, 'default':sel},
        {"label":"Interpolate? ", "type":"dropdownlist", "list": ['Yes', 'No'], 'value':0},
        title = "Warp series with deformation field..")
    if cancel:
        return
    warped = dipy.warp(f[0], f[1], 
        interpolate = True if f[2]==0 else False)
    app.display(warped)
    app.refresh()


def _align_center_of_mass_2d(app):
    series = app.database().series()
    sel = app.selected('Series')
    cancel, f = app.dialog.input(
        {"label":"Moving image", "type":"select record", "options":series, 'default':sel},
        {"label":"Fixed image", "type":"select record", "options":series, 'default':sel},
        title = "Align center of mass (2D)")
    if cancel:
        return
    moved = dipy.align_center_of_mass_2d(f[0], f[1])
    app.display(moved)
    app.refresh()


def _align_center_of_mass_3d(app):
    series = app.database().series()
    sel = app.selected('Series')
    cancel, f = app.dialog.input(
        {"label":"Moving image", "type":"select record", "options":series, 'default':sel},
        {"label":"Fixed image", "type":"select record", "options":series, 'default':sel},
        title = "Align center of mass (3D)")
    if cancel:
        return
    moved = dipy.align_center_of_mass_3d(f[0], f[1])
    app.display(moved)
    app.refresh()


def _coregister_translation_2d(app):
    series = app.database().series()
    sel = app.selected('Series')
    cancel, f = app.dialog.input(
        {"label":"Moving series", "type":"select record", "options":series, 'default':sel},
        {"label":"Fixed series", "type":"select record", "options":series, 'default':sel},
        title = "2D coregistration with translation")
    if cancel:
        return
    coregistered = dipy.coregister_translation_2d(f[0],f[1])
    app.display(coregistered)
    app.refresh()


def _coregister_rigid_2d(app):
    series = app.database().series()
    sel = app.selected('Series')
    cancel, f = app.dialog.input(
        {"label":"Moving series", "type":"select record", "options":series, 'default':sel},
        {"label":"Fixed series", "type":"select record", "options":series, 'default':sel},
        title = "2D coregistration with rigid transform")
    if cancel:
        return
    coregistered = dipy.coregister_rigid_2d(f[0],f[1])
    app.display(coregistered)
    app.refresh()


def _coregister_affine_2d(app):
    series = app.database().series()
    sel = app.selected('Series')
    cancel, f = app.dialog.input(
        {"label":"Moving series", "type":"select record", "options":series, 'default':sel},
        {"label":"Fixed series", "type":"select record", "options":series, 'default':sel},
        title = "2D coregistration with affine transform")
    if cancel:
        return
    coregistered = dipy.coregister_affine_2d(f[0],f[1])
    app.display(coregistered)
    app.refresh()


def coregister_deformable_2d(app):
    series = app.database().series()
    sel = app.selected('Series')
    metric = ["Cross-Correlation", 'Expectation-Maximization', 'Sum of Squared Differences']
    cancel, f = app.dialog.input(
        {"label":"Moving series", "type":"select record", "options":series, 'default':sel},
        {"label":"Fixed series", "type":"select record", "options":series, 'default':sel},
        {"label":"Metric", "type":"dropdownlist", "list": metric, 'value':0},
        title = "Please select 2D to 2D coregistration settings")
    if cancel:
        return
    coregistered, deformation = dipy.coregister_deformable_2d(f[0], f[1],
        transformation = 'Symmetric Diffeomorphic',
        metric = metric[f[2]["value"]],
    )
    app.display(coregistered)
    app.display(deformation)
    app.refresh()


def _coregister_translation_3d(app):
    series = app.database().series()
    sel = app.selected('Series')
    cancel, f = app.dialog.input(
        {"label":"Moving series", "type":"select record", "options":series, 'default':sel},
        {"label":"Fixed series", "type":"select record", "options":series, 'default':sel},
        title = "3D coregistration with translation")
    if cancel:
        return
    coregistered = dipy.coregister_translation_3d(f[0],f[1])
    app.display(coregistered)
    app.refresh()


def _coregister_rigid_3d(app):
    series = app.database().series()
    sel = app.selected('Series')
    cancel, f = app.dialog.input(
        {"label":"Moving series", "type":"select record", "options":series, 'default':sel},
        {"label":"Fixed series", "type":"select record", "options":series, 'default':sel},
        title = "3D coregistration with translation & rotation")
    if cancel:
        return
    coregistered = dipy.coregister_rigid_3d(f[0],f[1])
    app.display(coregistered)
    app.refresh()


def _coregister_affine_3d(app):
    series = app.database().series()
    sel = app.selected('Series')
    cancel, f = app.dialog.input(
        {"label":"Moving series", "type":"select record", "options":series, 'default':sel},
        {"label":"Fixed series", "type":"select record", "options":series, 'default':sel},
        title = "3D coregistration with affine transformation")
    if cancel:
        return
    coregistered = dipy.coregister_affine_3d(f[0],f[1])
    app.display(coregistered)
    app.refresh()


def coregister_deformable_3d(app):
    series = app.database().series()
    sel = app.selected('Series')
    metric = ["Cross-Correlation", 'Expectation-Maximization', 'Sum of Squared Differences']
    cancel, f = app.dialog.input(
        {"label":"Moving series", "type":"select record", "options":series, 'default':sel},
        {"label":"Fixed series", "type":"select record", "options":series, 'default':sel},
        {"label":"Metric", "type":"dropdownlist", "list": metric, 'value':0},
        title = "Please select 3D to 3D coregistration settings")
    if cancel:
        return
    coregistered, deformation = dipy.coregister_deformable_3d(f[0], f[1],
        transformation = 'Symmetric Diffeomorphic',
        metric = metric[f[2]["value"]])
    app.display(coregistered)
    app.display(deformation)
    app.refresh()


# Segmentation
action_median_otsu = Action('Median Otsu segmentation', on_clicked=median_otsu, is_clickable=_if_a_series_is_selected)

# Coregistration
action_align_center_of_mass_2d = Action('Align center of mass (2D)', on_clicked=_align_center_of_mass_2d, is_clickable=_if_a_database_is_open)
action_align_center_of_mass_3d = Action('Align center of mass (3D)', on_clicked=_align_center_of_mass_3d, is_clickable=_if_a_database_is_open)
action_align_moments_of_inertia_2d = Action('Align moments of inertia (2D)', on_clicked=_never, is_clickable=_never)
action_align_moments_of_inertia_3d = Action('Align moments of inertia (3D)', on_clicked=_never, is_clickable=_never)
action_coregister_translation_2d = Action('Coregister (Translation - 2D)', on_clicked=_coregister_translation_2d, is_clickable=_if_a_database_is_open)
action_coregister_translation_3d = Action('Coregister (Translation - 3D)', on_clicked=_coregister_translation_3d, is_clickable=_if_a_database_is_open)
action_coregister_rigid_2d = Action('Coregister (Rigid - 2D)', on_clicked=_coregister_rigid_2d, is_clickable=_if_a_database_is_open)
action_coregister_rigid_3d = Action('Coregister (Rigid - 3D)', on_clicked=_coregister_rigid_3d, is_clickable=_if_a_database_is_open)
action_coregister_affine_2d = Action('Coregister (Affine - 2D)', on_clicked=_coregister_affine_2d, is_clickable=_if_a_database_is_open)
action_coregister_affine_3d = Action('Coregister (Affine - 3D)', on_clicked=_coregister_affine_3d, is_clickable=_if_a_database_is_open)
action_coregister_deformable_2d = Action('Coregister (Deformable - 2D)', on_clicked=coregister_deformable_2d, is_clickable=_if_a_database_is_open)
action_coregister_deformable_3d = Action('Coregister (Deformable - 3D)', on_clicked=coregister_deformable_3d, is_clickable=_if_a_database_is_open)
action_warp = Action('Warp', on_clicked=warp, is_clickable=_if_a_database_is_open)
action_invert_deformation = Action('Invert deformation field', on_clicked=_invert_deformation_field, is_clickable=_if_a_database_is_open)


menu_all = Menu('dipy')
menu_all.add(action_median_otsu)
menu_all.add_separator()
menu_all.add(action_align_center_of_mass_2d)
menu_all.add(action_align_center_of_mass_3d)
menu_all.add(action_coregister_translation_2d)
menu_all.add(action_coregister_translation_3d)
menu_all.add_separator()
menu_all.add(action_align_moments_of_inertia_2d)
menu_all.add(action_align_moments_of_inertia_3d)
menu_all.add(action_coregister_rigid_2d)
menu_all.add(action_coregister_rigid_3d)
menu_all.add_separator()
menu_all.add(action_coregister_affine_2d)
menu_all.add(action_coregister_affine_3d)
menu_all.add_separator()
menu_all.add(action_coregister_deformable_2d)
menu_all.add(action_coregister_deformable_3d)
menu_all.add_separator()
menu_all.add(action_warp)
menu_all.add(action_invert_deformation)



menu_coreg = Menu('Coregister (dipy)')
menu_coreg.add(action_align_center_of_mass_2d)
menu_coreg.add(action_align_center_of_mass_3d)
menu_coreg.add_separator()
menu_coreg.add(action_align_moments_of_inertia_2d)
menu_coreg.add(action_align_moments_of_inertia_3d)
menu_coreg.add_separator()
menu_coreg.add(action_coregister_translation_2d)
menu_coreg.add(action_coregister_translation_3d)
menu_coreg.add_separator()
menu_coreg.add(action_coregister_rigid_2d)
menu_coreg.add(action_coregister_rigid_3d)
menu_coreg.add_separator()
menu_coreg.add(action_coregister_affine_2d)
menu_coreg.add(action_coregister_affine_3d)
menu_coreg.add_separator()
menu_coreg.add(action_coregister_deformable_2d)
menu_coreg.add(action_coregister_deformable_3d)
menu_coreg.add_separator()
menu_coreg.add(action_warp)
menu_coreg.add(action_invert_deformation)



