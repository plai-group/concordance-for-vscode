import sys
from itertools import cycle
import ipdb
import pyjson5 as json5  # for reading json w/ potential vscode comments
import json  # for saving
import re
import seaborn as sns

# paths
FILE_PATH = sys.argv[1]
SETTINGS_PATH = '/Users/vmasrani/dev/phd/dendron/dendron.code-workspace'
ARGS_PATH = '/Users/vmasrani/dev/phd/dendron/scripts/.args'
OUT_PATH = '/Users/vmasrani/dev/phd/dendron/vault/assets/concordance.csv'

# globals
PUNC = '[\p{P},\W,\_]{1,5}'  # seperators between words can be punctionation or whitespace x5
START = '[\\s,\\\",\\\']?'
HIGHLIGHT_KEY = 'highlight.regexes'

COLORS = cycle(sns.color_palette().as_hex())
TOSTRING = lambda x: str.join(" ", x)

# We pass in arguments via .args file because
# of how command-runner and emeraldwalk.runonsave work

with open(ARGS_PATH, 'r') as file:
    ARGS = [int(i) for i in file.readline().split()]

with open(SETTINGS_PATH) as json_file:
    SETTINGS = json5.load(json_file)

# fail fast here w/ bad paths or args
MIN_PHRASE_LENGTH = ARGS[0]
MIN_STRING_LENGTH = ARGS[1]
WORDS_ONLY        = ARGS[2]
RESET             = ARGS[3]

def is_valid(candidate, phrases):
    for p in phrases:
        if (p != candidate) and (candidate in p):
            return False
    return True

def parse_lines(lines):
    # deep nested generator so we iterate through everything only once
    for line in lines:
        for s in sent_tokenize(line):
            tokens = word_tokenize(re.sub(r'\W+', ' ', s.lower()))
            for gram in everygrams(tokens):
                yield gram

def make_key(phrase):
    phrase = phrase.replace(" ", PUNC)
    return f"({START}{phrase}{START})"

def make_val(phrase, color):
    return {
        'name': phrase,
        'decorations': [{'color': color}],
    }

def make_regexs(df):
    return {make_key(k): make_val(k, next(COLORS)) for k, v in df.iterrows()}

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

def process_file(md_path):
    lines = markdown_to_text(md_path)
    counts = defaultdict(int)
    for phrase in parse_lines(lines):
        counts[phrase] += 1

    df = (pd
          .DataFrame.from_dict(counts, orient='index', columns=['freq'])
          .query('freq > 1')
          .reset_index()
          .assign(
              phrase_length=lambda x: x['index'].apply(len),
              string_length=lambda x: x['index'].apply(lambda y: len(str.join('', y))),
          )
          .query(f'phrase_length > {MIN_PHRASE_LENGTH}')
          .query(f'string_length > {MIN_STRING_LENGTH}')
          .sort_values(['string_length', 'freq'], ascending=False)
          )

    df['index'] = df['index'].apply(TOSTRING)
    df = df.set_index('index')

    repeated_phrases = []

    for _, row in df.iterrows():
        candidate = row.name
        if is_valid(candidate, repeated_phrases):
            repeated_phrases.append(candidate)

    df = df[df.index.isin(repeated_phrases)]
    return df


def process_words_only(md_path):
    """
    use clever regex instead of pandas
    https://stackoverflow.com/questions/45986641/count-repetitive-words-in-string-using-regex
    (faster and avoids import overhead)
    """
    lines = markdown_to_text(md_path)
    text = str.join("", lines)
    phrases = [r for r in re.findall(r'\b(\w+)\b(?=.*\b\1\b)', text, re.I) if len(r) > MIN_STRING_LENGTH]
    return list(set(phrases))

if __name__ == "__main__":
    if RESET:
        SETTINGS['settings'][HIGHLIGHT_KEY] = {}
    elif WORDS_ONLY:
        phrases = process_words_only(FILE_PATH)
    else:
        # imports here for fast loading when doing WORDS_ONLY
        from collections import defaultdict
        from nltk.tokenize import sent_tokenize, word_tokenize
        from nltk.util import everygrams
        import markdown
        from bs4 import BeautifulSoup
        import pandas as pd
        import numpy as np

        df = process_file(FILE_PATH)

    if not RESET:
        SETTINGS['settings'][HIGHLIGHT_KEY] = make_regexs(df)
        df.to_csv(OUT_PATH)
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(df)

    with open(SETTINGS_PATH, 'w') as fp:
        json.dump(SETTINGS, fp, indent=4)
