import numpy as np
from wezel.gui import Menu, Action
from wezel.plugins import numpy, scipy


def is_series_selected(app):
    return app.nr_selected('Series') != 0  

def series_multislice_to_volume(app): 
    for sel in app.selected('Series'):
        affine = sel.affine_matrix()
        if not isinstance(affine, list):
            affine = [affine]
        n = np.sum([len(slice_group[1]) for slice_group in affine])
        cnt = 0
        for slice_group in affine:
            if len(slice_group[1]) != 1:
                slice_spacing = np.linalg.norm(slice_group[0][:3, 2])
                slice_thickness = slice_group[1][0].SliceThickness
                if slice_thickness != slice_spacing:
                    volume = sel.new_sibling(suffix='3D volume')
                    for image in volume.adopt(slice_group[1]):
                        sel.progress(cnt+1, n, 'Converting multislice to volume..')
                        image.SliceThickness = slice_spacing
    app.refresh()


action_ms_to_vol = Action('2D multislice -> 3D volume', on_clicked=series_multislice_to_volume, is_clickable=is_series_selected)


menu = Menu('Transform')
menu.add(scipy.action_function_of_one_series)
menu.add(scipy.action_function_of_two_series)
menu.add(scipy.action_function_of_n_series)
menu.add_separator()
menu.add(scipy.action_distance_transform_edit_3d)
menu.add_separator()
menu.add(numpy.menu_project)
menu.add_separator()
menu.add(scipy.action_zoom)
menu.add(scipy.action_resample_3d_isotropic)
menu.add(scipy.action_resample_3d)
menu.add_separator()
menu.add(action_ms_to_vol)
menu.add_separator()
menu.add(scipy.action_reslice_axial)
menu.add(scipy.action_reslice_coronal)
menu.add(scipy.action_reslice_sagittal)
