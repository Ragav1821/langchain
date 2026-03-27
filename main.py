import re
from langchain_help import generate_raw_names


# 🔹 Extract names from LLM response
def extract_names(text):
    lines = text.split("\n")
    names = []

    for line in lines:
        match = re.match(r"\d+\.\s*(\w+)", line)
        if match:
            names.append(match.group(1))

    return names


# 🔹 Filter names based on strict constraints
def filter_names(names, letter, let, length):
    valid = []

    for name in names:
        if (
            name.lower().startswith(letter.lower())
            and name.lower().endswith(let.lower())
            and len(name) == length
        ):
            valid.append(name)

    return valid


# 🔹 Main function used by UI
def generate_names(human_type, letter, let, length):
    attempts = 5
    collected = []

    for _ in range(attempts):
        raw_output = generate_raw_names(human_type, letter, let, length)

        names = extract_names(raw_output)
        valid = filter_names(names, letter, let, length)

        collected.extend(valid)

        if len(collected) >= 5:
            return list(set(collected))[:5]

    # 🔴 If not enough valid names
    if len(collected) > 0:
        return list(set(collected))

    return ["❌ No valid names found with given constraints"]