'''
1) Variable Declaration/Initialization /
2) VISIBLE /
3) ARITH OPS /
4) INPUT /
5) CONCAT /
'''

import customtkinter as ctk
import re

SEMANTIC_ERR = 2

symbol_table = {}

def semantic_analysis(symbols, parse_tree, print_console, reset_console, semantic_err_handler):
    global symbol_table 
    symbol_table = {}
    print("\n==================== PERFORMING SEMANTIC ANALYSIS ====================\n")

    # handle variable declarations
    for token in parse_tree:
        if token[0] == 'vardecport':
            try:
                process_vardecport(token)
            except Exception as e:
                reset_console()
                return semantic_err_handler(f"{e}")
            break

    # print_symbol_table()

    # TODO Functions

    # statements
    for token in parse_tree:
        if token[0] == 'statements':
            try:
                process_statements(token[1:], print_console)
            except Exception as e:
                reset_console()
                return semantic_err_handler(f"{e}")
            break

    # for token in parse_tree:
    #     print(token)

    # append to symbols
    for ident,sym_data in symbol_table.items():
         symbols.append([ident, sym_data['value']])

def process_statements(statements, print_console):
    for statement in statements:
        print(statement) 
        if statement[0] == 'print':
            print_str = []
            add_space = True
            if statement[1][0] == "concat":
                statement = statement[1]
                add_space = False
            for i in range(1,len(statement)):
                if statement[i][0] == 'literal':
                    print_type, print_val = typecast((statement[i][1], re.sub(r'\"', '', statement[i][2])), "YARN Literal")
                    set_or_update_it(print_type, print_val)
                    print_str.append(symbol_table["IT"]['value'])
                elif statement[i][0] == 'varident':
                    check_variable(statement[i][1])
                    print_type, print_val = typecast((symbol_table[statement[i][1]]['type'],symbol_table[statement[i][1]]['value']), "YARN Literal")
                    set_or_update_it(print_type, print_val)
                    print_str.append(symbol_table["IT"]['value'])
                    # print_console(symbol_table[statement[i][1]]['value'])
                elif statement[i][0] == 'expr':
                    print_type, print_val = evaluate_expr(statement[i])
                    print_type, print_val = typecast((print_type, print_val), "YARN Literal")
                    set_or_update_it(print_type, print_val)
                    print_str.append(symbol_table["IT"]['value'])
            if add_space:
                print_console(" ".join(print_str))
            else:
                print_console("".join(print_str))
        elif statement[0] == 'input':
            dialog = ctk.CTkInputDialog(text="Enter input:", title="Input")
            check_variable(statement[1][1])
            input_type, input_val = typecast(('YARN Literal',dialog.get_input()), 'YARN Literal')
            update_variable(statement[1][1], input_type, input_val)
            set_or_update_it(input_type, input_val)
        elif statement[0] == 'varassign':
            var = statement[1][1]
            new_val = statement[2]  # literal, varident, typecast, concat, expr
            check_variable(var)
            if new_val[0] == 'literal':
                var_type, var_val = typecast((new_val[1], new_val[2]), new_val[1])
                set_or_update_it(var_type, var_val)
                update_variable(var, var_type, var_val)
            elif new_val[0] == 'varident':
                check_variable(new_val[1])
                set_or_update_it(symbol_table[new_val[1]]['type'], symbol_table[new_val[1]]['value'])
                update_variable(var, symbol_table[new_val[1]]['type'], symbol_table[new_val[1]]['value'])
            elif new_val[0] == 'expr':
                var_type, var_val = evaluate_expr(new_val)
                set_or_update_it(var_type, var_val)
                update_variable(var_type, var_val)
            elif new_val[0] == 'concat':
                concat_str = []
                for i in range(1,len(new_val)):
                    if new_val[i][0] == 'literal':
                        concat_type, concat_val = typecast((new_val[i][1], re.sub(r'\"', '', new_val[i][2])), "YARN Literal")
                        set_or_update_it(concat_type, concat_val)
                        concat_str.append(symbol_table["IT"]['value'])
                    elif new_val[i][0] == 'varident':
                        check_variable(new_val[i][1])
                        concat_type, concat_val = typecast((symbol_table[new_val[i][1]]['type'],symbol_table[new_val[i][1]]['value']), "YARN Literal")
                        set_or_update_it(concat_type, concat_val)
                        concat_str.append(symbol_table["IT"]['value'])
                    elif new_val[i][0] == 'expr':
                        concat_type, concat_val = evaluate_expr(new_val[i])
                        concat_type, concat_val = typecast((concat_type, concat_val), "YARN Literal")
                        set_or_update_it(concat_type, concat_val)
                        concat_str.append(symbol_table["IT"]['value'])
                set_or_update_it("YARN Literal", "".join(concat_str))
                update_variable(var, "YARN Literal", "".join(concat_str))
            elif new_val[0] == 'typecast':
                new_var_type, new_var_val = typecast((symbol_table[new_val[1][1]]['type'],symbol_table[new_val[1][1]]['value']),new_val[2][2])
                set_or_update_it(new_var_type, new_var_val)
                update_variable(new_val[1][1], new_var_type, new_var_val)
        elif statement[0] == 'typecast':
            new_var_type, new_var_val = typecast((symbol_table[statement[1][1]]['type'],symbol_table[statement[1][1]]['value']),statement[2][2])
            set_or_update_it(new_var_type, new_var_val)
            update_variable(statement[1][1], new_var_type, new_var_val)

