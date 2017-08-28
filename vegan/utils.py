"""Various util functions used by vegan classes."""


def simple_log(msg, err=False):
    """Print a log message to stdout and then return it."""
    lmsg = ""

    if not err:
        lmsg = "\n[*] %s" % str(msg)
    else:
        lmsg = "\n[x] %s" % str(msg)

    print(lmsg, flush=True)
    return lmsg
