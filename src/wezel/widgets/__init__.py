"""
`widgets` is a collection of PyQt widgets that can be used as components 
in `wezel` applications.

"""

#from .log_to_GUI import *

from .dbimage import (
    ImageWindow,
)
from .series_sliders import (
    SeriesSliders,
)
from .plot_curve import (
    PlotCurve,
)
from .qrangeslider import (
    QRangeSlider,
)
from .sliders import (
    IndexSlider, 
    LabelSlider, 
    CheckBoxSlider,
)
from .main_mdi import (
    MainMultipleDocumentInterface, 
)
from .message import (
    Dialog, 
    StatusBar,
)
from .user_input import (
    UserInput,
)
from .dbdatabase import (
    DICOMFolderTree,
)
from .region_list import (
    RegionList,
)
from .file_display import (
    ImageLabel,
    MatplotLib,
)