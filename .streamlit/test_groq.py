import tomllib
from groq import Groq

with open(".streamlit/secrets.toml", "rb") as f:
    secrets = tomllib.load(f)

client = Groq(api_key=secrets["GROQ_API_KEY"])

try:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": "Say hello in Hindi"}
        ],
        max_tokens=100
    )

    print("GROQ CONNECTED!")
    print(response.choices[0].message.content)

except Exception as e:
    print("ERROR:", type(e).__name__, str(e))