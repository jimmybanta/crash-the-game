import requests

API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3.1-405B"
headers = {"Authorization": "Bearer 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"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()
	
output = query({
	"inputs": "Tell me about quantum physics ",
})

print(output)
