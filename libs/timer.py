# coding: utf-8
import time
from libs.logger import logger


local_indent = 1
name = 'unknown'
start = None
counter = 0


def timer(title=''): #todo: request start parameter
    def wrapper(f):
        def call(*args, **kwargs):
            global local_indent
            name = f.__name__ if not title else title
            message = '™%s↓ %s ' % (' ' * local_indent, name)
            logger.debug(message)
            print message
            local_indent += 1
            start = time.time()
            res = f(*args, **kwargs)
            finished = time.time()
            delta = finished - start
            local_indent -= 1
            message = '™%s↑ %s in %.3f' % (' ' * local_indent, name, delta)
            logger.debug(message)
            print message
            return res
        return call
    return wrapper


def ts(title='inline code'):
    global local_indent, start, name, counter
    counter = 0
    name = title
    message = '™%s↓ %s ' % (' ' * local_indent, name)
    logger.debug(message)
    print message
    local_indent += 1
    start = time.time()


def ti(mod=10000):
    global counter
    counter += 1
    if not counter % mod:
        message = '™%s· %d passed' % (' ' * local_indent, counter)
        print message


def tc(mod=10000):
    global local_indent, start, name, counter
    counter += 1
    if not counter % mod:
        delta = time.time() - start
        passed = " (%d passed)" % counter if counter else ''
        message = '™%s→ %s%s in %.3f' % (' ' * local_indent, name, passed, delta)
        logger.debug(message)
        print message


def tp():
    global local_indent, start, name, counter
    finished = time.time()
    delta = finished - start
    local_indent -= 1
    passed = "(%d passed)" % counter if counter else ''
    message = '™%s↑ %s%s in %.3f' % (' ' * local_indent, name, passed, delta)
    logger.debug(message)
    print message
