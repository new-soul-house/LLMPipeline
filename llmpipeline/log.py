import logging
import datetime
from pathlib import Path
from rich.console import Console
from rich.logging import RichHandler
from logging.handlers import RotatingFileHandler

def beijing(sec, what):
    beijing_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    return beijing_time.timetuple()

LOG_DIR = 'logs'
MAXBYTES = 10000000 # ~10M
LOGFORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOGFORMAT_RICH = '%(message)s'
rh = RichHandler(console=Console(stderr=True))
rh.setFormatter(logging.Formatter(LOGFORMAT_RICH))
log_dir = Path(LOG_DIR)
log_dir.mkdir(exist_ok=True, parents=True)
log_file = log_dir / f"{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
logging.Formatter.converter = beijing
logging.basicConfig(level="NOTSET", format=LOGFORMAT, datefmt="[%y-%m-%d %H:%M:%S]", handlers=[rh, RotatingFileHandler(log_file, maxBytes=MAXBYTES)])
log = logging.getLogger("llmpipeline")