"""
`widgets` is a collection of PyQt widgets that can be used as components 
in `wezel` applications.

"""

from .series_display_4d import (
    SeriesDisplay4D,
)
from .series_display import (
    SeriesDisplay,
)
from .plot_display import (
    PlotDisplay,
    MatplotLibDisplay,
)
from .table_display import (
    TableDisplay,
)
from .dicom_header import (
    SeriesViewerMetaData,
)