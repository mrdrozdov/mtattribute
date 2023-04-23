import collections
import json
import os

from io_tools import read_agent_file


def evaluate(agents):
    n = len(agents)
    names = [x['name'] for x in agents]
    jobs = [x['job'] for x in agents]
    name_jobs = [x['name'] + ' ' + x['job'] for x in agents]
    unames = set(names)
    ujobs = set(jobs)
    uname_jobs = set(name_jobs)

    print(f"""
n = {n}
names = {len(unames)}
jobs = {len(ujobs)}, {collections.Counter(jobs)}
name_jobs = {len(uname_jobs)}
        """.strip())

    stats = {}
    stats['n'] = len(unames)
    stats['names'] = len(unames)
    stats['jobs'] = len(ujobs)
    stats['name_jobs'] = len(uname_jobs)

    return stats


def main():
    # Read
    seed_file = f'outputs/cache.n_100.k_10.temp_0_3/agents.jsonl'
    seed_agents = read_agent_file(seed_file)
    print(f'SEED = {seed_file}')
    evaluate(seed_agents)

    results = {}
    expdir = 'outputs/seeded-v1'
    for filename in sorted(os.listdir(expdir)):
        if not filename.endswith('jsonl'):
            continue
        print('-' * 80)
        ix = int(filename.split('.')[-2])
        a = seed_agents[ix]
        filename = f'{expdir}/{filename}'
        agents = read_agent_file(filename)
        print(f'{filename}')
        results[filename] = (evaluate(agents), a)

    print('--- BY JOBS ---')

    for k, v in sorted(results.items(), key=lambda x: -x[1][0]['jobs']):
        v, a = v
        print(v, k, a['name'], a['job'])

    print('--- BY NAME ---')

    for k, v in sorted(results.items(), key=lambda x: -x[1][0]['names']):
        v, a = v
        print(v, k, a['name'], a['job'])


if __name__ == '__main__':
    import argparse

    main()
