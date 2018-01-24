#!/usr/bin/python
#-*-coding:utf-8-*-
"""

License
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    S the License for the specific language governing permissions and
    limitations under the License.

Brief
    logging helper
"""

import sys
import time
import logging
import logging.handlers

DEFAULT_LOGFMT = '[%(asctime)s][%(filename)s - %(lineno)s][%(levelname)s] $> %(message)s'
DEFAULT_DATAFMT = '%(message)s'
g_logger = None

# common logger creater
# @param logfile - name represent log file
# @param module - name represent log object
# @param loglevel - logging.[CRITICAL, ERROR, WARNING, INFO, DEBUG]
# @param stream - sys.stdout or sys.stderr
# @param b_append_lvlname - append level name to log
def _log2file(logfile, module=None, loglevel = logging.INFO, logfmt = DEFAULT_LOGFMT):
    #module = time.strftime(module + "_%Y-%m-%d", time.localtime(time.time()))
    logger = logging.getLogger(module)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(fmt=logfmt, datefmt='%Y-%m-%d %H:%M:%S')

    # logger | debug file
    loghandler = logging.handlers.RotatingFileHandler(logfile, maxBytes = 1024*1024*1024, backupCount = 5) # 实例化handle
    loghandler.setFormatter(formatter)
    loghandler.setLevel(loglevel)
    logger.addHandler(loghandler)
    logger.info("#### start ####")
    return logger

# log to stdout or stderr
def _log2stream(stream, module=None, loglevel = logging.INFO, logfmt = DEFAULT_LOGFMT):
    logger = logging.getLogger(module)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(fmt=logfmt, datefmt='%Y-%m-%d %H:%M:%S')

    if stream == sys.stdout or stream == sys.stderr:
        loghandler = logging.StreamHandler(stream)
        loghandler.setFormatter(formatter)
        loghandler.setLevel(loglevel)
        logger.addHandler(loghandler)
    #
    return logger

def log2stdout(module=None, loglevel = logging.INFO, logfmt = DEFAULT_DATAFMT):
    return _log2stream(sys.stdout, module, loglevel, logfmt)

def log2stderr(module=None, loglevel = logging.ERROR, logfmt = DEFAULT_DATAFMT):
    return _log2stream(sys.stderr, module, loglevel, logfmt)

# set root log file
def log2file(logfile, loglevel = logging.INFO, logfmt = DEFAULT_LOGFMT):
    return _log2file(logfile, None, loglevel, logfmt)

# @param module - auto append ".log"
def log2data(module, logfile = None, loglevel = logging.INFO, logfmt = DEFAULT_DATAFMT):
    if logfile is None:
        logfile = module + ".data"

    return _log2file(logfile, module, loglevel, logfmt)

def setlogger(logger):
    global g_logger
    g_logger = logger