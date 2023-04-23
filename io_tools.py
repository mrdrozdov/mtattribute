import json


def read_agent_file(filename):
    agents = []
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
    return agents
