import re

LITERAL_VAR_IDENTIFIER_PATTERN = [
    # ("YARN Literal", '\"[^"]+\"'),
    ("NUMBAR Literal","^-?[0-9]+\.[0-9]+"),
    ("NUMBR Literal", "^-?[0-9]+"),
    ("TROOF Literal", "(WIN|FAIL)"),
    ("TYPE Literal", "(NOOB|NUMBR|NUMBAR|YARN|TROOF)"),
    ("Variable Identifier", "^[a-zA-Z][a-zA-Z0-9_]*")
]

KEYWORDS_PATTERN = [
    ("HAI","^HAI"),
    ("KTHXBYE","^KTHXBYE"),
    ("WAZZUP","^WAZZUP"),
    ("BUHBYE","^BUHBYE"),
    ("I HAS A","^I HAS A"),
    ("ITZ"," ITZ "),
    ("R"," R "),
    ("VISIBLE","^VISIBLE"),
    ("FOUND YR","^FOUND YR"),
    ("SUM OF","SUM OF"),
    ("DIFF OF","DIFF OF"),
    ("PRODUKT OF","PRODUKT OF"),
    ("QUOSHUNT OF","QUOSHUNT OF"),
    ("MOD OF","MOD OF"),
    ("BIGGR OF","BIGGR OF"),
    ("SMALLR OF","SMALLR OF"),
    ("BOTH OF","BOTH OF"),
    ("EITHER OF","EITHER OF"),
    ("WON OF","WON OF"),
    ("NOT","NOT"),
    ("ANY OF","ANY OF"),
    ("ALL OF","ALL OF"),
    ("BOTH SAEM","BOTH SAEM"),
    ("DIFFRINT","^DIFFRINT"),
    ("SMOOSH","^SMOOSH"),
    ("MAEK","^MAEK"),
    ("A"," A "),
    ("AN"," AN "),
    ("IS NOW A","IS NOW A"),
    ("GIMMEH","^GIMMEH"),
    ("O RLY","^O RLY\?"),
    ("YA RLY","^YA RLY"),
    ("MEBBE","^MEBBE"),
    ("NO WAI","^NO WAI"),
    ("OIC","^OIC"),
    ("WTF","^WTF\?"),
    ("OMG","^OMG"),
    ("OMGWTF","^OMGWTF"),
    ("IM IN YR","^IM IN YR"),
    ("UPPIN","UPPIN"),
    ("NERFIN","NERFIN"),
    ("YR","YR"),
    ("TIL","TIL"),
    ("WILE","WILE"),
    ("IM OUTTA YR","^IM OUTTA YR"),
    ("HOW IZ I","^HOW IZ I"),
    ("IF U SAY SO","^IF U SAY SO"),
    ("GTFO","^GTFO"),
    ("I IZ","^I IZ"),
    ("MKAY","MKAY")
    ]

def lexical_analysis(lexeme_table_values: list, lolcode_source: str) -> None:
    lolcode_lines = lolcode_source.split("\n")
    lolcode_lines_len = len(lolcode_lines)

    for line in lolcode_lines:
        line = line.strip()
        if line:
            tokens = tokenize_classify(line)
            if tokens:
                for token in tokens:
                    lexeme_table_values.append(token)
    return

def tokenize_classify(line: str) -> tuple:
    original_line = line
    tokens = []
    print(f"tokenizing: {line}")

    # standalone comments
    btw_token = None
    btw_token = re.search("^BTW(.*)", line)
    if btw_token:
        tokens.append(("BTW", "Keyword"))
        comment = btw_token.group(1).strip()
        if comment:
            tokens.append((comment, "Comment"))
        tokens.append(("<linebreak>", "Linebreak"))
        return tokens
    
    # elif re.search("^OBTW", line):
    #     tokens.append(("OBTW", "Keyword"))

    # check for in-line comments and remove them
    token = re.search(" BTW(.*)", line)
    if token:
        tokens.append(("BTW", "Keyword"))
        comment = token.group(1).strip()
        tokens.append((comment, "Comment"))
        line = re.sub(" BTW(.*)", " ", line)

    isFunction = False
    isLoop = False
    # keywords
    for keyword, pattern in KEYWORDS_PATTERN:
        token = re.search(pattern, line)
        if token:
            # print(f'found {keyword} under {pattern}\n')
            tokens.append((keyword, "Keyword"))
            line = re.sub(pattern, " ", line)


    token = re.search('.*(\"[^"]+\").*', line)
    if token:
        tokens.append((token.group(1), "YARN Literal"))
        line = re.sub('\"[^"]+\"', " ", line)
        
    print(f'remaining: {line.split()}')
    if line:
        for remaining_tokens in line.split():
            for literal, pattern in LITERAL_VAR_IDENTIFIER_PATTERN:
                token = re.search(pattern, remaining_tokens)
                if token:
                    tokens.append((token.string, literal))
                    break
                    

    tokens.append(("<linebreak>", "Linebreak"))
    
    return tokens