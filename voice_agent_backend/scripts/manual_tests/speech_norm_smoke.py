import os
import sys
from pathlib import Path

# Add backend to path.
BACKEND_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(BACKEND_ROOT))

from app.services.speech_service import speech_service

def test_normalization():
    test_cases = [
        ("$1,500.50", "one thousand, five hundred dollars, fifty cents"),
        ("Contact us at support@elegancedress.com", "Contact us at support at elegancedress dot com"),
        ("Located on the 22nd floor", "Located on the twenty-second floor"),
        ("Visit us in SoHo", "Visit us in So-Ho"),
        ("Our shop in Le Marais", "Our shop in Luh Ma-ray"),
        ("Gift cards up to $1,000", "Gift cards up to one thousand dollars, zero cents"),
        ("Range is from 50 to 1000", "Range is from fifty to one thousand"),
    ]
    
    print("\n--- Speech Normalization Test ---")
    all_passed = True
    for input_text, expected in test_cases:
        actual = speech_service._normalize_tts_text(input_text)
        status = "PASS" if actual == expected else "FAIL"
        print(f"[{status}]")
        print(f"  Input:    {input_text}")
        print(f"  Expected: {expected}")
        print(f"  Actual:   {actual}")
        if actual != expected:
            all_passed = False
    
    print("-" * 34)
    if all_passed:
        print("ALL NORMALIZATION TESTS PASSED!")
    else:
        print("SOME TESTS FAILED. CHECK REGEX.")

if __name__ == "__main__":
    test_normalization()
