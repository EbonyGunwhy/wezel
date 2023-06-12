import sys
import os
import shutil
import timeit
import numpy as np
from PySide2.QtWidgets import QApplication, QWidget
import dbdicom as db
import wezel
from wezel import widgets, canvas


datapath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
twofiles = os.path.join(datapath, 'TWOFILES')
onefile = os.path.join(datapath, 'ONEFILE')
rider = os.path.join(datapath, 'RIDER')
rider_full = os.path.join(datapath, 'RIDER Neuro MRI-3369019796')
zipped = os.path.join(datapath, 'ZIP')
multiframe = os.path.join(datapath, 'MULTIFRAME')
skull_ct = os.path.join(datapath, '2_skull_ct')
tristan = 'C:\\Users\\steve\\Dropbox\\Data\\wezel_dev_tristan'

# Helper functions

def create_tmp_database(path=None, name='tmp'):
    tmp = os.path.join(os.path.dirname(__file__), name)
    if os.path.isdir(tmp):
        shutil.rmtree(tmp)
    if path is not None:
        shutil.copytree(path, tmp)
    else:
        os.makedirs(tmp)
    return tmp

def remove_tmp_database(tmp):
    shutil.rmtree(tmp)


##
## Tests
##



def test_build():
    pass
    # To build an executable of the application
    # -----------------------------------------
    # Turn off dropbox
    # place any required hooks in the directory of the main script.
    # pip install pyinstaller
    # pyinstaller --name wezel --clean --onefile --noconsole --additional-hooks-dir=. exec.py

def test_launch():

    #tmp = create_tmp_database(onefile)
    #tmp = create_tmp_database(rider)
    tmp = tristan

    app = wezel.app()
    #app.set_app(wezel.apps.dicom.Windows)
    app.open(tmp)
    #app.set_menu(wezel.menus.test)
    app.show()

    if tmp != tristan:
        remove_tmp_database(tmp)
    

def test_DICOMFolderTree(interactive = True):

    tmp = create_tmp_database(rider)
    #tmp = tristan
    database = db.database(tmp)

    app = QApplication(sys.argv)
    start = timeit.default_timer()
    window = widgets.DICOMFolderTree(database)
    stop = timeit.default_timer()
    window.selectRecords(database.patients()[0].studies()[0].uid)
    window.selectRecords(database.patients()[-1].uid)
    window.itemSelectionChanged.connect(lambda record: print('Selection changed for ' + record['label']))
    window.itemDoubleClicked.connect(lambda record: print('Double click on ' + record['label']))
    if interactive:
        window.show()
        app.exec_()

    print('Time for buiding display (sec)', stop-start)

    remove_tmp_database(tmp)


def test_SeriesSliders(interactive = True):

    tmp = create_tmp_database(rider)
    #tmp = tristan
    database = db.database(tmp)
    #series = database.series()[5]
    series = db.merge(database.series())

    app = QApplication(sys.argv)
    window = widgets.SeriesSliders(series)
    window.valueChanged.connect(lambda image: 
        print('No image') if image is None else print('Image ' + str(image.InstanceNumber))
    )
    
    if interactive:
        window.show()
        app.exec_()

    remove_tmp_database(tmp)


def test_SelectImageColorMap(interactive = True):

    tmp = create_tmp_database(rider)
    database = db.database(tmp)
    images = database.instances()

    app = QApplication(sys.argv)
    window = widgets.SelectImageColorMap(images[0])
    window.newColorMap.connect(lambda clr: print('New color map: ', clr))
    window.setValue('Greens')

    if interactive:
        print('Original color map: ', images[0].colormap)
        window.show()
        app.exec_()
        print('New color map (check): ', images[0].colormap)
    else:
        assert images[0].colormap == 'Greens'

    remove_tmp_database(tmp)


def test_ImageBrightness(interactive = True):

    tmp = create_tmp_database(rider)
    database = db.database(tmp)
    images = database.instances()

    app = QApplication(sys.argv)
    window = widgets.ImageBrightness(images[0])
    window.valueChanged.connect(lambda value: print('New brightness: ', value))
    window.setValue(100)
    
    if interactive:
        print('Original brightness: ', images[0].WindowCenter)
        window.show()
        app.exec_()
        print('New brightness (check): ', images[0].WindowCenter)
    else:
        window.raise_()
        assert images[0].WindowCenter == 100

    remove_tmp_database(tmp)


