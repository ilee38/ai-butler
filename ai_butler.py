import openai
import os

client = openai.OpenAI(
   api_key=os.environ.get("OPENAI_API_KEY")
)


