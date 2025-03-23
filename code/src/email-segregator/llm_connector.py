import google.generativeai as genai

# Configure with your Google AI Studio API Key
genai.configure(api_key="")

# Load the model
model = genai.GenerativeModel("gemini-2.0-flash")

# Function to translate text
def translate_to_spanish(text):
    prompt = f"Translate the following English text to Spanish. Provide only the best and most natural translation:\n\n'{text}'"
    response = model.generate_content(prompt)
    # Ensure we get a valid response
    if response and response.text:
        return response.text.strip().split("\n")[0]  # Pick the first translation

    return "Translation failed."

# Example usage
english_text = "Hello, how are you?"
spanish_translation = translate_to_spanish(english_text)

print(f"English: {english_text}")
print(f"Spanish: {spanish_translation}")

