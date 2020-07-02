import pandas as pd

def gpu_summary(query, merge=False):
    if merge:
        return merge_summaries({k: gpu_summary(v) for k, v in query.items()})
    data = []
    for i, gpu in enumerate(query):
        data.append({'gpu': str(i), **gpu})
        del data[-1]['processes']
    return pd.DataFrame(data)

def proc_summary(query, merge=False):
    if merge:
        return merge_summaries({k: proc_summary(v) for k, v in query.items()})
    data = []
    for i, gpu in enumerate(query):
        for p in gpu['processes']:
            data.append({'gpu': str(i), **p})
    return pd.DataFrame(data)



def gpu_proc_summary(query, merge=False):
    if merge:
        return merge_summaries({k: gpu_proc_summary(v) for k, v in query.items()})
    gpus = gpu_summary(query)
    procs = proc_summary(query)
    if len(procs) == 0:
        return gpus
    return pd.merge(gpus, procs, how='left', on='gpu')

def merge_summaries(summaries):
    for host, summary in summaries.items():
        summary['host'] = host
    return pd.concat(summaries.values(), sort=False)

def gpu_user_summary(queries):
    # TODO implement for compatibility
    g = df.groupby('userid')
    mem = g['used_memory'].sum() # Total used memory
    nprocs = g['pid'].count() # Total processes
    g['host'].unique() # Unique hosts
    df.groupby('userid')[['host','gpu']].nunique() # unique GPUS, (broken still)
    df = pd.merge(mem, nprocs, on='userid')
    df = df.sort_values(by=['used_memory', 'pid'], ascending=False)
    pass
