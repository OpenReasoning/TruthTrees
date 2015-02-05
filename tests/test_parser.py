"""
Tester for the logic parser
"""
from forseti import parser


def test_get_main_symbol():
    """
    Test that we can get the main symbol out of a variety of formulas
    """
    formulas = [["A > (B & C)", ">"], ["C < B", "<"], ["- C", "-"],
                ["- (- A)", "-"], ["(-(A & B) > (C < D))", ">"],
                ["((A & B) | D)", "|"]]

    for formula in formulas:
        symbol = parser.get_main_symbol(formula[0])
        assert formula[1] == symbol


def test_clean_formula():
    """
    Test that formulas are properly cleaned and parsed to something
    machine readable
    """
    formula = "((A implies B) and not (C or D)) iff E"
    expected = "((A>B)&-(C|D))<E"
    actual = parser.clean_formula(formula)
    assert expected == actual
