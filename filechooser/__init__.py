from filechooser.utils import Proxi
from filechooser import facade_filechooser

filechooser = Proxi('filechooser', facade_filechooser.FileChooser)
