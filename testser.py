import openai
import os

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def test_openai_api():
  try:
    # Example API call to test
    response = openai.Completion.create(
      engine="text-davinci-003",
      prompt="Say hello!",
      max_tokens=5
    )
    print("API Response:", response.choices[0].text.strip())
  except Exception as e:
    print("Error testing OpenAI API:", e)

if __name__ == "__main__":
  test_openai_api()