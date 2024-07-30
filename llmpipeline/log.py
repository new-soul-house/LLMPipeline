import logging
import datetime
from pathlib import Path
from rich.console import Console
from rich.logging import RichHandler
from logging.handlers import RotatingFileHandler

LOG_DIR = 'logs'
LOGFORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOGFORMAT_RICH = '%(message)s'
rh = RichHandler(console=Console(stderr=True))
rh.setFormatter(logging.Formatter(LOGFORMAT_RICH))
log_dir = Path(LOG_DIR)
log_dir.mkdir(exist_ok=True, parents=True)
log_fiel = log_dir / f"{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
logging.basicConfig(level="NOTSET", format=LOGFORMAT, datefmt="[%X]", handlers=[rh, RotatingFileHandler(log_fiel)])
log = logging.getLogger("rich")