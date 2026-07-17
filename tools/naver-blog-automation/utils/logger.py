import logging
import sys
from datetime import datetime

from config.settings import LOG_DIR
from utils.mask import SecretMaskingFilter


def setup_logger(name: str = "giftclean_blog", level: int = logging.DEBUG) -> logging.Logger:
    """File(DEBUG) + Console(INFO) 듀얼 로거 설정. 모든 레코드는 비밀값 마스킹을 거친다."""
    LOG_DIR.mkdir(exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger

    mask_filter = SecretMaskingFilter()

    log_file = LOG_DIR / f"{datetime.now():%Y-%m-%d}.log"
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.addFilter(mask_filter)
    fh.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s.%(funcName)s:%(lineno)d - %(message)s"
    ))

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.addFilter(mask_filter)
    ch.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"
    ))

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger
