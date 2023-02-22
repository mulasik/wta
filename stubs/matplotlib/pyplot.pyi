from collections.abc import Sequence
from os import PathLike
from typing import Literal, overload

from matplotlib import ArrayLike, Color
from matplotlib.axes import Axes
from matplotlib.figure import Figure, SubFigure
from matplotlib.text import Text

rcParams: dict[str, object]

@overload
def subplots(
    nrows: int = ...,
    ncols: int = ...,
    *,
    squeeze: Literal[False],
    sharex: bool | Literal["none", "all", "row", "col"] = ...,
    sharey: bool | Literal["none", "all", "row", "col"] = ...,
    figsize: tuple[float, float] = ...,
    gridspec_kw: dict[str, object] = ...,
) -> tuple[Figure, list[list[Axes]]]: ...
@overload
def subplots(
    nrows: Literal[1],
    ncols: int,
    *,
    sharex: bool | Literal["none", "all", "row", "col"] = ...,
    sharey: bool | Literal["none", "all", "row", "col"] = ...,
    squeeze: Literal[True] = ...,
    figsize: tuple[float, float] = ...,
    gridspec_kw: dict[str, object] = ...,
) -> tuple[Figure, list[Axes]]: ...
@overload
def subplots(
    nrows: int,
    ncols: Literal[1],
    *,
    sharex: bool | Literal["none", "all", "row", "col"] = ...,
    sharey: bool | Literal["none", "all", "row", "col"] = ...,
    squeeze: Literal[True] = ...,
    figsize: tuple[float, float] = ...,
    gridspec_kw: dict[str, object] = ...,
) -> tuple[Figure, list[Axes]]: ...
@overload
def subplots(
    *,
    sharex: bool | Literal["none", "all", "row", "col"] = ...,
    sharey: bool | Literal["none", "all", "row", "col"] = ...,
    squeeze: Literal[True] = ...,
    figsize: tuple[float, float] = ...,
    gridspec_kw: dict[str, object] = ...,
) -> tuple[Figure, Axes]: ...
def figure(
    num: int | str | Figure | SubFigure | None = ...,
    figsize: Sequence[float] | None = ...,
    dpi: float | None = ...,
    facecolor: Color | None = ...,
    edgecolor: Color | None = ...,
    frameon: bool = ...,
    clear: bool = ...,
) -> Figure: ...
def xticks(
    ticks: ArrayLike = ..., labels: ArrayLike = ...
) -> tuple[list[object], list[Text]]: ...
def yticks(
    ticks: ArrayLike = ..., labels: ArrayLike = ...
) -> tuple[list[object], list[Text]]: ...
def close(fig: Figure = ...) -> None: ...
def savefig(fname: str | PathLike[str], *, bbox_inches: str = ...) -> None: ...
