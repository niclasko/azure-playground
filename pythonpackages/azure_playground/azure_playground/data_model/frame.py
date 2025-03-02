from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from numpy import ndarray
from pydantic import BaseModel


class Frame(BaseModel):
    offset: float
    image: Path

    def view(self) -> None:
        img: ndarray = mpimg.imread(self.image)
        plt.imshow(img)
        plt.axis("off")  # Hide axes
        plt.show()
