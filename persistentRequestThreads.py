import requests, time, sys, queue
from common import eprint

def initThreads(maxThreads):
    """
    Return arrays of resources per thread
    :param maxThreads: int
    :return: list
    """
    th = [None] * maxThreads
    thSession = [None] * maxThreads
    for i in range(maxThreads):
        thSession[i] = requests.session()
    return th, thSession


def findFreeThreadSlot(th, thIdx):
    """
    Search for a free slot, with memory (so acts as round-robin)
    :param th:
    :param thIdx:
    :return:
    """
    t = (thIdx+1) % len(th)
    while True:
        if th[t] == None:                       # empty slot
            return t
        elif not th[t].is_alive():              # thread just finished
            th[t] = None
            return t
        else:                                   # keep searching
            t = (t+1) % len(th)
            if t == thIdx:
                # already polled each slot once this call - so wait a while
                time.sleep(0.1)


def gatherThreads(th, gatherTimeout):
    """
    Wait for threads to complete, marking them as None when done. Get logging results text back from queue, as this is
    thread-safe and process-safe
    :param th:
    :param gatherTimeout:
    :return:
    """
    for i, tj in enumerate(th):
        if tj:
            tj.join(timeout=gatherTimeout)  # for safety in case a thread hangs, set a timeout
            if tj.is_alive():
                eprint('Thread {} timed out'.format(i))
            th[i] = None


def doStuff(maxThreads):
    th, thSession = initThreads(maxThreads)
    resultsQ = queue.Queue()
    thIdx = 0                                       # round-robin slot
    for fname in fnameList:
        if os.path.isfile(fname):
            # check and get a free process space
            thIdx = findFreeThreadSlot(th, thIdx)
            th[thIdx] = threading.Thread(target=processMail, args=(fname, probs, shareRes, resultsQ, thSession[thIdx], openClickTimeout, userAgents, signalsTrafficPrefix, signalsOpenDays))
            th[thIdx].start()                      # launch concurrent process
            countDone += 1
            emitLogs(resultsQ)
    # check any remaining threads to gather back in
    gatherThreads(logger, th, gatherTimeout)
    emitLogs(resultsQ)