def process_vardecport(vardecport):
    for var in vardecport[1:]:
        # get name
        var_name = None
        if var[0] == 'vardec':
            var_name = var[1][1]
        elif var[0] == 'varinit':
            var_name = var[1][1][1]

        # get val & type
        var_val = ''
        var_type = 'NOOB Literal'
        if var[0] == 'varinit':
            if var[2][0] == 'literal':
                var_type = var[2][1]
                var_val = re.sub(r'\"', '', var[2][2])
            elif var[2][0] == 'varident':
                varident_val = var[2][1]
                try:
                    check_variable(varident_val)
                except:
                    raise Exception(f"Variable '{varident_val}' used before declaration.")
                var_val = symbol_table[varident_val]['value']
                var_type = symbol_table[varident_val]['type']
            elif var[2][0] == 'expr':
                var_type, var_val = evaluate_expr(var[2])
            set_or_update_it(var_type, var_val)

        add_variable(var_name, var_type, var_val)

def evaluate_expr(expr):
    if expr[0] == "varident":
        check_variable(expr[1])
        return [symbol_table[expr[1]]['type'], symbol_table[expr[1]]['value']]
    elif expr[0] == "literal":
        return expr[1:]
    elif expr[0] == "expr":
        return evaluate_expr(expr[1])
    elif expr[0] == "operation":
        op1 = evaluate_expr(expr[2])
        op2 = evaluate_expr(expr[3])

        if expr[1] in ["SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "MOD OF", "BIGGR OF", "SMALLR OF"]:
            # at least one numbar, result is numbar
            if op1[0] == "NUMBAR Literal" or op1[0] == "NUMBAR Literal":
                op1 = typecast(op1, "NUMBAR Literal")
                op2 = typecast(op2, "NUMBAR Literal")
            else:
                op1 = typecast(op1, "NUMBR Literal")
                op2 = typecast(op2, "NUMBR Literal")

            # Perform the operation
            if expr[1] == "SUM OF":
                return op1[0], op1[1] + op2[1]
            elif expr[1] == "DIFF OF":
                return op1[0], op1[1] - op2[1]
            elif expr[1] == "PRODUKT OF":
                return op1[0], op1[1] * op2[1]
            elif expr[1] == "QUOSHUNT OF":
                if op2[1] == 0:
                    raise Exception("Runtime Error: Division by zero.")
                if op1[0] == "NUMBAR Literal" or op1[0] == "NUMBAR Literal":
                    return op1[0], op1[1] / op2[1]
                else:
                    return op1[0], op1[1] // op2[1]
            elif expr[1] == "MOD OF":
                if op2[1] == 0:
                    raise Exception("Runtime Error: Division by zero.")
                else:
                    return op1[0], op1[1] % op2[1]
            elif expr[1] == "BIGGR OF":
                return op1[0], max(op1[1], op2[1])
            elif expr[1] == "SMALLR OF":
                return op1[0], min(op1[1], op2[1])
                
    else:
        raise ValueError("Unknown operation")

def typecast(value, target_type):
    source_type, source_value = value
    
    # Handle typecasting
    if source_type == "NOOB Literal" or source_type == "NOOB":
        if target_type == "TROOF Literal" or target_type == "TROOF":
            return ("TROOF Literal", "FAIL")    # TODO will become FAIL or WIN?
        elif target_type == "NUMBR Literal" or target_type == "NUMBR":
            return ("NUMBR Literal", 0)
        elif target_type == "NUMBAR Literal" or target_type == "NUMBAR":
            return ("NUMBAR Literal", 0.0)
        elif target_type == "YARN Literal" or target_type == "YARN":
            return ("YARN Literal", "")
        elif target_type == "NOOB Literal" or target_type == "NOOB":
            return ("NOOB Literal", "")
        else:
            raise Exception(f"Invalid typecast: NOOB Literal to {target_type}")

    elif source_type == "TROOF Literal" or source_type == "TROOF":
        if target_type == "NUMBR Literal" or target_type == "NUMBR":
            return ("NUMBR Literal", 1 if source_value == "WIN" else 0)
        elif target_type == "NUMBAR Literal" or target_type == "NUMBAR":
            return ("NUMBAR Literal", 1.0 if source_value == "WIN" else 0.0)
        elif target_type == "YARN Literal" or target_type == "YARN":
            return ("YARN Literal", source_value)
        elif target_type == "TROOF Literal" or target_type == "TROOF":
            return ("TROOF Literal", "WIN" if source_value == "WIN" else "FAIL")
        else:
            raise Exception(f"Invalid typecast: TROOF Literal to {target_type}")

    elif source_type == "NUMBR Literal" or source_type == "NUMBR":
        if target_type == "NUMBAR Literal" or target_type == "NUMBAR":
            return ("NUMBAR Literal", float(source_value))
        elif target_type == "YARN Literal" or target_type == "YARN":
            return ("YARN Literal", str(source_value))
        elif target_type == "NUMBR Literal" or target_type == "NUMBR":
            return ("NUMBR Literal", int(source_value))
        elif (target_type == "TROOF Literal" or target_type == "TROOF"):
            return ("TROOF Literal", "FAIL" if int(source_value) == 0 else "WIN")
        else:
            raise Exception(f"Invalid typecast: NUMBR Literal to {target_type}")

    elif source_type == "NUMBAR Literal" or source_type == "NUMBAR":
        if target_type == "NUMBR Literal" or target_type == "NUMBR":
            return ("NUMBR Literal", int(source_value))  # Truncate decimal part
        elif target_type == "YARN Literal" or target_type == "YARN":
            return ("YARN Literal", f"{source_value}")
        elif source_type == "NUMBAR Literal":
            return ("NUMBAR Literal", float(source_value))
        elif (target_type == "TROOF Literal" or target_type == "TROOF"):
            return ("TROOF Literal", "FAIL" if source_value == 0 else "WIN")
        else:
            raise Exception(f"Invalid typecast: NUMBAR Literal to {target_type}")

    elif source_type == "YARN Literal" or source_type == "YARN":
        if target_type == "NUMBR Literal" or target_type == "NUMBR":
            try:
                return ("NUMBR Literal", int(re.sub(r'\"', '', source_value)))
            except ValueError:
                raise Exception(f"Invalid typecast: YARN Literal '{source_value}' cannot be converted to NUMBR Literal")
        elif target_type == "NUMBAR Literal" or target_type == "NUMBAR":
            try:
                return ("NUMBAR Literal", float(re.sub(r'\"', '', source_value)))
            except ValueError:
                raise Exception(f"Invalid typecast: YARN Literal '{source_value}' cannot be converted to NUMBAR Literal")
        elif (target_type == "TROOF Literal" or target_type == "TROOF"):
            return ("TROOF Literal", "FAIL" if source_value == "" or source_value == None else "WIN")
        elif target_type == "YARN Literal" or target_type == "YARN":
            return ("YARN Literal", f"{source_value}")
        else:
            raise Exception(f"Invalid typecast: YARN Literal to {target_type}")

    else:
        raise Exception(f"Unknown source type: {source_type}")

def set_or_update_it(it_type, it_value):
    if 'IT' in symbol_table:
        symbol_table['IT']['type'] = it_type
        symbol_table['IT']['value'] = it_value
    else:
        symbol_table['IT'] = {'type': it_type, 'value': it_value}

def add_variable(name, var_type, value=None):
    if name in symbol_table:
        raise Exception(f"Variable '{name}' already declared.")
    symbol_table[name] = {'type': var_type, 'value': value}

def update_variable(name, var_type=None, value=None):
    if name not in symbol_table:
        raise Exception(f"Variable '{name}' not already declared.")
    if var_type != None:
        symbol_table[name]['type'] = var_type
    if value != None:
        symbol_table[name]['value'] = value

def check_variable(name):
    if name not in symbol_table:
        raise Exception(f"Variable '{name}' used before declaration.")

# TODO COMMENT! FOR TESTING PURPOSES ONLY!
def print_symbol_table():
    for k,v in symbol_table.items():
        print(f'{k} {v}')