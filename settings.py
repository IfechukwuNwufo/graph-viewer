
from typing import Final
from typing import Callable, Literal, IO, Union
from os import PathLike
import pygame

# Game RES
SCR_WIDTH: Final = 650
SCR_HEIGHT: Final = 650
FPS: Final = 60

# Game Screen
SCREEN_BG_COLOR = 'black'

# Type Aliases
type _AnyPath = Union[str, bytes, PathLike[str], PathLike[bytes]]
type Number = Union[float, int]
type ColorType = Union[pygame.Color, tuple[Number, Number, Number, Number], list[Number, Number, Number, Number], str]
type SupportsPositionAndSize = Union[list[Number, Number], tuple[Number, Number]]
type FileType = Union[_AnyPath, IO[bytes], IO[str]]

