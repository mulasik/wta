from typing import Literal

from matplotlib import ArrayLike, Color
from matplotlib.artist import Artist
from matplotlib.container import BarContainer
from matplotlib.patches import Wedge
from matplotlib.text import Text

class Axes:
    def legend(
        self, handles: list[Artist] = ..., labels: list[str] = ..., *, loc: str = ...
    ) -> None: ...
    def bar(
        self,
        x: float | ArrayLike,
        height: float | ArrayLike,
        width: float | ArrayLike = ...,
        bottom: float | ArrayLike = ...,
        *,
        align: Literal["center", "edge"] = "center",
        label: str = ...,
        color: Color = ...,
        edgecolor: Color = ...,
        alpha: float = ...,
    ) -> BarContainer: ...
    def barh(
        self,
        y: float | ArrayLike,
        width: float | ArrayLike,
        height: float | ArrayLike = ...,
        left: float | ArrayLike = ...,
        *,
        align: Literal["center", "edge"] = "center",
        label: str = ...,
        color: Color = ...,
        edgecolor: Color = ...,
        alpha: float = ...,
    ) -> BarContainer: ...
    def pie(
        self,
        x: ArrayLike,
        explode: ArrayLike | None = None,
        labels: list[str] | None = None,
        colors: ArrayLike | None = None,
        autopct: None | str = None,
        pctdistance: float = 0.6,
        shadow: bool = False,
        labeldistance: float | None = 1.1,
        startangle: float = 0,
        radius: float = 1,
        counterclock: bool = True,
        center: tuple[float, float] = (0, 0),
        frame: bool = False,
        rotatelabels: bool = False,
        *,
        normalize: bool = True,
    ) -> tuple[list[Wedge], list[Text], list[Text]]: ...
    def set_xlabel(
        self,
        xlabel: str,
        labelpad: float = ...,
        *,
        loc: Literal["left", "center", "right"] = ...,
    ) -> None: ...
    def set_ylabel(
        self,
        ylabel: str,
        labelpad: float = ...,
        *,
        loc: Literal["bottom", "center", "top"] = ...,
    ) -> None: ...
    def set_title(
        self,
        label: str,
        loc: Literal["center", "left", "right"] = ...,
        pad: float = ...,
        *,
        y: float = ...,
        horizontalalignment: str = ...,
    ) -> Text: ...
    def get_legend_handles_labels(self) -> tuple[list[Artist], list[str]]: ...
    def set_xlim(
        self,
        bottom: float = ...,
        top: float = ...,
        *,
        emit: bool = ...,
        auto: bool = ...,
        ymin: float = ...,
        ymax: float = ...,
    ) -> None: ...
    def set_ylim(
        self,
        bottom: float = ...,
        top: float = ...,
        *,
        emit: bool = ...,
        auto: bool = ...,
        ymin: float = ...,
        ymax: float = ...,
    ) -> None: ...
    def tick_params(
        self,
        axis: Literal["both", "x", "y"] = ...,
        *,
        direction: Literal["in", "out", "inout"] = ...,
        length: float = ...,
        width: float = ...,
        color: Color = ...,
        pad: float = ...,
        labelsize: float | str = ...,
        labelcolor: Color = ...,
        colors: Color = ...,
        zorder: float = ...,
        bottom: bool = ...,
        top: bool = ...,
        left: bool = ...,
        right: bool = ...,
        labelbottom: bool = ...,
        labeltop: bool = ...,
        labelleft: bool = ...,
        labelright: bool = ...,
        labelrotation: float = ...,
        grid_color: Color = ...,
        grid_alpha: float = ...,
        grid_linewidth: float = ...,
        grid_linestyle: str = ...,
        which: str = ...,
    ) -> None: ...
    def label_outer(self) -> None: ...
