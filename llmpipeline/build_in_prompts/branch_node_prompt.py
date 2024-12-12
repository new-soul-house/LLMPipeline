prompt="""Task: Please select the closest item from the items based on the input content and only answer the item id in JSON format: ```json\n{"item_id": "#i"}\n```.
Input: {input}
Items:
{items}

Let's think step by step.
Answer:
"""
keys=['{input}', '{items}']