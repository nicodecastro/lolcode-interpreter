'''
Implement
- variables /
- operations
- input/output
- if-then
- switch-case
- loops
- functions
'''

LEXEME = 0
CLASSIFICATION = 1
TYPE = 0

def remove_comments(tokens: list, syntax_err_handler) -> list:
    print("\n==================== PERFORMING SYNTAX ANALYSIS ====================\n")
    print("Removing comments\n")
    updated_tokens = []
    # remove comment-related tokens
    for i, token in enumerate(tokens):
        if tokens[i][CLASSIFICATION] == "Invalid Token":
            return syntax_err_handler("Invalid token")
        elif tokens[i][CLASSIFICATION] == 'Invalid statements after TLDR':
            return syntax_err_handler("Unexpected statements after TLDR")
        elif tokens[i][CLASSIFICATION] == 'No closing TLDR':
            return syntax_err_handler("Expected closing TLDR on a separate line")
        elif token[LEXEME] == 'BTW' or token[LEXEME] == 'OBTW' or token[CLASSIFICATION] == 'Comment':
            pass
        elif token[LEXEME] == 'TLDR' and token[CLASSIFICATION] == 'Keyword':
            pass
        else:
            updated_tokens.append(token)

    # fix linebreaks, start & consecutive linebreaks
    while True:
        if updated_tokens[0][CLASSIFICATION] == "Linebreak":
            del updated_tokens[0]
        else:
            break

    fixed_tokens = [updated_tokens[0]]
    for token in updated_tokens[1:]:
        if fixed_tokens[-1][CLASSIFICATION] != 'Linebreak' or token != fixed_tokens[-1]:
            fixed_tokens.append(token)

    while fixed_tokens[-1][CLASSIFICATION] == 'Linebreak':
        del fixed_tokens[-1]

    print(f"List of Tokens:\n{fixed_tokens}\n")

    return fixed_tokens

