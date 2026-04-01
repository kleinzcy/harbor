#!/usr/bin/env python3
"""
Example usage of jusText library.
"""

from justext import extract_text, get_available_languages, load_stoplist

# Example HTML with mixed content
html_example = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Example Article</title>
    <style>
        body { font-family: Arial; }
        nav { background: #eee; padding: 10px; }
    </style>
    <script>
        console.log("This is a script");
    </script>
</head>
<body>
    <header>
        <h1>My Website</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/about">About</a>
            <a href="/contact">Contact</a>
            <a href="/products">Products</a>
            <a href="/services">Services</a>
        </nav>
    </header>
    
    <main>
        <article>
            <h2>Article Title</h2>
            <p>This is the first paragraph of the article. It contains useful information 
            about the topic being discussed. The paragraph has sufficient length and 
            contains common words that help with classification.</p>
            
            <p>Short ad paragraph.</p>
            
            <p>This is another substantial paragraph with meaningful content. It continues 
            the discussion from the previous paragraph and provides additional insights 
            into the subject matter. The text here is relevant and informative.</p>
            
            <div class="advertisement">
                <p><a href="/buy">Buy now!</a> <a href="/learn">Learn more</a> Special offer!</p>
            </div>
            
            <p>The final paragraph concludes the article with important takeaways and 
            summary points. This content is valuable to readers and should be extracted.</p>
        </article>
    </main>
    
    <footer>
        <p>&copy; 2023 My Website. All rights reserved.</p>
        <p><a href="/privacy">Privacy Policy</a> | <a href="/terms">Terms of Service</a></p>
    </footer>
</body>
</html>
"""

def demonstrate_basic_extraction():
    """Demonstrate basic text extraction."""
    print("=== Basic Text Extraction ===")
    paragraphs = extract_text(html_example)
    
    print(f"Total paragraphs extracted: {len(paragraphs)}")
    print(f"Content paragraphs: {sum(1 for p in paragraphs if not p.is_boilerplate)}")
    print(f"Boilerplate paragraphs: {sum(1 for p in paragraphs if p.is_boilerplate)}")
    print()
    
    print("Content paragraphs:")
    for i, paragraph in enumerate(paragraphs):
        if not paragraph.is_boilerplate:
            print(f"{i+1}. {paragraph.text[:80]}...")
            print(f"   Words: {paragraph.word_count}, Link density: {paragraph.link_density:.2f}")
    print()

def demonstrate_language_support():
    """Demonstrate language support."""
    print("=== Language Support ===")
    
    # Get available languages
    languages = get_available_languages()
    print(f"Available languages: {', '.join(languages)}")
    print()
    
    # Show stopwords for a few languages
    for lang in ['english', 'german', 'french']:
        try:
            stopwords = load_stoplist(lang)
            print(f"{lang.capitalize()}: {len(stopwords)} stopwords")
            sample = list(stopwords)[:5]
            print(f"  Sample: {', '.join(sample)}")
        except ValueError as e:
            print(f"{lang}: {e}")
    print()

def demonstrate_custom_parameters():
    """Demonstrate custom extraction parameters."""
    print("=== Custom Parameters ===")
    
    # Extract with stricter parameters
    paragraphs = extract_text(
        html_example,
        language="english",
        min_paragraph_length=30,
        max_link_density=0.3,
        min_stopword_density=0.15,
    )
    
    print("Extracted with strict parameters:")
    for i, paragraph in enumerate(paragraphs):
        if not paragraph.is_boilerplate:
            print(f"{i+1}. {paragraph.text[:60]}...")
    print()

def main():
    """Run all demonstrations."""
    print("jusText Library Demonstration\n")
    
    demonstrate_basic_extraction()
    demonstrate_language_support()
    demonstrate_custom_parameters()
    
    print("=== Command Line Usage ===")
    print("To use jusText from command line:")
    print("  cat input.html | python extract_text.py")
    print("  cat input.html | python extract_text.py --language german --min-length 25")
    print()
    print("For more options:")
    print("  python extract_text.py --help")

if __name__ == "__main__":
    main()