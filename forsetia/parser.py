"""
Parser for formal logic statements
"""

SYMBOLS = ["&", "|", ">", "<", "-"]
REPLACES = [["and", "&"], ["or", "|"], ["implies", ">"], ["iff", "<"],
            ["not", "-"]]


def clean_formula(formula):
    """
    Clean a given formula into a format we can use easily parse/use
    :param formula: A valid formal logic formula
    :return: A machine readable formula for parsing
    """
    formula = formula.replace(" ", "")
    for replace in REPLACES:
        formula = formula.replace(replace[0], replace[1])
    return formula


def get_main_symbol(formula):
    """
    Gets the primary symbol of a given formula
    :param formula: a formal logic formula
    :return: the main symbol in the formula (the most important
             outermost symbol)
    """
    formula = clean_formula(formula)
    symbol = ""
    symbol_para = 0
    current_para = 0
    for char in formula:
        if char == " ":
            continue
        elif char == "(":
            current_para += 1
        elif char == ")":
            current_para -= 1
        elif char in ["&", "|", ">", "<", "-"]:
            if symbol == "":
                symbol = char
                symbol_para = current_para
            elif current_para < symbol_para:
                symbol = char
                symbol_para = current_para
            elif current_para == symbol_para:
                found_i = SYMBOLS.index(symbol)
                new_i = SYMBOLS.index(char)
                if new_i < found_i:
                    symbol = char
                    symbol_para = current_para
            else:
                # found symbol is higher than current
                pass
        else:
            # Just a symbol
            pass
    return symbol
