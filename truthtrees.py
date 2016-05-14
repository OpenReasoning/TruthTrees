# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import argparse
from forseti.formula import Formula, Predicate, Symbol, Not, And, Or, If, Iff
import forseti.parser
from six import string_types


def pretty_print(formula):
    """

    :param formula:
    :return:
    """
    if isinstance(formula, Symbol) or isinstance(formula, Predicate):
        text = str(formula)
    elif isinstance(formula, Not):
        text = "¬" + pretty_print(formula.args[0])
    else:
        temp = []
        for arg in formula.args:
            temp.append(pretty_print(arg))
        if isinstance(formula, And):
            text = " ∧ ".join(temp)
        elif isinstance(formula, Or):
            text = " ∨ ".join(temp)
        elif isinstance(formula, If):
            text = " → ".join(temp)
        elif isinstance(formula, Iff):
            text = " ↔ ".join(temp)
        else:
            raise TypeError("Invalid Formula Type: " + str(type(formula)))
        text = "(" + text + ")"
    return text.strip()


class TreeNode(object):
    def __init__(self):
        self.formulas = []
        self.parent = None
        self.children = []
        self.closed = False
        self.number = None

    def add_formula(self, formula, count):
        if self.closed:
            return False
        self.formulas.append(formula)
        to_check = Not(formula.formula) if not isinstance(formula.formula, Not) else formula.formula.args[0]
        if self.has_formula(to_check):
            self.closed = True
            self.number = count
            return True
        return False

    def has_formula(self, check_formula):
        for formula in self.formulas:
            if formula.formula == check_formula:
                return True
        if self.parent is not None:
            return self.parent.has_formula(check_formula)
        return False

    def is_closed(self):
        if len(self.children) == 0:
            return self.closed
        closed_children = []
        for child in self.children:
            closed_children.append(child.is_closed())
        return not (False in closed_children)

    def can_expand(self):
        if self.closed:
            return False
        for formula in self.formulas:
            if formula.broken is False:
                return True
        expand = True
        for child in self.children:
            expand = expand and child.can_expand()
        return expand

    def add_children(self):
        """

        :return: Two lists one containing all new left nodes in the tree and one containing all new right nodes
        :rtype: List[TreeNode], List[TreeNode]
        """
        if self.closed:
            return [[], []]
        elif len(self.children) == 0:
            for i in range(2):
                node = TreeNode()
                node.parent = self
                self.children.append(node)
            return [self.children[0]], [self.children[1]]
        else:
            left_nodes = []
            right_nodes = []
            for child in self.children:
                left, right = child.add_children()
                left_nodes.extend(left)
                right_nodes.extend(right)
            return left_nodes, right_nodes

    def get_children(self):
        if self.closed:
            return []
        elif len(self.children) == 0:
            return [self]
        else:
            children = []
            for child in self.children:
                children.extend(child.get_children())
            return children


class TreeFormula(object):
    def __init__(self, formula):
        """

        :param formula:
        :type formula: Formula
        """
        self.formula = formula
        self.broken = False
        self.number = None

    def can_break(self):
        return not (isinstance(self.formula, Symbol) or
                    (isinstance(self.formula, Not) and isinstance(self.formula.args[0], Symbol)))

    def __repr__(self):
        return repr(self.formula)


