import random
import numpy as np
import scipy.ndimage as ndi
import pyvista as pv
from pyvistaqt import QtInteractor
from PySide2.QtWidgets import QVBoxLayout
from wezel.gui import Action, MainWidget
from dbdicom.wrappers import scipy


class SurfaceDisplay(MainWidget):

    def __init__(self, series, reference=None, triangulate=False):

        # Initialize UI
        super().__init__()
        self.initUI()

        # For convenience ensure series are a list
        if not isinstance(series, list):
            series = [series]

        # Display data
        if reference is None:

            # Display all series in color and opaque
            self.setSeries(series[0], color=0, opacity=1.0, triangulate=triangulate)
            for clr, s in enumerate(series[1:]):
                self.addSeries(s, color=clr+1, opacity=1.0, triangulate=triangulate)

        else:

            # For convenience ensure references are a list.
            if not isinstance(reference, list):
                reference = [reference]

            # Display references in transparent white
            self.setSeries(reference[0], color=-1, opacity=0.5, triangulate=triangulate)
            for r in reference[1:]:
                self.addSeries(r, color=-1, opacity=0.5, triangulate=triangulate)

            # Display all other data in opaque colors
            for clr, s in enumerate(series):
                self.addSeries(s, color=clr, opacity=1.0, triangulate=triangulate)


    def initUI(self):

        # Widgets
        self.plotter = QtInteractor(self)

        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.plotter)
        self.setLayout(layout)


    def setSeries(self, series, color=0, opacity=1.0, triangulate=False):

        # Save for reuse
        self.series = series
        if series is None:
            return

        # Get affine matrix
        affine = series.affine_matrix()
        if isinstance(affine, list):
            msg = 'Cannot display this as a single volume \n'
            msg += 'This series contains multiple slice groups.'
            series.dialog.information(msg)
            return
        else:
            affine = affine[0]

        # Get geometry
        column_spacing = np.linalg.norm(affine[:3, 0])
        row_spacing = np.linalg.norm(affine[:3, 1])
        slice_spacing = np.linalg.norm(affine[:3, 2])
        spacing = (column_spacing, row_spacing, slice_spacing)  # mm

        # Get array sorted by slice location
        # If there are multiple volumes, show only the first one
        arr, _ = series.array('SliceLocation', pixels_first=True, first_volume=True)

        series.status.message('Preprocessing mask...')

        # Scale in the range [0,1] so it can be treated as mask
        max = np.amax(arr)
        min = np.amin(arr)
        arr -= min
        arr /= max-min

        # add zeropadding at the boundary slices
        array = _zeropad(arr)

        # Smooth surface
        array = ndi.gaussian_filter(array, 0.5)

        series.status.message('Displaying surface...')

        # Extracting surface
        self.grid = pv.UniformGrid(dimensions=array.shape, spacing=spacing)
        surf = self.grid.contour([0.5], array.flatten(order="F"), method='marching_cubes')
        if triangulate:
            surf = surf.reconstruct_surface()

        self.plotter.add_mesh(surf, 
            color = _RGB(color), 
            opacity = opacity, 
            show_edges = False, 
            smooth_shading = True, 
            specular = 0, 
            show_scalar_bar = False,
        )

        # Surface colour coded based on x-coordinate
        # self.plotter.add_mesh(surf, 
        #     scalars = np.linalg.norm(surf.points, axis=1),
        #     cmap = "plasma",  
        #     show_edges = False, 
        #     smooth_shading = True, 
        #     specular = 0, 
        #     show_scalar_bar = False,
        #     opacity = 1.0)

        ## Note: In script, plotting can also be done as:
        # surf.plot(scalars=dist, show_edges=False, smooth_shading=True, specular=5, cmap="plasma", show_scalar_bar=False)

        # Extracting surfaces with skimage causes erratic crashes of PolyData
        # verts, faces, _, _ = skimage.measure.marching_cubes(array, level=0.5, spacing=spacing, step_size=1.0)
        # cloud = pv.PolyData(verts, faces, n_faces=faces.shape[0])
        # surf = cloud.reconstruct_surface()


    def addSeries(self, series, color=-1, opacity=0.5, triangulate=False):

        if series is None:
            return
        if self.series is None:
            return
        
        arr, _ = scipy.mask_array(series, on=self.series)
        if isinstance(arr, list):
            msg = 'Cannot display reference as a single volume \n'
            msg += 'This series contains multiple slice groups.'
            series.dialog.information(msg)
            return
        else:
            # If there are multiple acquisitions per slice, use only the first.
            arr = arr[...,0]

        series.status.message('Preprocessing mask...')

        # add zeropadding at the boundary slices 
        array = _zeropad(arr)

        ## Smooth surface
        #array = ndi.gaussian_filter(array, 0.5)

        series.status.message('Displaying surface...')

        # Extracting surface
        surf = self.grid.contour([0.5], array.flatten(order="F"), method='marching_cubes')
        #surf = self.grid.contour([0.0], array.flatten(order="F"), method='marching_cubes')
        if triangulate:
            surf = surf.reconstruct_surface()

        # Plot surface transparent
        self.plotter.add_mesh(surf, 
            #color = 'white',
            color = _RGB(color),
            opacity = opacity,
            show_edges = False, 
            smooth_shading = True, 
            specular = 0, 
            show_scalar_bar = False,
        )
        


