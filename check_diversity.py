import json


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
                agents = []
                filename = f'outputs/cache.n_{n}.k_{k}.temp_{temp}.jsonl'
                with open(filename) as f:
                    for line in f:
                        obj = json.loads(line)
                        content = obj['content']
                        # Sanitize the content.
                        content = content.replace('}\n', '@@@')
                        content = content.replace('\n', ' ')
                        content = content.replace('@@@', '}\n')
                        # Parse into agents.
                        for a in content.split('\n'):
                            if not a.strip():
                                continue
                            agents.append(json.loads(a))
                data[filename] = agents

    for k, agents in data.items():
        print(k)
        evaluate(agents)



if __name__ == '__main__':
    import argparse

    main()