class TruthTree(object):
    def __init__(self, formulas, goal):
        self.root = TreeNode()
        for formula in formulas:
            self.root.formulas.append(TreeFormula(formula))
        self.root.formulas.append(TreeFormula(Not(goal)))
        self.count = 1
        self.expand_tree()

    def is_done(self):
        return self.root.is_closed() or not self.root.can_expand()

    def expand_tree(self):
        while not self.is_done():
            self.expand_node(self.root)

    def expand_node(self, node):
        if node.is_closed():
            return False

        for formula in node.formulas:
            assert(isinstance(formula, TreeFormula))
            if not formula.broken and formula.can_break():
                self.expand_formula(formula, node)
                return True

        for child in node.children:
            if self.expand_node(child):
                return True

        return False

    def add_formula(self, node, formula):
        """

        :param node:
        :type node: TreeNode
        :param formula:
        :type formula: Formula
        :return:
        """
        if node.add_formula(TreeFormula(formula), self.count):
            self.count += 1
            return True
        return False

    def expand_formula(self, tree_formula, tree_node):
        tree_formula.number = self.count
        tree_formula.broken = True
        self.count += 1
        formula = tree_formula.formula
        if isinstance(formula, Not):
            if isinstance(formula.args[0], Not):
                children_nodes = tree_node.get_children()
                for child_node in children_nodes:
                    self.add_formula(child_node, formula.args[0].args[0])
            elif isinstance(formula.args[0], And):
                left_nodes, right_nodes = tree_node.add_children()
                for left_node in left_nodes:
                    self.add_formula(left_node, Not(formula.args[0].args[0]))
                for right_node in right_nodes:
                    self.add_formula(right_node, Not(formula.args[0].args[1]))
            elif isinstance(formula.args[0], Or):
                children_nodes = tree_node.get_children()
                for child_node in children_nodes:
                    for i in range(2):
                        if self.add_formula(child_node, Not(formula.args[0].args[i])):
                            break
            elif isinstance(formula.args[0], If):
                children_nodes = tree_node.get_children()
                for child_node in children_nodes:
                    if self.add_formula(child_node, formula.args[0].args[0]):
                        continue
                    self.add_formula(child_node, Not(formula.args[0].args[1]))
            elif isinstance(formula.args[0], Iff):
                left_nodes, right_nodes = tree_node.add_children()
                for left_node in left_nodes:
                    if self.add_formula(left_node, formula.args[0].args[0]):
                        continue
                    self.add_formula(left_node, Not(Formula.args[0].args[1]))
                for right_node in right_nodes:
                    if self.add_formula(right_node, Not(formula.args[0].args[0])):
                        continue
                    self.add_formula(right_node, formula.args[0].args[1])
        elif isinstance(formula, And):
            children_nodes = tree_node.get_children()
            for child_node in children_nodes:
                for i in range(2):
                    if self.add_formula(child_node, formula.args[i]):
                        break
        elif isinstance(formula, Or):
            left_nodes, right_nodes = tree_node.add_children()
            for left_node in left_nodes:
                self.add_formula(left_node, formula.args[0])
            for right_node in right_nodes:
                self.add_formula(right_node, formula.args[1])
        elif isinstance(formula, If):
            left_nodes, right_nodes = tree_node.add_children()
            for left_node in left_nodes:
                self.add_formula(left_node, Not(formula.args[0]))
            for right_node in right_nodes:
                self.add_formula(right_node, formula.args[1])
        elif isinstance(formula, Iff):
            left_nodes, right_nodes = tree_node.add_children()
            for left_node in left_nodes:
                for i in range(2):
                    if self.add_formula(left_node, formula.args[i]):
                        break
            for right_node in right_nodes:
                for i in range(2):
                    if self.add_formula(right_node, Not(formula.args[i])):
                        break


def runner(formulas, goal):
    """

    :param formulas:
    :type formulas: List[string_types]
    :param goal:
    :type goal: string_types
    :return:
    """

    if isinstance(formulas, string_types):
        formulas = [formulas]

    if not isinstance(goal, string_types):
        raise TypeError("Expected str for goal, got " + str(type(goal)))

    parsed_formulas = []
    for formula in formulas:
        formula = formula.strip()
        if len(formula) == 0:
            continue
        parsed_formulas.append(forseti.parser.parse(formula))

    goal = forseti.parser.parse(goal)
    return TruthTree(parsed_formulas, goal)


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(description="Generate Truth Table for a logical formula")
    PARSER.add_argument('formulas', metavar='formula', type=str, nargs="+", help='Logical formula')
    PARSER.add_argument('goal', metavar='goal', type=str, help='Goal Formula')
    PARSER_ARGS = PARSER.parse_args()
    SHORT_TRUTH_TABLE = runner(PARSER_ARGS.formulas, PARSER_ARGS.goal)
    pass
