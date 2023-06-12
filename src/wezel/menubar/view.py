from wezel import displays
from wezel.gui import Menu, Action

   

def no_database(app):
    if app.database() is None:
        return False
    if app.treeViewDockWidget is None:
        return False
    #return not app.treeViewDockWidget.isVisible()
    return True


def show_database(app):
    app.treeViewDockWidget.show()
    app.menuBar().enable()


def is_series_selected(app):
    return app.nr_selected('Series') != 0


def show_series_2d(app):
    for series in app.selected('Series'):
        app.display(series)      
    #app.central.tileSubWindows()      


def show_series_4d(app):
    for series in app.selected('Series'):
        viewer = displays.SeriesDisplay4D()
        viewer.setSeries(series)
        app.addWidget(viewer, series.label())


def show_dicom_header(app):
    for series in app.selected('Series'):
        viewer = displays.SeriesViewerMetaData(series)
        app.addWidget(viewer, series.label())


def show_toolbar(app):
    if app.toolBarDockWidget.widget() is None:
        msg = 'There are currently no toolbars available.'
        msg += '\n Please open a display first.'
        app.dialog.information(msg, title='No toolbars available')
        return
    app.toolBarDockWidget.show()
    #self.setEnabled(False)


def close_windows(app):
    app.central.closeAllSubWindows()


def tile_windows(app):
    app.central.tileSubWindows()



action_show_database = Action('Database', on_clicked=show_database, is_clickable=no_database)
action_show_series_2d = Action('Series (2D)', on_clicked=show_series_2d, is_clickable=is_series_selected)
action_show_series_4d = Action('Series (2D + 1D)', on_clicked=show_series_4d, is_clickable=is_series_selected)
action_show_dicom_header = Action('Series (Header)', on_clicked=show_dicom_header, is_clickable=is_series_selected)
action_show_toolbar = Action('Toolbar', on_clicked=show_toolbar, is_clickable=no_database)
action_close_windows = Action('Close windows', on_clicked=close_windows, is_clickable=no_database)
action_tile_windows = Action('Tile windows', on_clicked=tile_windows, is_clickable=no_database)



menu = Menu('View')
menu.add(action_show_database)
menu.add_separator()
menu.add(action_show_series_2d)
menu.add(action_show_series_4d)
menu.add(action_show_dicom_header)
menu.add_separator()
menu.add(action_show_toolbar)
menu.add(action_close_windows)
menu.add(action_tile_windows)
