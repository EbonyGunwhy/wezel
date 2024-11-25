from wezel.gui import Menu
from wezel.plugins import (
    dipy,
    elastix,
    skimage,
    scipy,
    vreg,
)

menu = Menu('Align')
#menu.add(scipy.action_overlay_on)
menu.add(vreg.action_overlay_on)
menu.add_separator()
menu.add(vreg.action_translation)
menu.add(vreg.action_sbs_translation)
menu.add_separator()
menu.add(vreg.action_rigid)
menu.add(vreg.action_sbs_rigid)
menu.add_separator()
menu.add(elastix.menu)
menu.add(skimage.menu_coreg)
menu.add(dipy.menu_coreg)
menu.add(vreg.menu_coreg_wip)