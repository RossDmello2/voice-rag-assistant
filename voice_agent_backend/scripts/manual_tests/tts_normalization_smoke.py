import re
import unicodedata

def normalize(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "...",
        "\u00a0": " ",
    }
    for src, dest in replacements.items():
        text = text.replace(src, dest)
    
    # 1. Numeric ranges: "5-7" -> "5 to 7"
    text = re.sub(r'(\d+)\s*-\s*(\d+)', r'\g<1> to \g<2>', text)
    
    # 2. Currency: "$25.50" -> "25.50 dollars"
    text = re.sub(r'\$(\d+(?:\.\d+)?)', r'\g<1> dollars', text)
    
    # 3. Percent: "10%" -> "10 percent"
    text = re.sub(r'(\d+(?:\.\d+)?)%', r'\g<1> percent', text)
    
    # 4. Ampersands: "A & B" -> "A and B"
    text = re.sub(r'\s+&\s+', ' and ', text)
    text = re.sub(r'\b&\b', ' and ', text)
    
    # 5. Common Shorthand (Order matters: check longer ones first)
    text = re.sub(r'\bw/o\b', 'without', text, flags=re.IGNORECASE)
    text = re.sub(r'\bw/(?=\s|$)', 'with', text, flags=re.IGNORECASE)
    text = re.sub(r'\bb/c\b', 'because', text, flags=re.IGNORECASE)
    
    # 6. Units (Common)
    text = re.sub(r'\b(\d+)\s*km\b', r'\g<1> kilometers', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(\d+)\s*kg\b', r'\g<1> kilograms', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(\d+)\s*mph\b', r'\g<1> miles per hour', text, flags=re.IGNORECASE)
    
    # 7. Math/Special: "5+" -> "5 plus"
    text = re.sub(r'(\d+)\s*\+', r'\g<1> plus', text)

    text = re.sub(r"\s+", " ", text).strip()
    return text

test_cases = [
    ("It takes 5-7 business days.", "It takes 5 to 7 business days."),
    ("The cost is $25.50 w/ tax & insurance.", "The cost is 25.50 dollars with tax and insurance."),
    ("We have a 15-20% increase.", "We have a 15 to 20 percent increase."),
    ("Drive at 60 mph for 10 km.", "Drive at 60 miles per hour for 10 kilometers."),
    ("It happened b/c of the rain.", "It happened because of the rain."),
    ("Experience: 5+ years.", "Experience: 5 plus years."),
    ("Wait w/o worrying.", "Wait without worrying."),
]

print("--- TTS Normalization Test ---")
for original, expected in test_cases:
    result = normalize(original)
    status = "PASS" if result == expected else "FAIL"
    print(f"[{status}]")
    print(f"  In:  {original}")
    print(f"  Out: {result}")
    if status == "FAIL":
        print(f"  Exp: {expected}")
