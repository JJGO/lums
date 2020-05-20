class color:
    MAGENTA      = "\033[95m"
    PURPLE       = "\033[35m"
    CYAN         = "\033[96m"
    DARKCYAN     = "\033[36m"
    BLUE         = "\033[94m"
    NAVY         = "\033[34m"
    GREEN        = "\033[92m"
    GRASS        = "\033[32m"
    ORANGE       = "\033[93m"
    YELLOW       = "\033[33m"
    RED          = "\033[91m"
    FADERED      = "\033[31m"
    GREY         = "\033[90m"
    BOLD         = "\033[1m"
    UNDERLINE    = "\033[4m"
    END          = "\033[0m"


def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 *
                                                     (iteration / float(total)))
    if len(percent) < 2 and decimals == 0:
        percent = " "+percent
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    # print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='\r')
    # Print New Line on Complete
    if iteration == total:
        print()
