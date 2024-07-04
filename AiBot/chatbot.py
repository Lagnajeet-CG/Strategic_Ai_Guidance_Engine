import google.generativeai as genai

key = "AIzaSyB2Ap-o973pkpyvPaKiktbZwd4LX1FxU2c"
genai.configure(api_key=key)

# query generation
def qgen(prompt):
    model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
)
    response=model.generate_content(prompt)
    return response.text

user=input("type here")
output=qgen(user)
print(output)