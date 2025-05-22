import groq_client

class GroqClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def ask(self, content_context, question):
        data = {
            "model": "mixtral-8x7b-32768",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that answers questions only based on the given context."},
                {"role": "user", "content": f"Context:\n{content_context}\n\nQuestion:\n{question}"}
            ],
            "temperature": 0.7,
            "stream": False
        }

        response = requests.post(self.api_url, headers=self.headers, json=data)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.text}"