def test_ImageContrast(interactive = True):

    tmp = create_tmp_database(rider)
    database = db.database(tmp)
    images = database.instances()

    app = QApplication(sys.argv)
    window = widgets.ImageContrast(images[0])
    window.valueChanged.connect(lambda value: print('New contrast: ', value))
    window.setValue(100)
    
    if interactive:
        window.show()
        app.exec_()
        print('New contrast (check): ', images[0].WindowWidth)
    else:
        assert images[0].WindowWidth == 100

    remove_tmp_database(tmp)


def test_PixelValueLabel(interactive = True):

    tmp = create_tmp_database(rider)
    database = db.database(tmp)
    images = database.instances()

    app = QApplication(sys.argv)
    window = widgets.PixelValueLabel(images[0])
    window.setValue([10,20])
    
    if interactive:
        window.show()
        app.exec_()

    remove_tmp_database(tmp)


def test_ImageColors(interactive = True):

    tmp = create_tmp_database(rider)
    database = db.database(tmp)
    images = database.instances()

    app = QApplication(sys.argv)
    window = widgets.ImageColors(images[0])
    window.valueChanged.connect(lambda clrs: 
        print('New color settings: ', clrs)
    )
    window.setValue('Oranges', 100, 200)
    
    if interactive:
        window.show()
        app.exec_()
        print(
            'New color settings (check): ', 
            images[0].colormap, 
            images[0].WindowCenter, 
            images[0].WindowWidth, 
        )
    else:
        assert images[0].colormap == 'Oranges'
        assert images[0].WindowCenter == 100
        assert images[0].WindowWidth == 200

    remove_tmp_database(tmp)


def test_Canvas(interactive=True):

    tmp_rider = create_tmp_database(rider, 'tmp_rider')
    database = db.database(tmp_rider)
    images = database.instances()

    app = QApplication(sys.argv)
    cnvs = canvas.Canvas()
    cnvs.setImage(images[0])
    
    #msk_blank = cnvs.setMask(images[0].copy(), color=1, opacity=0.5)

    #cnvs.setFilter(canvas.PanFilter()) 
    toolBar = canvas.ToolBar()
    toolBar.setCanvas(cnvs)

    cnvs.show()
    toolBar.show()

    if interactive:
        app.exec_()
    else:
        cnvs.raise_()

    remove_tmp_database(tmp_rider)
    #remove_tmp_database(tmp_skull_ct)


def test_SeriesCanvas(interactive = True):

    #tmp_rider = create_tmp_database(rider, 'tmp')

    #database = db.database(tmp_rider)
    database = db.database(rider_full)
    database.save()
    series = database.series()

    app = QApplication(sys.argv)

    seriesCanvas = widgets.SeriesCanvas()
    seriesCanvas.setImageSeries(series[0])
    seriesCanvas.setMaskSeries(series[0].new_sibling())

    toolBar = canvas.ToolBar()
    toolBar.setSeriesCanvas(seriesCanvas)

    toolBar.show()
    #seriesCanvas.show()

    # seriesCanvas2 = widgets.SeriesCanvas()
    # seriesCanvas2.setImageSeries(series[1])
    # seriesCanvas2.setMaskSeries(series[1].new_sibling())
    # toolBar.setSeriesCanvas(seriesCanvas2)
    # seriesCanvas2.show()

    if interactive:
        app.exec_()

    database.restore()
    #remove_tmp_database(tmp_rider)
    #remove_tmp_database(tmp_skull_ct)


if __name__ == "__main__":

    interactive=True

    test_launch()
    # test_DICOMFolderTree(interactive)
    # test_SeriesSliders(interactive)
    # test_SelectImageColorMap(interactive)
    # test_ImageBrightness(interactive)
    # test_ImageContrast(interactive)
    # test_PixelValueLabel(interactive)
    # test_ImageColors(interactive)
    # test_Canvas(interactive)
    # test_SeriesCanvas(interactive)


    print('-----------------------')
    print('wezel passed all tests!')
    print('-----------------------')