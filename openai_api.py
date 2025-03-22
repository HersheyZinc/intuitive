from dotenv import load_dotenv
from openai import OpenAI
load_dotenv(override=True)
CLIENT = OpenAI()

def openai_query(messages, model="gpt-4o-mini", temperature=0, max_tokens=4096):

    response = CLIENT.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    reply = response.choices[0].message.content

    return reply


def rag_query(messages, documents=[]):
    system_prompt = "You are an expert in change management. Answer the query in a concise manner."

    reply = openai_query([system_prompt] + messages)

    return reply