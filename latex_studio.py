"""
LaTeX Equation Studio & BibTeX Assistant for OmniDoc Studio Pro.
Provides:
- Live LaTeX formula rendering to crisp PNG images with transparent backgrounds
- Pre-built formula library for Calculus, Physics, Linear Algebra, and Statistics
- BibTeX citation validator and syntax beautifier
"""

import io
import re
from typing import Dict, List, Any, Optional, Tuple
from PIL import Image

try:
    import matplotlib
    matplotlib.use("Agg")  # Non-interactive backend
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


# Pre-built curated catalog of LaTeX formulas
FORMULA_CATALOG: Dict[str, Dict[str, str]] = {
    "Calculus & Analysis": {
        "Gaussian Integral": r"\int_{-\infty}^{\infty} e^{-x^2} \, dx = \sqrt{\pi}",
        "Euler's Identity": r"e^{i\pi} + 1 = 0",
        "Taylor Series": r"f(x) = \sum_{n=0}^{\infty} \frac{f^{(n)}(a)}{n!} (x - a)^n",
        "Fundamental Theorem of Calculus": r"\frac{d}{dx} \left( \int_{a}^{x} f(t) \, dt \right) = f(x)",
        "Cauchy-Schwarz Inequality": r"\left| \langle u, v \rangle \right|^2 \leq \langle u, u \rangle \cdot \langle v, v \rangle"
    },
    "Linear Algebra": {
        "Matrix Determinant (2x2)": r"\det \begin{pmatrix} a & b \\ c & d \end{pmatrix} = ad - bc",
        "Eigenvalue Equation": r"A \mathbf{v} = \lambda \mathbf{v}",
        "Rotation Matrix": r"R(\theta) = \begin{bmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{bmatrix}",
        "Singular Value Decomposition": r"A = U \Sigma V^T"
    },
    "Physics & Quantum Mechanics": {
        "Schrödinger Equation (Time-Dependent)": r"i\hbar \frac{\partial}{\partial t} \Psi(\mathbf{r}, t) = \hat{H} \Psi(\mathbf{r}, t)",
        "Einstein Mass-Energy-Momentum": r"E^2 = (pc)^2 + (m_0 c^2)^2",
        "Maxwell's Gauss Law": r"\nabla \cdot \mathbf{E} = \frac{\rho}{\varepsilon_0}",
        "Heisenberg Uncertainty": r"\Delta x \Delta p \geq \frac{\hbar}{2}"
    },
    "Probability & Statistics": {
        "Gaussian / Normal PDF": r"f(x) = \frac{1}{\sigma \sqrt{2\pi}} \exp\left( -\frac{(x - \mu)^2}{2\sigma^2} \right)",
        "Bayes' Theorem": r"P(A \mid B) = \frac{P(B \mid A) P(A)}{P(B)}",
        "Binomial Coefficient": r"\binom{n}{k} = \frac{n!}{k!(n - k)!}"
    }
}


def render_latex_equation_image(
    latex_code: str,
    fontsize: int = 24,
    dpi: int = 300,
    text_color: str = "#ffffff",
    transparent: bool = True
) -> bytes:
    """
    Renders LaTeX mathematical code into a crisp PNG image using Matplotlib's mathtext engine.
    """
    if not MATPLOTLIB_AVAILABLE:
        raise RuntimeError("matplotlib is required to render equation images.")

    raw_tex = latex_code.strip()
    # Strip wrapping dollar signs or equation tags if user included them
    if raw_tex.startswith("$$") and raw_tex.endswith("$$"):
        raw_tex = raw_tex[2:-2].strip()
    elif raw_tex.startswith("$") and raw_tex.endswith("$"):
        raw_tex = raw_tex[1:-1].strip()

    # Wrap in mathtext display delimiter
    math_expr = f"${raw_tex}$"

    fig = plt.figure(figsize=(0.01, 0.01))
    fig.patch.set_alpha(0.0 if transparent else 1.0)
    if not transparent:
        fig.patch.set_facecolor("#0f172a")

    try:
        text_obj = fig.text(
            0.5, 0.5,
            math_expr,
            fontsize=fontsize,
            color=text_color,
            ha="center",
            va="center"
        )

        out_buffer = io.BytesIO()
        fig.savefig(
            out_buffer,
            format="png",
            dpi=dpi,
            bbox_inches="tight",
            pad_inches=0.15,
            transparent=transparent,
            facecolor=fig.get_facecolor(),
            edgecolor="none"
        )
        plt.close(fig)
        return out_buffer.getvalue()
    except Exception as e:
        plt.close(fig)
        raise RuntimeError(f"LaTeX rendering error: {e}")


def validate_bibtex_entry(bibtex_str: str) -> Dict[str, Any]:
    """
    Validates and formats a BibTeX entry.
    Checks syntax, entry type, citation key, and common required fields.
    """
    clean_str = bibtex_str.strip()
    if not clean_str:
        return {"valid": False, "error": "BibTeX content is empty.", "fields": {}, "entry_type": "", "key": ""}

    # Pattern for @entry_type{citation_key,
    entry_match = re.match(r"^@([a-zA-Z]+)\s*\{\s*([^,]+),", clean_str)
    if not entry_match:
        return {
            "valid": False,
            "error": "Invalid BibTeX format. Expected '@type{key, field = {value}, ...}'",
            "fields": {},
            "entry_type": "",
            "key": ""
        }

    entry_type = entry_match.group(1).lower()
    citation_key = entry_match.group(2).strip()

    # Check balanced braces
    if clean_str.count("{") != clean_str.count("}"):
        return {
            "valid": False,
            "error": "Unbalanced curly braces '{' and '}' in BibTeX entry.",
            "fields": {},
            "entry_type": entry_type,
            "key": citation_key
        }

    # Extract fields: field_name = {value} or field_name = "value" or field_name = 123
    field_pattern = re.compile(r"([a-zA-Z_]+)\s*=\s*[{|\"]?(.*?)[}|\"]?(?:,|$)", re.DOTALL)
    body = clean_str[entry_match.end():-1] if clean_str.endswith("}") else clean_str[entry_match.end():]

    fields = {}
    for match in field_pattern.finditer(body):
        fname = match.group(1).lower().strip()
        fval = match.group(2).strip().rstrip(",")
        if fname and fval:
            fields[fname] = fval

    # Check common required fields
    required_fields_map = {
        "article": ["author", "title", "journal", "year"],
        "book": ["author", "title", "publisher", "year"],
        "inproceedings": ["author", "title", "booktitle", "year"],
        "misc": ["title"]
    }

    missing_fields = []
    if entry_type in required_fields_map:
        for req in required_fields_map[entry_type]:
            if req not in fields:
                missing_fields.append(req)

    # Format cleanly
    formatted_lines = [f"@{entry_type}{{{citation_key},"]
    for f_k, f_v in sorted(fields.items()):
        formatted_lines.append(f"  {f_k:<12} = {{{f_v}}},")
    formatted_lines.append("}")
    beautified = "\n".join(formatted_lines)

    return {
        "valid": True,
        "entry_type": entry_type,
        "key": citation_key,
        "fields": fields,
        "missing_recommended": missing_fields,
        "beautified": beautified,
        "error": None
    }
