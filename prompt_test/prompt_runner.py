import google.generativeai as genai
import argparse
import os
import json

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def load_text(file_path):
    with open(file_path, 'r') as f:
        return f.read()

def run_prompt(prompt, riddles):
    model = genai.GenerativeModel('gemini-1.5-flash')

    full_prompt = prompt.replace("{riddles}", riddles)
    response = model.generate_content(full_prompt)
    return response.text

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run prompt with riddles input")
    parser.add_argument('--prompt_file', type=str, required=True, help="Path to prompt file (.txt)")
    parser.add_argument('--riddles_file', type=str, required=True, help="Path to riddles file (.txt)")

    args = parser.parse_args()

    prompt_template = load_text(args.prompt_file)
    riddles_input = load_text(args.riddles_file)

    output = run_prompt(prompt_template, riddles_input)

    print("\nPrompt Output:\n")
    print(output)

     # Save JSON output
    with open("prompt_test/output.json", "w") as json_file:
        json.dump(output, json_file, indent=2)
    print("\nJSON output saved to 'prompt_test/output.json'")
