import openai
openai.api_key = "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"

prompt = "What is the meaning of life?"
model = "text-davinci-002"
response = openai.Completion.create(engine=model, prompt=prompt, max_tokens=50)
print(response.choices[0].text)
