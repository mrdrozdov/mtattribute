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
    prompt = 'Give me ' + str(args.k) + ' interesting personas. Please give each of them a first and last name. Use JSON format: {"id": ID, "name": NAME, "job": JOB, "description": DESCRIPTION}. Other instructions: a) The ID should be 0-indexed representing the order in which they are generated. b) Do not return any unnecessary text, only the personas as JSON. c) Do not respond by saying "Sure" or anything similar. d) Each line should begin with a "{" and not a number.'
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
        top_p = 1.0 if args.temp == 0 else 0.95
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

    filename = f'outputs/cache.n_{args.n}.k_{args.k}.temp_{str(args.temp).replace(".", "_")}.jsonl'

    print(f'writing {filename}')
    with open(filename, 'w') as f:
        for x in cache:
            f.write(f'{json.dumps(x)}\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--temp', default=0.0, type=float, help="Temperature.")
    parser.add_argument('--k', default=5, type=int, help="Number of personas per request.")
    parser.add_argument('--n', default=100, type=int, help="Total amount of personas.")
    parser.add_argument('--batch-size', default=10, type=int, help="Number of prompts in parallel.")
    args = parser.parse_args()
    print(json.dumps(args.__dict__))
    main(args)
