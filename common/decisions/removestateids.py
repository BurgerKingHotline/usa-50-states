from pathlib import Path

def remove_number_blocks(text: str) -> str:
    lines = text.splitlines(keepends=True)
    output = []

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Detect lines like: 13 = {
        # Also allows: 13 = { thing }
        if starts_number_block(stripped):
            brace_depth = 0

            while i < len(lines):
                current_line = lines[i]

                brace_depth += current_line.count("{")
                brace_depth -= current_line.count("}")

                i += 1

                if brace_depth <= 0:
                    break

            # Skip the whole block by not appending it
            continue

        output.append(line)
        i += 1

    return "".join(output)


def starts_number_block(line: str) -> bool:
    """
    Returns True for lines starting with patterns like:
    13 = {
    149 = { thing }
    """
    left, sep, right = line.partition("=")

    if not sep:
        return False

    return left.strip().isdigit() and right.lstrip().startswith("{")


script_folder = Path(__file__).parent
output_folder = script_folder / "fixed_txt"

output_folder.mkdir(exist_ok=True)

for input_file in script_folder.glob("*.txt"):
    output_file = output_folder / input_file.name

    text = input_file.read_text(encoding="utf-8")
    cleaned = remove_number_blocks(text)

    output_file.write_text(cleaned, encoding="utf-8")

    print(f"Fixed: {input_file.name} -> {output_file}")