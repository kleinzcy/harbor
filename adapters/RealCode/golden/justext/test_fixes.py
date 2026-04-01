#!/usr/bin/env python3
"""Test fixes for identified issues."""

from justext import extract_text

print("Testing fixes for identified issues...")

# Test 1: Basic extraction with h1
print("\n1. Testing <h1> + <p> extraction:")
html = '<h1>Title</h1><p>Content</p>'
paragraphs = extract_text(html, min_paragraph_length=5)
content = [p.text for p in paragraphs if not p.is_boilerplate]
print(f"   Input: {html}")
print(f"   Output: {content}")
print(f"   Result: {'PASS' if content == ['Title', 'Content'] else 'FAIL'}")

# Test 2: Encoding with Chinese characters
print("\n2. Testing encoding with Chinese characters:")
html_bytes = '<p>Hello 世界</p>'.encode('utf-8')
paragraphs = extract_text(html_bytes, min_paragraph_length=5)
content = [p.text for p in paragraphs if not p.is_boilerplate]
print("   Input: bytes with Chinese characters")
print(f"   Output: {content}")
print(f"   Result: {'PASS' if content and '世界' in content[0] else 'FAIL'}")

# Test 3: Script removal
print("\n3. Testing script removal:")
html = '<body><script>alert("test")</script><p>Real content</p></body>'
paragraphs = extract_text(html, min_paragraph_length=5)
content = [p.text for p in paragraphs if not p.is_boilerplate]
print(f"   Input: {html[:50]}...")
print(f"   Output: {content}")
print(f"   Result: {'PASS' if content == ['Real content'] else 'FAIL'}")

# Test 4: Style removal
print("\n4. Testing style removal:")
html = '<body><style>.class { color: red; }</style><p>Text</p></body>'
paragraphs = extract_text(html, min_paragraph_length=5)
content = [p.text for p in paragraphs if not p.is_boilerplate]
print(f"   Input: {html[:50]}...")
print(f"   Output: {content}")
print(f"   Result: {'PASS' if content == ['Text'] else 'FAIL'}")

# Test 5: Comment removal
print("\n5. Testing comment removal:")
html = '<body><!-- Comment --><p>Content</p></body>'
paragraphs = extract_text(html, min_paragraph_length=5)
content = [p.text for p in paragraphs if not p.is_boilerplate]
print(f"   Input: {html}")
print(f"   Output: {content}")
print(f"   Result: {'PASS' if content == ['Content'] else 'FAIL'}")

# Test 6: Check what's actually being extracted
print("\n6. Debug: Check all paragraphs extracted:")
html = '<body><script>test</script><p>Real content</p></body>'
paragraphs = extract_text(html, min_paragraph_length=5)
print(f"   All paragraphs: {[(p.text[:20], p.is_boilerplate) for p in paragraphs]}")