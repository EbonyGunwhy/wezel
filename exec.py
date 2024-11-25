# To develop the application
# --------------------------
# Navigate to a folder outside of the folder with the source code, 
# for instance C:\Users\steve\Dropbox\Software\QIB-Sheffield\dev
# For Mac OSX
# python3 -m venv .venv_ibeat           
# source .venv_ibeat/bin/activate
# Windows
# py -3 -m venv .venv           # create virtual environment
# .venv/Scripts/activate        # activate virtual environment

# pip install -r requirements.txt
#
# install editable versions of requirements under development, eg.
# pip install -e C:\Users\steve\Dropbox\Software\QIB-Sheffield\dbdicom
# pip install -e C:\Users\steve\Dropbox\Software\QIB-Sheffield\wezel
# pip install -e C:\Users\steve\Dropbox\Software\QIB-Sheffield\mdreg
# pip install -e C:\Users\steve\Dropbox\Software\dcmri


# to build an executable:
# -----------------------
# distribution mode: splash screen, single file and no console
# pyinstaller --name wezel --clean --onefile --noconsole --additional-hooks-dir=. --noconfirm --splash wezel.jpg exec.py

# debug mode: not single file & no splash screen
# pyinstaller --name wezel --clean --noconsole --additional-hooks-dir=. --noconfirm exec.py

# After this, you should see a dist folder which contains a link to the executable wezel.exe
# Troubleshoot: if pyinstaller throws an error, try deleting "build" and "dist" folders before running this command.


import wezel
from wezel.plugins import (
    pyvista,
    scipy,
    measure,
    transform,
    segment,
    align,
    dcmri,
)


if __name__ == "__main__":

    app = wezel.app()
    
    app.add_menu(scipy.menu_filter)
    app.add_menu(segment.menu)
    app.add_menu(align.menu)
    app.add_menu(transform.menu)
    app.add_menu(measure.menu)
    app.add_menu(dcmri.menu)
    app.add_menu(wezel.menubar.about.menu)

    app.add_separator(menu='View', position=5)
    app.add_action(pyvista.action_show_mask_surface, menu='View', position=6)
    app.add_action(pyvista.action_show_mask_surfaces, menu='View', position=7)
    app.add_action(pyvista.action_show_mask_surfaces_with_reference, menu='View', position=8)

    app.show()