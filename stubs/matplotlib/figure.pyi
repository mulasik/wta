from matplotlib.artist import Artist

class FigureBase(Artist): ...

class Figure(FigureBase):
    def tight_layout(
        self,
        *,
        pad: float = 1.08,
        h_pad: float = ...,
        w_pad: float = ...,
        rect: tuple[float, float, float, float] = ...
    ) -> None: ...

class SubFigure(FigureBase): ...
