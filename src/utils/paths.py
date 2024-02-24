import os


class PathConfig:
    ROOT = os.getcwd()
    SRC = os.path.join(ROOT, "src")
    DATA = os.path.join(SRC, "data")
    INDEXER = os.path.join(SRC, "indexer")
    SCRAPER = os.path.join(SRC, "scraper")
    LOG = os.path.join(ROOT, "log")

    if not os.path.isdir(LOG):
        os.mkdir(LOG)
