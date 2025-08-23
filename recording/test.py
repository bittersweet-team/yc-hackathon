from browser_use_sdk import BrowserUse
import json

client = BrowserUse(
    api_key="bu_XmyzlCRF_9_vTAkPrI1pUQzqWDtzPjT7vzTLRYonz4U",
)
tasks = client.tasks.list()
for task in tasks.items:
    print(json.dumps(task.to_dict(), indent=4))

task = client.tasks.retrieve(task_id="b0b9f385-a163-47e9-8cf6-7a646e2b3469")

print(json.dumps(task.to_dict(), indent=4))
