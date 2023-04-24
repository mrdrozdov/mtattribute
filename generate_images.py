import json
import replicate

with open('outputs/seed-agents.jsonl', 'r') as json_file:
  json_list = list(json_file)

outputs = []
for json_str in json_list:
    result = json.loads(json_str)
    print(f"result: {result}")
    name = result["name"]
    description = result["description"]
    url = replicate.run(
      "stability-ai/stable-diffusion:27b93a2413e7f36cd83da926f3656280b2931564ff050bf9575f1fdf9bcd7478",
      input={"prompt": f"A personal website photo for {name}. {description}"}
    )
    print(url)
    result['photo'] = url[0]
    outputs.append(result)

with open("outputs/sedd-agents-image-urls.jsonl", "w") as outfile:
    outfile.write(json.dumps(outputs))
outfile.close()

# raw_urls = open('outputs/urls.txt', 'r')
#
# outputs = []
# for row in raw_urls:
#     if 'result: {' in row:
        # try:
        #     row = row[8:-1].replace('\'id\'', '\"id\"')
        #     row = row.replace('\'name\'', '\"name\"')
        #     row = row.replace('\'job\'', '\"job\"')
        #     row = row.replace('\'description\'', '\"description\"')
        #     import ipdb;
        #
        #     ipdb.set_trace()
        #     dict = json.loads(row)
        # except:
        #     import ipdb;
        #
        #     ipdb.set_trace()
#         pass
#     else:
#         outputs.append(row.strip('[').replace(']', ''))
#
# with open ('outputs/urls_clean.txt', 'w') as fo:
#    for d in outputs:
#         fo.write(str(d))
# fo.close()
