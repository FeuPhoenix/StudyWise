import openai
import time

def generate_concise_title(headline, OPENAI_API_KEY):
    while True:
        try:
                    openai.api_key = OPENAI_API_KEY
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": f"Convert this headline into a concise title: \"{headline}\""}
                        ]
                    )

                    return response['choices'][0]['message']['content'].strip()

        except openai.error.RateLimitError as e:
            print("Rate limit exceeded, waiting to retry...")
            time.sleep(20)
            
print(generate_concise_title( "What if your income doubles but the income of everyone else triples","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"))