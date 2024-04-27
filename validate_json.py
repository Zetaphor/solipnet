import json

with open('search_results.json', 'r') as file:
  data = json.load(file)
  # Determine if the data is a dict or list
  if isinstance(data, dict):
    print("Data is a dictionary")
  elif isinstance(data, list):
    print("Data is a list")
    print(data[0])

