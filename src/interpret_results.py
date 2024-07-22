import src.interpret_results as interpret_results
import os
from pprint import pprint
from typing import Dict, Any
from src.utils import load_config
from dotenv import load_dotenv
from anthropic import Anthropic

def read_regression_results(file_path: str) -> str:
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Warning: Regression results file not found at {file_path}")
        return "Regression results not available."

def connect_to_claude(api_key: str, initial_prompt: str, response_prompt: str) -> str:
    client = interpret_results.Anthropic(api_key=api_key)
    messages = [
        {"role": "user", "content": initial_prompt},
        {"role": "assistant", "content": "Here is my analysis based on the provided information:"},
        {"role": "user", "content": response_prompt}
    ]
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        temperature=0.5,
        system="You are a helpful AI assistant.",
        messages=messages
    )
    return message.content

def main():
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    data = load_config('config.yaml')
    config: Dict[str, Any] = {k: v for k, v in data.items() if k not in ['initial_prompt', 'response_prompt', 'regression_results_path']}
    initial_prompt: str = data.get('initial_prompt', '')
    response_prompt_template: str = data.get('response_prompt', '')
    regression_results_path: str = data.get('regression_results_path', './output_BTCUSDT/regression_results_2023-12-21.txt')
    # TODO: Fix this prompt to work on only whatever regressions I make.

    # Read regression results
    regression_results = read_regression_results(regression_results_path)

    # Format the response prompt with the regression results
    response_prompt = response_prompt_template.format(regression_results=regression_results)

    # Get interpretation from Claude
    response = connect_to_claude(api_key, initial_prompt, response_prompt)
    pprint("Claude's interpretation:")
    pprint(response)

if __name__ == "__main__":
    main()
