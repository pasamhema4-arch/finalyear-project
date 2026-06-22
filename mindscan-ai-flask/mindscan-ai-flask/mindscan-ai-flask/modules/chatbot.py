from openai import OpenAI

# Create client
client = OpenAI(api_key="YOUR_API_KEY")

def ai_response(user_message):

    prompt = f"You are a friendly AI psychologist. Respond supportively to: {user_message}"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content