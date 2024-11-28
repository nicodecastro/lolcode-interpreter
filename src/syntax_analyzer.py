'''
Implemented Syntax Errors: 
- Closing BUHBYE
- Closing KTHXBYE
- Statements after KTHXBYE
- HAI
- Statements on same line as HAI
- variable assignment (ITZ expressions not yet)


- function before hai after kthxbye
'''

LEXEME = 0
CLASSIFICATION = 1

LITERAL_VAR_IDENTIFIER_CLASSIFICATIONS = [
    "YARN Literal",
    "NUMBAR Literal",
    "NUMBR Literal",
    "TROOF Literal",
    "TYPE Literal",
    "Identifier",
]

STATEMENT = [
        "VISIBLE",
        "GIMMEH",
        "variable",
        "O RLY?",
        "WTF?",
        "IM IN YR",
        "HOW IZ I",
        "I IZ"
    ]

OPERATION = [
    "SUM OF",
    "DIFF OF",
    "PRODUKT OF",
    "QUOSHUNT OFF",
    "MOD OF",
    "BIGGR OF",
    "SMALLR OF",
    "BOTH OF",
    "EITHER OF",
    "WON OF",
    "NOT",
    "ANY OF",
    "ALL OF",
    "BOTH SAEM",
    "DIFFRINT",
    "SMOOSH",
    "MAEK"
]

SYNTAX_ERR = 1

def syntax_analysis(tokens: list, syntax_err_handler) -> int:
    print("\n==================== PERFORMING SYNTAX ANALYSIS ====================\n")
    tokens_to_parse = tokens[:]
    parse_tree = []

    # parse program
    if check_if_match(tokens_to_parse[0], LEXEME, "HOW IZ I", parse_tree, tokens_to_parse, remove=False, append=False):     # check for functions at before HAI
        funcs = remove_funcs(tokens_to_parse, syntax_err_handler)
        if funcs == SYNTAX_ERR or parse_funcs(funcs, syntax_err_handler) == SYNTAX_ERR:
            return SYNTAX_ERR
        parse_tree.insert(0, ["funcList", funcs])
   
    if not check_if_match(tokens_to_parse[0], LEXEME, "HAI", parse_tree, tokens_to_parse):
        return syntax_err_handler("Expected 'HAI' at the start of the program")
    
    if not check_if_match(tokens_to_parse[0], CLASSIFICATION, "Linebreak", parse_tree, tokens_to_parse):
        return syntax_err_handler("Statements are not allowed on the same line as 'HAI'")
    
    if check_if_match(tokens_to_parse[0], LEXEME, "WAZZUP", parse_tree, tokens_to_parse, remove=False, append=False):
            vardec = remove_vardec(tokens_to_parse, syntax_err_handler)
            if vardec == SYNTAX_ERR or parse_vardec(vardec, syntax_err_handler) == SYNTAX_ERR:
                return SYNTAX_ERR
            parse_tree.append(["vardecList", vardec])
            check_if_match(tokens_to_parse[0], CLASSIFICATION, "Linebreak", parse_tree, tokens_to_parse)
    
    statements = remove_statements(tokens_to_parse, syntax_err_handler)
    if statements == SYNTAX_ERR:
        return SYNTAX_ERR
    parse_tree.append(["statementList", statements])
    check_if_match(tokens_to_parse[0], LEXEME, "KTHXBYE", parse_tree, tokens_to_parse, remove=True, append=True)

    # TODO check for functions after KTHXBYE
    # if check_if_match(tokens[0], LEXEME, "HOW IZ I", parse_tree, tokens_to_parse, remove=False, append=False):
    #     funcs = remove_funcs(tokens_to_parse, syntax_err_handler)
    #     if funcs == SYNTAX_ERR or parse_funcs(funcs, syntax_err_handler) == SYNTAX_ERR:
    #         return 1
    #     parse_tree.insert(0, ["funcList", funcs])

    print(f"Parse Tree:\n")
    for node in parse_tree:
        print(node)
    print("\n==================== COMPLETED SYNTAX ANALYSIS ====================")
    return 0

def check_if_match(token: list, type: int, match: str, parse_tree: list, tokens_to_parse: list, multiple=False, remove=True, append=True) -> bool:
    if multiple == False and token[type] == match:
        if append:
            parse_tree.append(match)
        if remove:
            del tokens_to_parse[0]
        return True
    elif multiple == True:
        for match_token in match:
            if match_token == token[type]:
                if append:
                    parse_tree.append(match)
                if remove:
                    del tokens_to_parse[0]
                return True
    return False

def remove_funcs(tokens_to_parse: list, syntax_err_handler) -> list:
    cur_idx = 0
    while cur_idx < len(tokens_to_parse):
        if tokens_to_parse[cur_idx][LEXEME] == "IF U SAY SO":
            break
        cur_idx += 1

    if cur_idx == len(tokens_to_parse):
        return syntax_err_handler(f"Expected 'IF U SAY SO' at the end of function")
    
    funcs = tokens_to_parse[0:cur_idx]
    del tokens_to_parse[0:cur_idx]
    return funcs

