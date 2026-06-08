def validate_latex(content):

    errors = []

    if content.count("{") != content.count("}"):
        errors.append("Unbalanced braces detected.")

    if content.count("\\begin{") != content.count("\\end{"):
        errors.append("Environment mismatch detected.")

    return errors