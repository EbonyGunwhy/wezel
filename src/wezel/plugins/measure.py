
from wezel.gui import Menu
from wezel.plugins import (
    skimage,
    scipy,
)

menu = Menu('Measure')
menu.add(skimage.action_volume_features)
menu.add(scipy.action_roi_statistics)
menu.add(scipy.action_roi_curve)

    