def syntax_analysis(tokens: list, syntax_err_handler) -> int:
    parse_tree = tokens[:]
    

    # # =============== Fix Identifiers, Literals, and Linebreaks ===============
    index = 0
    for token in parse_tree:
        # function name
        if token[LEXEME] in ["HOW IZ I", "I IZ"] and index < len(parse_tree)-1 and parse_tree[index+1][CLASSIFICATION] == "Identifier":
            parse_tree[index+1] = ["funcname", parse_tree[index+1][LEXEME]]
            tokens[index+1] = (parse_tree[index+1][LEXEME], "Function Name")
        # loop label
        elif token[LEXEME] in ["IM IN YR", "IM OUTTA YR"] and index < len(parse_tree)-1 and parse_tree[index+1][CLASSIFICATION] == "Identifier":
            parse_tree[index+1] = ["looplabel", parse_tree[index+1][LEXEME]]
            tokens[index+1] = (parse_tree[index+1][LEXEME], "Loop Label")
        # variable
        elif token[CLASSIFICATION] == "Identifier":
            tokens[index] = (parse_tree[index][LEXEME], "Variable Identifier")
            parse_tree[index] = ["varident", parse_tree[index][LEXEME]]
        elif token[CLASSIFICATION] in ("NUMBR Literal", "NUMBAR Literal", "TROOF Literal", "TYPE Literal", "YARN Literal"):
            parse_tree[index] = ["literal", token[CLASSIFICATION], token[LEXEME]]
        elif token[CLASSIFICATION] == "Linebreak":
            parse_tree[index] = "linebreak"
        index += 1


    index = 0
    for token in parse_tree:
        # =============== Keywords w/o Nesting ===============
        if token[LEXEME] == "HAI":
            parse_tree[index] = "HAI"

        elif token[LEXEME] == "KTHXBYE":
            parse_tree[index] = "KTHXBYE"

        elif token[LEXEME] in ("GTFO"):
            parse_tree[index] = "loopbreak"

        # =============== Variable Assignment ===============
        elif token[LEXEME] == 'varident' and index < len(parse_tree)-1 and parse_tree[index+1][LEXEME] == "R":
            parse_tree[index] = ["varassign", parse_tree[index]]
            del parse_tree[index+1]

        # =============== Typecasting ===============
        elif token[LEXEME] == "MAEK":
            # TODO Clarify if need A, e.g. MAEK var1 A NUMBAR vs. y R MAEK A y TROOF (for now implementation is MAEK A)
            if index < len(parse_tree)-2 and parse_tree[index+1][LEXEME] == "A" and (parse_tree[index+2][TYPE] in ("varident", "literal")):
                if index < len(parse_tree)-3 and (parse_tree[index+3][CLASSIFICATION] == "TYPE Literal"):
                    parse_tree[index] = ["typecast", parse_tree[index+2], parse_tree[index+3]]
                    del parse_tree[index+1:index+4]
                else:
                    return syntax_err_handler("Expected type literal to typecast to")
            else:
                return syntax_err_handler("Expected literal for explicit typecasting")
        elif token[TYPE] == 'varident' and index < len(parse_tree)-1 and parse_tree[index+1][LEXEME] == "IS NOW A":
            if index < len(parse_tree)-2 and (parse_tree[index+2][CLASSIFICATION] == "TYPE Literal"):
                parse_tree[index] = ["typecast", parse_tree[index], parse_tree[index+2]]
                if index < len(parse_tree)-3 and parse_tree[index+3] != "linebreak":
                    return syntax_err_handler("Expected new line after MAEK")
                del parse_tree[index+1:index+3]
            else:
                return syntax_err_handler("Expected type literal to typecast to")

        # =============== Input ===============
        elif token[LEXEME] == "GIMMEH":
            if index < len(parse_tree)-1 and parse_tree[index+1][TYPE] == "varident":
                parse_tree[index] = ["input", parse_tree[index+1]]
                if parse_tree[index+2] != "linebreak":
                    return syntax_err_handler("Expected new line after GIMMEH")
                del parse_tree[index+1]

        index += 1

    # =============== Operations ===============
    index = 0
    for token in parse_tree:
        if token[LEXEME] in ("SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "MOD OF", "BIGGR OF", "SMALLR OF", "BOTH SAEM", "DIFFRINT", "BOTH OF","EITHER OF","WON OF","NOT"):
            del_index = [index]
            operands = parse_expression(parse_tree[index:], syntax_err_handler, del_index)
            parse_tree[index] = ["expr", operands]
            del parse_tree[index+1:del_index[0]+1]

        # elif token[LEXEME] in ("BOTH OF","EITHER OF","WON OF","NOT"):
        #     del_index = [index]
        #     operands = parse_boolop(parse_tree[index:], syntax_err_handler, del_index)
        #     parse_tree[index] = ["expr", operands]
        #     del parse_tree[index+1:del_index[0]+1]

        index += 1

    # =============== Operations pt. 2 ===============
    index = 0
    for token in parse_tree:
        if token[LEXEME] in ("ANY OF", "ALL OF"):
            bool_start_index = index+1
            bool_tokens = ["infboolop", token[LEXEME]]
            while bool_start_index < len(parse_tree)-1 and (parse_tree[bool_start_index][LEXEME] != "MKAY" and parse_tree[bool_start_index] != 'linebreak'):
                if parse_tree[bool_start_index][TYPE] in ('varident', 'literal', 'expr'):
                    bool_tokens.append(parse_tree[bool_start_index])
                    del parse_tree[bool_start_index]
                    if parse_tree[bool_start_index][LEXEME] == "AN":
                        del parse_tree[bool_start_index]
                    elif parse_tree[bool_start_index][LEXEME] == "MKAY":
                        continue
                    else:
                        return syntax_err_handler("Unexpected statements in 'ANY OF' or 'ALL OF'")
                else:
                    print(parse_tree[bool_start_index][LEXEME])
                    return syntax_err_handler("Expected variable, literal, or expression for 'ANY OF' or 'ALL OF'")
            if bool_start_index < len(parse_tree)-1 and parse_tree[bool_start_index] == 'linebreak':
                return syntax_err_handler("Expected closing 'MKAY' keyword for 'ANY OF' or 'ALL OF'")
            elif bool_start_index < len(parse_tree)-1 and parse_tree[bool_start_index][LEXEME] == 'MKAY':
                del parse_tree[bool_start_index]
            parse_tree[index] = ["expr", bool_tokens]
        index += 1

    # =============== String Concatenation ===============
    index = 0
    for token in parse_tree:
        if token[LEXEME] == "SMOOSH":
            smoosh_start_index = index+1
            smoosh_tokens = ["concat"]
            while smoosh_start_index < len(parse_tree)-1 and parse_tree[smoosh_start_index] != 'linebreak':
                if parse_tree[smoosh_start_index][TYPE] in ('varident', 'literal', 'expr'):
                    smoosh_tokens.append(parse_tree[smoosh_start_index])
                    del parse_tree[smoosh_start_index]
                    if parse_tree[smoosh_start_index][LEXEME] == "AN":
                        del parse_tree[smoosh_start_index]
                    elif parse_tree[smoosh_start_index] == "linebreak":
                        pass
                    else:
                        return syntax_err_handler("Unexpected statements in string concatenation")
                else:
                    return syntax_err_handler("Expected variable, literal, or expression for string concatenation")
            parse_tree[index] = smoosh_tokens
        index += 1

    index = 0
    for token in parse_tree:
        # =============== VISIBLE ===============
        if token[LEXEME] == "VISIBLE":
            print_start_index = index+1
            print_tokens = ["print"]
            while print_start_index < len(parse_tree)-1 and parse_tree[print_start_index] != 'linebreak':
                if parse_tree[print_start_index][TYPE] in ('varident', 'literal', 'expr', 'concat'):
                    print_tokens.append(parse_tree[print_start_index])
                    del parse_tree[print_start_index]
                    if parse_tree[print_start_index][LEXEME] == "AN" or parse_tree[print_start_index][LEXEME] == "+ ":
                        del parse_tree[print_start_index]
                    elif parse_tree[print_start_index] == "linebreak":
                        pass
                    else:
                        print(parse_tree[print_start_index])
                        return syntax_err_handler("Unexpected statements in 'VISIBLE'")
                else:
                    print(parse_tree[print_start_index])
                    return syntax_err_handler("Expected variable, literal, or expression for 'VISIBLE'")
            parse_tree[index] = print_tokens

        # =============== Variable Assignment pt. 2 ===============
        elif token[LEXEME] == 'varassign' and index < len(parse_tree)-1 and parse_tree[index+1][TYPE] in ("literal", "varident", "expr"):
            parse_tree[index].append(parse_tree[index+1])
            del parse_tree[index+1]
        elif token[LEXEME] == 'varassign' and (index >= len(parse_tree)-1 or parse_tree[index+1][TYPE] not in ("literal", "varident", "expr")):
            return syntax_err_handler("Expected literal, variable, or expression in variable assignment")
        index += 1

    # =============== If-then Statements ===============
    index = 0
    for token in parse_tree:
        if token[LEXEME] == "O RLY?":
            if_then_tokens = ["ifelse"]
            del parse_tree[index]
            if parse_tree[index] != 'linebreak':
                return syntax_err_handler("Unexpected statements after 'O RLY?'")
            del parse_tree[index]
            if parse_tree[index][LEXEME] != 'YA RLY':
                return syntax_err_handler("Expected 'YA RLY' for if-then conditional")
            del parse_tree[index]
            if parse_tree[index] != 'linebreak':
                return syntax_err_handler("Unexpected statements after 'O RLY?'")
            del parse_tree[index]
            if_tokens = ["if"]
            while index < len(parse_tree)-1 and parse_tree[index][LEXEME] not in ("NO WAI", "OIC"):
                if parse_tree[index][LEXEME] in ("YA RLY", "O RLY?", "WTF?", "OMG", "OMGWTF"):
                    return syntax_err_handler("Unexpected nesting in if-then statement")
                elif parse_tree[index] != "linebreak":
                    if_tokens.append(parse_tree[index])
                del parse_tree[index]
            if_then_tokens.append(if_tokens)
            
            
            if index < len(parse_tree)-1 and parse_tree[index][LEXEME] == 'NO WAI' and parse_tree[index+1] == 'linebreak':
                del parse_tree[index:index+2]
                else_tokens = ["else"]
                while index < len(parse_tree)-1 and parse_tree[index][LEXEME] not in ("OIC"):
                    if parse_tree[index][LEXEME] in ("YA RLY", "NO WAI", "O RLY?", "WTF?", "OMG", "OMGWTF"):
                        return syntax_err_handler("Unexpected nesting in if-then statement")
                    elif parse_tree[index] != "linebreak":
                        else_tokens.append(parse_tree[index])
                    del parse_tree[index]
                if_then_tokens.append(else_tokens)
            elif index < len(parse_tree)-1 and parse_tree[index][LEXEME] == 'NO WAI' and parse_tree[index+1] != 'linebreak':
                return syntax_err_handler("Unexpected statements after 'NO WAI'")
            
            if parse_tree[index] == parse_tree[-1]:
                return syntax_err_handler("Expected OIC for if-then statement")
            parse_tree[index] = if_then_tokens
        index += 1
                
    # =============== Switch-case ===============
    index = 0
    for token in parse_tree:
        if token[LEXEME] == "WTF?":
            switch_case_tokens = ["switchcase"]
            del parse_tree[index]
            if parse_tree[index] != 'linebreak':
                return syntax_err_handler("Unexpected statements after 'WTF?'")
            del parse_tree[index]
            while True:
                if parse_tree[index] == parse_tree[-1]:
                    return syntax_err_handler("Expected OIC for switch-case statement")
                if parse_tree[index][LEXEME] == 'OIC':
                    break
                elif parse_tree[index][LEXEME] == 'OMGWTF':     # next needs to be OIC
                    del parse_tree[index]
                    omgwtf_token = ["omgwtf"]
                    if parse_tree[index] != 'linebreak':
                        return syntax_err_handler("Unexpected statements after 'OMGWTF'")
                    del parse_tree[index]
                    while index < len(parse_tree)-1 and parse_tree[index][LEXEME] not in ('OIC'):
                        if parse_tree[index][LEXEME] in ("ifelse", "WTF?", "OMG", "OMGWTF"):
                            return syntax_err_handler("Unexpected nesting in if-then statement")
                        elif parse_tree[index] != "linebreak":
                            omgwtf_token.append(parse_tree[index])
                        del parse_tree[index]
                    switch_case_tokens.append(omgwtf_token)
                elif parse_tree[index][LEXEME] == 'OMG':
                    del parse_tree[index]
                    if parse_tree[index][TYPE] != 'literal':
                        return syntax_err_handler("Expected value literal for 'OMG'")
                    omg_token = ['omg', parse_tree[index]]
                    del parse_tree[index]
                    if parse_tree[index] != 'linebreak':
                        return syntax_err_handler("Unexpected statements after 'OMG'")
                    del parse_tree[index]
                    while index < len(parse_tree)-1 and parse_tree[index][LEXEME] not in ('OMG', 'OMGWTF', 'OIC'):
                        if parse_tree[index][LEXEME] in ("ifelse", "WTF?"):
                            return syntax_err_handler("Unexpected nesting in if-then statement")
                        elif parse_tree[index] != "linebreak":
                            omg_token.append(parse_tree[index])
                        del parse_tree[index]
                    switch_case_tokens.append(omg_token)
                else:
                    return syntax_err_handler("Unexpected statements in switch-case")
            if parse_tree[index] == parse_tree[-1]:
                return syntax_err_handler("Expected OIC for if-then statement")
            parse_tree[index] = switch_case_tokens
        index += 1

    # =============== Loops ===============
    index = 0
    for token in parse_tree:
        if token[LEXEME] == "IM IN YR":
            del parse_tree[index]
            loop_tokens = ["loop"]
            if parse_tree[index][TYPE] != "looplabel":
                return syntax_err_handler("Expected label for loop")
            loop_label = parse_tree[index]
            loop_tokens.append(loop_label)
            del parse_tree[index]
            if parse_tree[index][LEXEME] not in ("UPPIN", "NERFIN"):
                return syntax_err_handler("Expected 'UPPIN/NERFIN' operation for loop")
            loop_tokens.append(['loopop', parse_tree[index][LEXEME]])
            del parse_tree[index]
            if parse_tree[index][LEXEME] != "YR":
                return syntax_err_handler("Expected 'YR' for loop")
            del parse_tree[index]
            if parse_tree[index][TYPE] != "varident":
                return syntax_err_handler("Expected variable for loop")
            loop_tokens[-1].append(parse_tree[index])
            del parse_tree[index]
            if parse_tree[index][LEXEME] not in ("TIL", "WILE"):
                return syntax_err_handler("Expected 'TIL/WILE' for loop")
            loop_tokens.append(['condexpr', parse_tree[index][LEXEME]])
            del parse_tree[index]
            if parse_tree[index][TYPE] != "expr":
                return syntax_err_handler("Expected expression for loop")
            loop_tokens[-1].append(parse_tree[index])
            del parse_tree[index]

            if parse_tree[index] != 'linebreak':
                return syntax_err_handler("Unexpected statements after loop expression")
            del parse_tree[index]

            loop_statements = ['loopstatements']
            while index < len(parse_tree)-1 and parse_tree[index][LEXEME] not in ('IM OUTTA YR'):
                if parse_tree[index][LEXEME] in ("IM IN YR", "TIL", "WILE", "UPPIN", "NERFIN"):
                    return syntax_err_handler("Unexpected loop nesting")
                elif parse_tree[index] != "linebreak":
                    loop_statements.append(parse_tree[index])
                del parse_tree[index]
            if parse_tree[index] == parse_tree[-1]:
                return syntax_err_handler("Expected 'IM OUTTA YR' for loop")
            del parse_tree[index]
            if parse_tree[index][CLASSIFICATION] != loop_label[CLASSIFICATION]:
                return syntax_err_handler("Unexpected loop label in 'IM OUTTA YR'")
            loop_tokens.append(loop_statements)

            parse_tree[index] = loop_tokens
        index += 1

    # =============== Variable Declaration ===============
    index = 0
    for token in parse_tree:
        if token[LEXEME] == "I HAS A":
            if index < len(parse_tree)-1 and parse_tree[index+1][TYPE] == 'varident':
                parse_tree[index] = ['vardec', parse_tree[index+1]]
                del parse_tree[index+1]
            else:
                return syntax_err_handler("Expected variable identifier in variable declaration")
        index += 1

    # =============== Variable Initialization ===============
    index = 0
    for token in parse_tree:
        if token[TYPE] == "vardec" and index < len(parse_tree)-1 and parse_tree[index+1][LEXEME] == "ITZ":
            if index < len(parse_tree)-2 and parse_tree[index+2][TYPE] in ('varident', 'literal', 'expr'):
                parse_tree[index] = ['varinit', token, parse_tree[index+2]]
                del parse_tree[index+1:index+3]
            else:
                return syntax_err_handler("Expected literal, variable, or expression for variable initialization")
        elif token[TYPE] == "vardec" and index < len(parse_tree)-1 and parse_tree[index+1] != "linebreak":
            print(token)
            return syntax_err_handler("Unexpected statements after variable declaration")
        index += 1

    # =============== Variable Declaration Portion ===============
    index = 0
    vardec_start = 0
    for token in parse_tree:
        if token[LEXEME] == "WAZZUP" and index < len(parse_tree)-1 and parse_tree[index+1] == "linebreak":
            del parse_tree[index:index+2]
            vardecport = ["vardecport"]
            vardec_end = index
            for token in parse_tree[index:]:
                if token[LEXEME] == "BUHBYE" and index < len(parse_tree)-1 and parse_tree[vardec_end+1] == "linebreak":
                    break
                elif token[LEXEME] == "BUHBYE" and index < len(parse_tree)-1 and parse_tree[vardec_end+1] != "linebreak":
                    return syntax_err_handler("Unexpected statements after 'BUHBYE'")
                elif token[TYPE] in ('vardec', 'varinit'):
                    vardecport.append(token)
                elif parse_tree[vardec_end-1][TYPE] in ('vardec', 'varinit') and token == "linebreak":
                    pass
                else:
                    return syntax_err_handler("Unexpected statements in variable declaration portion")
                vardec_end += 1
            parse_tree[index] = vardecport
            del parse_tree[index+1:vardec_end+1]
            break
        elif token[LEXEME] == "WAZZUP" and index < len(parse_tree)-1 and parse_tree[index+1] != "linebreak":
            return syntax_err_handler("Unexpected statements after 'WAZZUP'")
        index += 1

    # =============== TODO Statements ===============
    # elif token[LEXEME] == "HAI":
    #     parse_tree[index] = "HAI"

    # elif token[LEXEME] == "KTHXBYE":
    #     parse_tree[index] = "KTHXBYE"

    # =============== TODO Functions ===============

    # =============== TODO Program ===============
    # program = ['program']
    # index = 0
    # for token in parse_tree:
    #     if token[0] == 'HAI':
    #         break
    #     program.append(token)
    #     index += 1

    # if index == len(parse_tree):
    #     return syntax_err_handler("Expected 'HAI' at the start of the program")
    # else:
    #     program.append(parse_tree[index])
    #     index += 2

    # if parse_tree[index][0] == 'vardecs':
    #     program.append(parse_tree[index])
    #     index += 2

    # if parse_tree[index][0] == 'statements':
    #     program.append(parse_tree[index])
    #     index += 2
    
    # if parse_tree[index] == 'KTHXBYE':
    #     program.append(parse_tree[index])

    print(f"Parse Tree:")
    for node in parse_tree:
        print(node)
    print("\n==================== COMPLETED SYNTAX ANALYSIS ====================")
    return parse_tree

def parse_expression(tokens, syntax_err_handler, del_index):
    if tokens[0][TYPE] in ("SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "MOD OF", "BIGGR OF", "SMALLR OF", "BOTH SAEM", "DIFFRINT"):
        operation = ["operation", tokens[0][TYPE]]
        del tokens[0]
        del_index[0] += 1
        left_expr = parse_expression(tokens, syntax_err_handler, del_index)
        if tokens[0][LEXEME] == "AN":
            del tokens[0]
            del_index[0] += 2
        else:
            return syntax_err_handler("Unexpected operation")
        right_expr = parse_expression(tokens, syntax_err_handler, del_index)
        operation.append(left_expr)
        operation.append(right_expr)
        return operation
    elif tokens[0][TYPE] in ("BOTH OF","EITHER OF","WON OF"):
        operation = ["boolop", tokens[0][TYPE]]
        del tokens[0]
        del_index[0] += 1
        left_expr = parse_expression(tokens, syntax_err_handler, del_index)
        if tokens[0][LEXEME] == "AN":
            del tokens[0]
            del_index[0] += 2
        else:
            return syntax_err_handler("Unexpected boolean operation")
        right_expr = parse_expression(tokens, syntax_err_handler, del_index)
        operation.append(left_expr)
        operation.append(right_expr)
        return operation
    elif tokens[0][TYPE] == "NOT":
        operation = ["boolop", tokens[0][TYPE]]
        del tokens[0]
        del_index[0] += 1
        unary_expr = parse_expression(tokens, syntax_err_handler, del_index)
        operation.append(unary_expr)
        return operation
    elif tokens[0][LEXEME] in ("literal", "varident", "typecast"):
        operand = tokens[0]
        del tokens[0]
        return operand
    else:
        print(tokens[0])
        return syntax_err_handler("Unexpected operation")
    
# def parse_boolop(tokens, syntax_err_handler, del_index):
#     if tokens[0][TYPE] in ("BOTH OF","EITHER OF","WON OF"):
#         operation = ["boolop", tokens[0][TYPE]]
#         del tokens[0]
#         del_index[0] += 1
#         left_expr = parse_boolop(tokens, syntax_err_handler, del_index)
#         if tokens[0][LEXEME] == "AN":
#             del tokens[0]
#             del_index[0] += 2
#         # else:
#         #     return syntax_err_handler("Unexpected boolean operation")
#         right_expr = parse_boolop(tokens, syntax_err_handler, del_index)
#         operation.append(left_expr)
#         operation.append(right_expr)
#         return operation
#     elif tokens[0][TYPE] == "NOT":
#         operation = ["boolop", tokens[0][TYPE]]
#         del tokens[0]
#         del_index[0] += 1
#         unary_expr = parse_boolop(tokens, syntax_err_handler, del_index)
#         operation.append(unary_expr)
#         return operation
#     elif tokens[0][LEXEME] in ("literal", "varident", "typecast"):
#         operand = tokens[0]
#         del tokens[0]
#         return operand
    # else:
    #     print(tokens[0])
    #     return syntax_err_handler("Unexpected boolean operation")