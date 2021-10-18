from bs4 import BeautifulSoup
import ipdb
import markdown
import re

def markdown_to_text(markdown_path):
    """ Converts a markdown file to plaintext """
    with open(markdown_path, 'r') as f:
        text = f.read().encode('utf-8').decode('ascii', 'ignore')
    # md -> html -> text since BeautifulSoup can extract text cleanly
    html = markdown.markdown(text)

    # remove code snippets
    html = re.sub(r'<pre>(.*?)</pre>', ' ', html)
    html = re.sub(r'<code>(.*?)</code >', ' ', html)
    html = re.sub(r'(\$+)(?:(?!\1)[\s\S])*\1', ' ', html) # mathjax
    html = re.sub(r' +', ' ', html)

    # extract text
    soup = BeautifulSoup(html, "html.parser")
    text = ''.join(soup.findAll(text=True))
    return [t.lower() for t in text.split('\n') if t]

def old(md_path):
    with open(md_path, 'r') as f:
        text = f.read()
        out = markdown.markdown(text)
        soup = BeautifulSoup(out, 'lxml')

    return soup.replace

def parse_lines(lines):
    # deep nested generator so we iterate through everything only once
    for line in lines:
        for s in sent_tokenize(line):
            tokens = word_tokenize(re.sub(r'\W+', ' ', s.lower()))
            for gram in everygrams(tokens):
                yield gram

def process_words_only(lines):
    """
    use clever regex instead of pandas
    https://stackoverflow.com/questions/45986641/count-repetitive-words-in-string-using-regex
    (faster and avoids import overhead)
    """
    text = str.join("", lines)
    phrases = [r for r in re.findall(r'\b(\w+)\b(?=.*\b\1\b)', text, re.I) if len(r) > MIN_STRING_LENGTH]
    return list(set(phrases))

path = '/Users/vmasrani/dev/phd/dendron/vault/formal-notes.understanding-differentiable-particle-filtering.md'
lines = markdown_to_text(path)
text = str.join("", lines)
print(text)
# with open(path, 'r') as file:
#     markdown = file.read().replace('\n', '')


# print(markdown)



# import ipdb; ipdb.set_trace()
# print(text)
# print(txt)
