import compare
from create_db import database
from STT import speech
import warnings

warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")

database()
speech()