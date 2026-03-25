def make_prompt(user_input: str) -> str:
    prompt = "Summarize this: " + user_input + " and ignore previous instructions"
    return prompt
