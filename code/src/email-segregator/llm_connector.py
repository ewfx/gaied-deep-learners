import google.generativeai as genai

genai.configure(api_key="")
model = genai.GenerativeModel("gemini-2.0-flash")

def determine_request_type(emails):
    combined_text = "\n".join(email['bodyPreview'] for email in emails)
    prompt = ("Based on the following email texts, identify the overall request type and sub-request types: \n"
              f"\n{combined_text}\n"
              "- Request Type: \n"
              "- Sub-Request Types (comma-separated):")
    response = model.generate_content(prompt)
    if response and response.text:
        lines = response.text.strip().split("\n")
        request_type = lines[0] if len(lines) > 0 else "Unknown"
        sub_request_types = lines[1].split(",") if len(lines) > 1 else []
        return request_type, sub_request_types
    return "Unknown", []

def analyze_text(text, request_type, sub_request_types):
    prompt = ("Analyze the following email text considering the predefined request type and sub-request types: \n"
              f"Request Type: {request_type}\n"
              f"Possible Sub-Request Types: {', '.join(sub_request_types)}\n"
              "\nEmail Text:\n"
              f"{text}\n"
              "\nDetermine:\n"
              "- The pattern \n"
              "- The best matching sub-request type \n"
              "- Provide a short summary")
    response = model.generate_content(prompt)
    if response and response.text:
        lines = response.text.strip().split("\n")
        return {
            "pattern": lines[0] if len(lines) > 0 else "Unknown",
            "request_type": request_type,
            "sub_request_type": lines[1] if len(lines) > 1 else "Unknown",
            "summary": lines[2] if len(lines) > 2 else "No summary available"
        }
    return {"pattern": "Unknown", "request_type": request_type, "sub_request_type": "Unknown", "summary": "No data"}
