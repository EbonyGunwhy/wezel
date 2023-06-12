from wezel.gui import Menu
from wezel.plugins import (
    dipy,
    elastix,
    skimage,
    scipy,
    vreg,
)

menu = Menu('Align')
menu.add(scipy.action_overlay_on)
menu.add_separator()
menu.add(elastix.menu)
menu.add(skimage.menu_coreg)
menu.add(dipy.menu_coreg)
menu.add(vreg.menu_coreg)