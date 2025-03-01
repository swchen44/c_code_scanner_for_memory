import csv
import os
import re
import argparse
import google.generativeai as genai
import openai
import json

class AIModel:
    def __init__(self):
        pass

    def generate_content(self, prompt, code_line):
        raise NotImplementedError("Subclasses must implement generate_content method")


class GeminiAIModel(AIModel):
    def __init__(self):
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            print("Error: GOOGLE_API_KEY environment variable not set.")
            exit()
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def generate_content(self, prompt, code_line):
        try:
            response = self.model.generate_content(prompt + "\\n" + code_line)
            return response.text
        except Exception as e:
            print(f"Error: An error occurred during the API call: {e}")
            return None


class OpenAIModel(AIModel):
    def __init__(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("Error: OPENAI_API_KEY environment variable not set.")
            exit()
        self.api_key = api_key
        openai.api_key = self.api_key
        self.model_name = "gpt-3.5-turbo"  # You can change this to other available models

    def generate_content(self, prompt, code_line):
        try:
            response = openai.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": code_line}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error: An error occurred during the OpenAI API call: {e}")
            return None


class DeepSeekAIModel(AIModel):
    def __init__(self, api_key):
        # TODO: Implement DeepSeek initialization
        pass

    def generate_content(self, prompt, code_line):
        # TODO: Implement DeepSeek API interaction
        return None


def get_ai_response(code_line, prompt, ai_model):
    """
    Sends a request to the specified AI model and returns the response.
    """
    return ai_model.generate_content(prompt, code_line)


def write_csv(data, output_csv_file):
    """
    Writes the output data to a CSV file.
    """
    with open(output_csv_file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Line Number', 'Original Code', 'Reason'])  # Header
        csvwriter.writerows(data)


def scan_c_code(c_code_file, prompt_file, output_csv_file, ai_model):
    """
    Scans C source code for bugs and memory inefficiencies using AI's REST API,
    reads the prompt from a file, and outputs a CSV file with the line number,
    original code, and reason for the bug/inefficiency.
    """
    try:
        # Read the C code from the file
        with open(c_code_file, 'r') as f:
            c_code = f.readlines()

        # Read the prompt from the file
        with open(prompt_file, 'r') as f:
            prompt = f.read()

        # Prepare the data for CSV output
        output_data = []

        # Send the entire C code to the AI API and get the response
        reason = get_ai_response("".join(c_code), prompt, ai_model)

        if reason:
            # Append the data to the output list
            output_data.append([1, "".join(c_code).strip(), reason])

        # Write the output to a CSV file
        write_csv(output_data, output_csv_file)

        print(f"Successfully scanned {c_code_file} and generated {output_csv_file}")

    except FileNotFoundError as e:
        print(f"Error: File not found: {e}")
    except Exception as e:
        print(f"Error: An error occurred during the scanning process: {e}")


def load_custom_rules(rules_file):
    with open(rules_file, 'r') as file:
        return json.load(file)


def main():
    parser = argparse.ArgumentParser(description='Scan C code for potential bugs and memory inefficiencies.')
    parser.add_argument('--model', choices=['gemini', 'openai'], default='gemini', help='Choose the AI model to use.')
    parser.add_argument('c_code_file', help='Path to the C source code file.')
    parser.add_argument('prompt_file', help='Path to the prompt file.')
    parser.add_argument('output_csv_file', help='Path to the output CSV file.')
    parser.add_argument('--rules', help='Path to the user-defined rules file.', default=None)
    args = parser.parse_args()

    if args.rules:
        custom_rules = load_custom_rules(args.rules)
        # Use custom_rules in the scanning process
        print(f"Loaded custom rules: {custom_rules}")

    c_code_file = args.c_code_file
    prompt_file = args.prompt_file
    output_csv_file = args.output_csv_file
    ai_model_name = args.model

    if ai_model_name == "gemini":
        ai_model = GeminiAIModel()
    elif ai_model_name == "openai":
        ai_model = OpenAIModel()
    else:
        print("Error: Invalid AI model name.")
        exit()

    scan_c_code(c_code_file, prompt_file, output_csv_file, ai_model)


if __name__ == '__main__':
    main()
