from dbdicom.wrappers import vreg
from wezel.gui import Action, Menu


def _if_a_series_is_selected(app):
    return app.nr_selected('Series') != 0

def _if_a_database_is_open(app):
    return app.database() is not None


def _translation_sos(app):
    series = app.database().series()
    sel = app.selected('Series')
    cancel, f = app.dialog.input(
        {"label":"Moving series", "type":"select record", "options": series, 'default':sel},
        {"label":"Static series", "type":"select record", "options": series, 'default':sel},
        {"label":"Tolerance (smaller = slower but more accurate)", "type":"float", 'value':0.1, 'minimum':0.001}, 
        title = "Please select coregistration parameters (translation with sum-of-squares)")
    if cancel:
        return
    coregistered = vreg.translation_sos(f[0], f[1], tolerance=f[2]["value"])
    app.display(coregistered)
    app.refresh()


def _sbs_translation_sos(app):
    series = app.database().series()
    sel = app.selected('Series')
    cancel, f = app.dialog.input(
        {"label":"Moving series", "type":"select record", "options": series, 'default':sel},
        {"label":"Static series", "type":"select record", "options": series, 'default':sel},
        {"label":"Tolerance (smaller = slower but more accurate)", "type":"float", 'value':0.1, 'minimum':0.001}, 
        title = "Please select coregistration parameters (slice-by-slice translation with sum-of-squares)")
    if cancel:
        return
    coregistered = vreg.sbs_translation_sos(f[0], f[1], tolerance=f[2]["value"])
    app.display(coregistered)
    app.refresh()


def _rigid_sos(app):
    series = app.database().series()
    sel = app.selected('Series')
    cancel, f = app.dialog.input(
        {"label":"Moving series", "type":"select record", "options": series, 'default':sel},
        {"label":"Static series", "type":"select record", "options": series, 'default':sel},
        {"label":"Tolerance (smaller = slower but more accurate)", "type":"float", 'value':0.1, 'minimum':0.001}, 
        title = "Please select coregistration parameters (rotation sum of squares)")
    if cancel:
        return
    coregistered = vreg.rigid_sos(f[0], f[1], tolerance=f[2]["value"])
    app.display(coregistered)
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


action_translation_sos = Action('Translation (cost = sum of squares)', on_clicked=_translation_sos, is_clickable=_if_a_database_is_open)
action_rigid_sos = Action('Rigid (cost = sum of squares)', on_clicked=_rigid_sos, is_clickable=_if_a_database_is_open)
action_rigid_around_com_sos = Action('Rigid around center of mass (cost = sum of squares)', on_clicked=_rigid_around_com_sos, is_clickable=_if_a_database_is_open)

action_sbs_translation_sos = Action('Slice-by-slice translation (cost = sum of squares)', on_clicked=_sbs_translation_sos, is_clickable=_if_a_database_is_open)
action_sbs_rigid_around_com_sos = Action('Slice-by-slice rigid around center of mass (cost = sum of squares)', on_clicked=_sbs_rigid_around_com_sos, is_clickable=_if_a_database_is_open)


menu_coreg = Menu('Coregister (vreg)')
menu_coreg.add(action_translation_sos)
menu_coreg.add(action_rigid_sos)
menu_coreg.add(action_rigid_around_com_sos)
menu_coreg.add_separator()
menu_coreg.add(action_sbs_translation_sos)
menu_coreg.add(action_sbs_rigid_around_com_sos)