def _zeropad(arr):
    # Helper function
    # add zeropadding at the boundary slices
    shape = list(arr.shape)
    npad = 4
    shape[-1] = shape[-1] + 2*npad
    array = np.zeros(shape)
    array[:,:,npad:-npad] = arr 
    return array  


def _RGB(color):
    # Helper function
    # Return an RGB color based on an integer
    if color == -1:
        return [255, 255, 255]
    elif color == 0:
        return [255, 0, 0]
    elif color == 1:
        return [0, 255, 0]
    elif color == 2:
        return [0, 0, 255]
    elif color == 3:
        return [0, 255, 255]
    elif color == 4:
        return [255, 0, 255]
    elif color == 5:
        return [255, 255, 0]
    elif color == 6:
        return [0, 128, 255]
    elif color == 7:
        return [255, 0, 128]
    elif color == 8:
        return [128, 255, 0]
    else:
        return [
            random.randint(0,255), 
            random.randint(0,255), 
            random.randint(0,255),
        ]



##########################
### wezel menu buttons ###
##########################



def _show_mask_surface(app):
    for series in app.selected('Series'):
        viewer = SurfaceDisplay(series)
        app.addWidget(viewer, title=series.label())


def _show_mask_surfaces(app):
    sel = app.selected('Series')
    all = app.database().series()
    cancel, f = app.dialog.input(
        {'label':'Base surface to display', 'type':'select record', 'options':all, 'default':sel},
        {'label':'Other surface(s)', 'type':'select records', 'options':all, 'default':sel},
        {'label':'Triangulate surface?', 'type':'dropdownlist', 'list':['Yes','No'], 'value':1},
    )
    if cancel:
        return
    viewer = SurfaceDisplay([f[0]] + f[1], triangulate=f[2]['value']==0)
    app.addWidget(viewer, title=f[0].label())


def _show_mask_surfaces_with_reference(app):
    sel = app.selected('Series')
    all = app.database().series()
    cancel, f = app.dialog.input(
        {'label':'Reference surface', 'type':'select record', 'options':all, 'default':sel},
        {'label':'Surface(s) to display', 'type':'select records', 'options':all, 'default':sel},
        {'label':'Triangulate surface?', 'type':'dropdownlist', 'list':['Yes','No'], 'value':1},
    )
    if cancel:
        return
    viewer = SurfaceDisplay(f[1], reference=f[0], triangulate=f[2]['value']==0)
    app.addWidget(viewer, title=f[1][0].label())


def _if_a_database_is_open(app):
    return app.database() is not None


def _if_a_series_is_selected(app):
    return app.nr_selected('Series') != 0


action_show_mask_surface = Action('Single 3D surface', on_clicked=_show_mask_surface, is_clickable=_if_a_series_is_selected)
action_show_mask_surfaces = Action('Multiple 3D surfaces', on_clicked=_show_mask_surfaces, is_clickable=_if_a_database_is_open)
action_show_mask_surfaces_with_reference = Action('3D surface(s) with reference', on_clicked=_show_mask_surfaces_with_reference, is_clickable=_if_a_database_is_open)

