#!/usr/bin/env python3
"""
Verify that all features from start.md are implemented correctly.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from justext import extract_text, get_available_languages, load_stoplist


def test_feature1():
    """Test basic text extraction."""
    print("Testing Feature 1: Basic Text Extraction")
    
    test_cases = [
        ("<p>Hello world</p>", "Hello world"),
        ("<div><p>First paragraph</p><p>Second paragraph</p></div>", 
         "First paragraph\nSecond paragraph"),
        ("<h1>Title</h1><p>Content</p>", "Title\nContent"),
    ]
    
    all_pass = True
    for html, expected in test_cases:
        paragraphs = extract_text(html, min_paragraph_length=5)
        content = [p.text for p in paragraphs if not p.is_boilerplate]
        actual = "\n".join(content)
        
        if actual == expected:
            print(f"  ✓ {html[:30]}...")
        else:
            print(f"  ✗ {html[:30]}...")
            print(f"    Expected: {expected}")
            print(f"    Actual: {actual}")
            all_pass = False
    
    return all_pass


def test_feature2():
    """Test boilerplate detection."""
    print("\nTesting Feature 2: Boilerplate Detection")
    
    # Test case 1: High link density should be filtered
    html1 = '<div><a href="#">Link1</a><a href="#">Link2</a><a href="#">Link3</a>Short text</div>'
    paragraphs1 = extract_text(html1)
    content1 = [p.text for p in paragraphs1 if not p.is_boilerplate]
    
    # Test case 2: Long paragraph with stopwords should be kept
    html2 = '<p>This is a long paragraph with many common words like the, and, is, which are typical stopwords in English. It contains useful information.</p>'
    paragraphs2 = extract_text(html2)
    content2 = [p.text for p in paragraphs2 if not p.is_boilerplate]
    
    # Test case 3: Very short paragraph should be filtered
    html3 = '<p>Short.</p>'
    paragraphs3 = extract_text(html3)
    content3 = [p.text for p in paragraphs3 if not p.is_boilerplate]
    
    tests = [
        (html1, len(content1) == 0, "High link density filtered"),
        (html2, len(content2) == 1, "Long paragraph with stopwords kept"),
        (html3, len(content3) == 0, "Short paragraph filtered"),
    ]
    
    all_pass = True
    for html, passed, description in tests:
        if passed:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description}")
            all_pass = False
    
    return all_pass


def test_feature3():
    """Test encoding handling."""
    print("\nTesting Feature 3: Encoding Handling")
    
    # Test with UTF-8 encoded bytes
    html_bytes = '<p>Hello 世界</p>'.encode('utf-8')
    paragraphs = extract_text(html_bytes, min_paragraph_length=1)
    content = [p.text for p in paragraphs if not p.is_boilerplate]
    
    if content and content[0] == 'Hello 世界':
        print("  ✓ UTF-8 encoding handled correctly")
        return True
    else:
        print(f"  ✗ UTF-8 encoding failed. Got: {content}")
        return False


def test_feature4():
    """Test multilingual support."""
    print("\nTesting Feature 4: Multilingual Support")
    
    languages = get_available_languages()
    
    # Check that we have at least English, German, French
    required_langs = ['english', 'german', 'french']
    missing = [lang for lang in required_langs if lang not in languages]
    
    if not missing:
        print("  ✓ Required languages available")
        
        # Try to load stopwords for each language
        for lang in required_langs:
            try:
                stopwords = load_stoplist(lang)
                if len(stopwords) > 0:
                    print(f"  ✓ {lang.capitalize()} stopwords loaded ({len(stopwords)} words)")
                else:
                    print(f"  ✗ {lang.capitalize()} stopwords empty")
                    return False
            except Exception as e:
                print(f"  ✗ Failed to load {lang} stopwords: {e}")
                return False
        
        return True
    else:
        print(f"  ✗ Missing languages: {missing}")
        return False


def test_feature5():
    """Test HTML preprocessing."""
    print("\nTesting Feature 5: HTML Preprocessing")
    
    # Test script removal
    html1 = '<body><script>alert("test")</script><p>Real content</p></body>'
    paragraphs1 = extract_text(html1, min_paragraph_length=1)
    content1 = [p.text for p in paragraphs1 if not p.is_boilerplate]
    
    # Test style removal
    html2 = '<body><style>.class { color: red; }</style><p>Text</p></body>'
    paragraphs2 = extract_text(html2, min_paragraph_length=1)
    content2 = [p.text for p in paragraphs2 if not p.is_boilerplate]
    
    # Test comment removal
    html3 = '<body><!-- Comment --><p>Content</p></body>'
    paragraphs3 = extract_text(html3, min_paragraph_length=1)
    content3 = [p.text for p in paragraphs3 if not p.is_boilerplate]
    
    tests = [
        (html1, len(content1) == 1 and content1[0] == 'Real content', "Script tags removed"),
        (html2, len(content2) == 1 and content2[0] == 'Text', "Style tags removed"),
        (html3, len(content3) == 1 and content3[0] == 'Content', "Comments removed"),
    ]
    
    all_pass = True
    for html, passed, description in tests:
        if passed:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description}")
            all_pass = False
    
    return all_pass


def test_feature6():
    """Test context-based classification."""
    print("\nTesting Feature 6: Context-Based Classification")
    
    html = '<div><p>Long good paragraph with many words and sufficient length.</p><p>Short.</p><p>Another long good paragraph with adequate length.</p></div>'
    paragraphs = extract_text(html, min_paragraph_length=20)
    content = [p.text for p in paragraphs if not p.is_boilerplate]
    
    # The short paragraph between two long ones should be kept
    expected = [
        'Long good paragraph with many words and sufficient length.',
        'Short.',
        'Another long good paragraph with adequate length.'
    ]
    
    if content == expected:
        print("  ✓ Short paragraph between content paragraphs preserved")
        return True
    else:
        print("  ✗ Context classification failed")
        print(f"    Expected: {expected}")
        print(f"    Actual: {content}")
        return False


def test_feature7():
    """Test link density calculation."""
    print("\nTesting Feature 7: Link Density Calculation")
    
    # Test high link density (should be filtered)
    html1 = '<p><a href="#">Link1</a><a href="#">Link2</a><a href="#">Link3</a>text</p>'
    paragraphs1 = extract_text(html1, max_link_density=0.5)
    content1 = [p.text for p in paragraphs1 if not p.is_boilerplate]
    
    # Test low link density (should be kept)
    html2 = '<p>This is a long paragraph with only one <a href="#">link</a> and plenty of regular text.</p>'
    paragraphs2 = extract_text(html2, max_link_density=0.5)
    content2 = [p.text for p in paragraphs2 if not p.is_boilerplate]
    
    # Test no links (should be kept)
    html3 = '<p>Plain text without any links</p>'
    paragraphs3 = extract_text(html3, max_link_density=0.5)
    content3 = [p.text for p in paragraphs3 if not p.is_boilerplate]
    
    tests = [
        (html1, len(content1) == 0, "High link density filtered"),
        (html2, len(content2) == 1, "Low link density kept"),
        (html3, len(content3) == 1, "No links kept"),
    ]
    
    all_pass = True
    for html, passed, description in tests:
        if passed:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description}")
            all_pass = False
    
    return all_pass


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("jusText Implementation Verification")
    print("=" * 60)
    
    results = []
    
    results.append(("Feature 1: Basic Text Extraction", test_feature1()))
    results.append(("Feature 2: Boilerplate Detection", test_feature2()))
    results.append(("Feature 3: Encoding Handling", test_feature3()))
    results.append(("Feature 4: Multilingual Support", test_feature4()))
    results.append(("Feature 5: HTML Preprocessing", test_feature5()))
    results.append(("Feature 6: Context Classification", test_feature6()))
    results.append(("Feature 7: Link Density Calculation", test_feature7()))
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} {name}")
    
    print(f"\n{passed}/{total} features passed")
    
    if passed == total:
        print("\n✅ All features implemented successfully!")
        return 0
    else:
        print("\n❌ Some features need attention.")
        return 1


if __name__ == "__main__":
    sys.exit(main())