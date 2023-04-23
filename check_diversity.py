import json

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
jobs = {len(ujobs)}
name_jobs = {len(uname_jobs)}
        """)


def main():
    ks = [10, 5, 1]
    ns = [100]
    temps = ['0_0', '0_3']

    data = {}
    for n in ns:
        for temp in temps:
            for k in ks:
                # Read
                filename = f'outputs/cache.n_{n}.k_{k}.temp_{temp}/agents.jsonl'
                agents = read_agent_file(filename)
                data[filename] = agents

    for k, agents in data.items():
        print(k)
        evaluate(agents)

    agents = data['outputs/cache.n_{n}.k_{k}.temp_{temp}/agents.jsonl'.format(n=100, k=10, temp='0_3')]
    for a in agents:
        print(a)



if __name__ == '__main__':
    import argparse

    main()
