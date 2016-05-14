# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from flask import Flask, Markup, render_template, request
import truthtrees

CLOSED_STRING = "<span style='color: red;'>X</span>"
FLASK_APP = Flask(__name__)


@FLASK_APP.route("/")
def index_page():
    return render_template('index.html')


@FLASK_APP.route("/submit", methods=['POST'])
def generate_tree():
    formulas = request.form.getlist('formula[]')
    goal = request.form['goal']
    i = 0
    while i < len(formulas):
        formulas[i] = str(formulas[i]).strip()
        if len(formulas[i]) == 0:
            del formulas[i]
            i -= 1
        i += 1
    form = Markup(render_template('form.html', formulas=formulas, goal=goal))

    try:
        tree = truthtrees.runner(formulas, goal)
    except (SyntaxError, TypeError) as exception:
        return render_template('error.html', error=str(exception), form=form)

    tree_render = render_node(tree.root)

    return render_template('tree.html', tree=tree_render, closed=tree.root.is_closed())


def render_node(node):
    children = []
    for child in node.children:
        children.append(render_node(child))

    formulas = []
    for formula in node.formulas:
        formulas.append(truthtrees.pretty_print(formula.formula))
    if node.closed:
        formulas.append(Markup(CLOSED_STRING))

    return Markup(render_template('node.html', formulas=formulas, children=children))


if __name__ == '__main__':
    FLASK_APP.debug = True
    FLASK_APP.run()