def remove_vardec(tokens_to_parse: list, syntax_err_handler) -> list:
    cur_idx = 0
    while cur_idx < len(tokens_to_parse):
        if tokens_to_parse[cur_idx][LEXEME] == "BUHBYE":
            break
        cur_idx += 1

    if cur_idx == len(tokens_to_parse):
        return syntax_err_handler(f"Expected closing 'BUHBYE' in variable declaration")
    
    vardec = tokens_to_parse[0:cur_idx+1]
    del tokens_to_parse[0:cur_idx+1]
    return vardec

def remove_statements(tokens_to_parse: list, syntax_err_handler) -> list:
    cur_idx = 0
    while cur_idx < len(tokens_to_parse):
        if tokens_to_parse[cur_idx][LEXEME] == "KTHXBYE":
            break
        cur_idx += 1

    if cur_idx == len(tokens_to_parse):
        return syntax_err_handler(f"Expected closing 'KTHXBYE' in program")

    statements = tokens_to_parse[0:cur_idx]
    del tokens_to_parse[0:cur_idx]
    return statements

def parse_vardec(vardec, syntax_err_handler):
    vardec_to_parse = vardec[:]
    del vardec[:]
    index = 0
    while vardec_to_parse:
        if vardec_to_parse[0][LEXEME] in ("WAZZUP", "<linebreak>", "BUHBYE"):
            del vardec_to_parse[0]
        elif vardec_to_parse[0][LEXEME] == "I HAS A":
            single_vardec = []
            single_vardec.append("I HAS A")
            del vardec_to_parse[0]
            if vardec_to_parse[0][CLASSIFICATION] == "Identifier":
                single_vardec.append(["Identifier", vardec_to_parse[0][LEXEME]])
                del vardec_to_parse[0]
                if vardec_to_parse[0][LEXEME] == "ITZ" and vardec_to_parse[1][CLASSIFICATION] in LITERAL_VAR_IDENTIFIER_CLASSIFICATIONS:
                    single_vardec.insert(0, "varinit")
                    # variable/literal/expr
                    single_vardec.append([vardec_to_parse[1][CLASSIFICATION], vardec_to_parse[1][LEXEME]])
                    del vardec_to_parse[0:2]
                elif vardec_to_parse[0][CLASSIFICATION] == "Linebreak":
                    single_vardec.insert(0, "vardec")
                    del vardec_to_parse[0]
                else:
                    return syntax_err_handler(f"Invalid statements after variable initialization")
            else:
                return syntax_err_handler("Expected identifier for 'I HAS A'")
            vardec.append(single_vardec)
        else:
            return syntax_err_handler(f"Unexpected '{vardec_to_parse[0][LEXEME]}' in variable declaration portion")
        
def parse_funcs(funcs, syntax_err_handler):
    funcs_to_parse = funcs[:]
    del funcs[:]
    while funcs_to_parse:
        single_func = []
        if check_if_match(funcs_to_parse[0], LEXEME, "HOW IZ I", single_func, funcs_to_parse):
            if check_if_match(funcs_to_parse[0], CLASSIFICATION, "Identifier", single_func, funcs_to_parse, remove=False, append=False):
                single_func.insert(0, "funcdec")
                single_func.append(["Identifier", funcs_to_parse[0][LEXEME]])
                del funcs_to_parse[0]

                # parse func params
                if check_if_match(funcs_to_parse[0], LEXEME, "YR", single_func, funcs_to_parse, remove=True, append=False):
                    if check_if_match(funcs_to_parse[0], CLASSIFICATION, "Identifier", single_func, funcs_to_parse, remove=False, append=False):
                        params = ["params", funcs_to_parse[0]]
                        del funcs_to_parse[0]
                        while not check_if_match(funcs_to_parse[0], CLASSIFICATION, "Linebreak", single_func, funcs_to_parse, remove=False, append=False):
                            if check_if_match(funcs_to_parse[0], LEXEME, "AN", single_func, funcs_to_parse, remove=True, append=False):
                                if check_if_match(funcs_to_parse[0], LEXEME, "YR", single_func, funcs_to_parse, remove=True, append=False):
                                    if check_if_match(funcs_to_parse[0], CLASSIFICATION, "Identifier", single_func, funcs_to_parse, remove=False, append=False):
                                        params.append(funcs_to_parse[0])
                                        del funcs_to_parse[0]
                                    else:
                                        return syntax_err_handler(f"Expected identifier for function")
                                else:
                                    return syntax_err_handler("Unexpected YR in function parameter")
                            else:
                                return syntax_err_handler("Unexpected statements in function parameters")
                        single_func.append(params)
                    else:
                        return syntax_err_handler("Unexpected YR in function parameter")
                
                # parse func body
                check_if_match(funcs_to_parse[0], CLASSIFICATION, "Linebreak", single_func, funcs_to_parse, remove=True, append=False)

            else:
                return syntax_err_handler(f"Expected identifier for function")
        else:
            print(funcs_to_parse)
            return syntax_err_handler(f"Unexpected '{funcs_to_parse[0][LEXEME]}'")
        
