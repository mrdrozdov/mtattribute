import argparse
import datetime
import json
import os
import requests
import time

import asyncio
import openai
import pytz
from tqdm import tqdm

from io_tools import read_agent_file


USE_AZURE = False

if USE_AZURE:
    openai.api_key = None
    openai.api_base =  "https://umassnlp.openai.azure.com/"
    openai.api_type = 'azure'
    openai.api_version = "2023-03-15-preview"
    deployment_name = 'gpt-35-turbo' #This will correspond to the custom name you chose for your deployment when you deployed a model.
    base_kwargs = dict(engine=deployment_name)
else:
    with open('openai-key.txt') as f:
        openai.api_key = f.read().strip()
    deployment_name = 'gpt-3.5-turbo'
    base_kwargs = dict(model=deployment_name)


async def dispatch_openai_requests(messages_list, temperature, top_p, max_tokens):
    """Dispatches requests to OpenAI API asynchronously.

    Args:
        messages_list: List of messages to be sent to OpenAI ChatCompletion API.
        temperature: Temperature to use for the model.
        top_p: Top p to use for the model.
        max_tokens: Maximum number of tokens to generate.
    Returns:
        List of responses from OpenAI API.
    """
    async_responses = []

    for x in messages_list:
        kwargs = base_kwargs.copy()
        kwargs.update(dict(
                messages=x,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
            ))
        async_responses.append(openai.ChatCompletion.acreate(**kwargs))

    return await asyncio.gather(*async_responses)


def api_call(prompt, model_name='ChatGPT'):
    current_date = datetime.datetime.now(pytz.timezone('America/New_York')).strftime('%B %d, %Y')
    kwargs = base_kwargs.copy()
    kwargs.update(dict(temperature=args.temp,  # you might want to change this for your task
        max_tokens=2048,   # you might want to change this for your task
        messages=[
            {"role": "system", "content": f"You are {model_name}, a large language model trained by OpenAI. Answer as concisely as possible. Knowledge cutoff: 2021-09. Current date: {current_date}."},
            {"role": "user", "content": prompt},
        ]))
    response = openai.ChatCompletion.create(**kwargs)
    return response


def main(args):
    if args.seed_file is None:
        expdir = f'outputs/cache.n_{args.n}.k_{args.k}.temp_{str(args.temp).replace(".", "_")}'
        os.system(f'mkdir -p {args.expdir}')
        with open(expdir + '/flags.json', 'w') as f:
            f.write(json.dumps(args.__dict__))

        out_file = f'{expdir}/agents.jsonl'
        run(args, out_file)

    else:
        assert args.exp_dir is not None
        expdir = args.exp_dir
        os.system(f'mkdir -p {expdir}')
        with open(expdir + '/flags.json', 'w') as f:
            f.write(json.dumps(args.__dict__))

        agents = read_agent_file(args.seed_file)

        for i, a in enumerate(agents):
            out_file = f'{expdir}/agents.{i}.jsonl'
            print(i, a)
            run(args, out_file, agent=a)


def run(args, out_file, agent=None):
    prompt = 'Give me ' + str(args.k) + ' interesting personas. Please give each of them a first and last name. Use JSON format: {"id": ID, "name": NAME, "job": JOB, "description": DESCRIPTION}. Other instructions: a) The ID should be 0-indexed representing the order in which they are generated. b) Do not return any unnecessary text, only the personas as JSON. Each JSON should be on a single separate line. c) Do not respond by saying "Sure" or anything similar. d) Each line should begin with a "{" and not a number.'
    if agent is not None:
        prompt = f"""
You are {agent["name"]}.
Job: {agent["job"]}
Description: {agent["description"]}

Complete the following task:

{prompt}
""".strip()

    number_of_calls = args.n // (args.k * args.batch_size)
    assert args.n == args.k * args.batch_size * number_of_calls
    # response = api_call(prompt)

    batches = []
    for _ in range(number_of_calls):
        model_name = 'ChatGPT'
        current_date = datetime.datetime.now(pytz.timezone('America/New_York')).strftime('%B %d, %Y')
        messages = [
            {"role": "system", "content": f"You are {model_name}, a large language model trained by OpenAI. Answer as concisely as possible. Knowledge cutoff: 2021-09. Current date: {current_date}."},
            {"role": "user", "content": prompt},
        ]
        batch = [messages] * args.batch_size
        batches.append(batch)

    cache = []

    for i, batch in enumerate(batches):
        print(i)
        temperature = args.temp
        max_tokens = 2048
        num_retries = 5
        top_p = 0.95 if args.temp == 0 else 1.0
        for _ in range(num_retries):
            try:
                responses = asyncio.run(dispatch_openai_requests(batch, temperature, top_p, max_tokens))
            except openai.error.RateLimitError:
                time.sleep(10)
                continue
            except openai.error.APIError:
                print('openai.error.APIError')
                time.sleep(10)
                continue
            break
        # print(responses)
        for messages, response in zip(batch, responses):
            content = response['choices'][0]['message']['content']
            print(content)
            cache.append(dict(messages=messages, content=content))

    print(f'writing {out_file}')
    with open(out_file, 'w') as f:
        for x in cache:
            f.write(f'{json.dumps(x)}\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--exp-dir', default=None, type=str)
    parser.add_argument('--seed-file', default=None, type=str,
        help="Personas to generate from. NOTE: We run this separately for each persona in the list.")
    parser.add_argument('--temp', default=0.0, type=float, help="Temperature.")
    parser.add_argument('--k', default=5, type=int, help="Number of personas per request.")
    parser.add_argument('--n', default=100, type=int, help="Total amount of personas.")
    parser.add_argument('--batch-size', default=10, type=int, help="Number of prompts in parallel.")
    args = parser.parse_args()
    print(json.dumps(args.__dict__))
    main(args)
