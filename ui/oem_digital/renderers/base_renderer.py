from abc import ABC, abstractmethod
from PyQt5.QtGui import QPainter


class BaseRenderer(ABC):
    """
    Every screen class must inherit this and implement render().
    This enforces a consistent interface across all screens.
    """

    @abstractmethod
    def render(self, painter: QPainter, state) -> None:
        """
        Draw this screen onto `painter` using data from `state`.

        Args:
            painter : active QPainter (screen-space coordinates)
            state   : VehicleState instance
        """
        ...
