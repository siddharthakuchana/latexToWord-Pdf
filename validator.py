def validate_latex(content):

    errors = []

    if content.count("{") != content.count("}"):
        errors.append("Unbalanced braces detected.")

    begin_count = content.count("\\begin{")
    end_count = content.count("\\end{")

    if begin_count != end_count:
        errors.append("Environment mismatch detected.")

    return errors