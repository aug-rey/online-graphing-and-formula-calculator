from math import *
from json import loads, load, dumps, dump, decoder
from urllib3 import PoolManager

formulas, keys, values = None, None, None
online = False
default_selection_length = 30
graph_size = 50
half_graph = ceil(graph_size / 2)
zoom = 2.0
password = "" # api secret redacted
url = "" # url redacted too

def refresh(download=False):
    global keys, values, formulas, online
    
    if download:
        if online:
            try:
                formulas = loads(PoolManager().request("GET", url).data.decode("utf-8"))
                online = True
            except decoder.JSONDecodeError:
                online = False
                with open("formulas.json", "r") as f:
                    formulas = load(f)
        else:
            with open("formulas.json", "r") as f:
                formulas = load(f)
                
    else:
        if online:
            PoolManager().request("POST", url, headers={"Content-Type": "application/json", "password": password}, body=dumps(formulas))
        with open("formulas.json", "w") as f:
                dump(formulas, f)
    keys = list(formulas.keys())
    keys.sort()
    values = [formulas[i] for i in keys]

def cls():
    print("\033[H\033[2J", end="")

def selection(options, title="Please select an option"):
    string = ""
    selection_length = default_selection_length
    
    for i, v in enumerate(options):
        selection_length = max(selection_length, len(v) + 5 + len(str(i + 1)))
    for i, v in enumerate(options):
        string += "│" + f" [{i + 1}] {v}" + (" " * (selection_length - 4 - len(v) - len(str(i + 1)))) + "│\n"
    string = "┌" + title + "─" * (selection_length - len(title)) + "┐" + "\n│" + (" " * selection_length) + "│\n" + string + "│" + (" " * selection_length) + "│\n" + "└" + "─" * selection_length + "┘"
    
    while True:
        cls()
        n = input(string + "\n> ")
        try:
            n = int(n)
            if n >= 1 and n <= len(options):
                return n
        except ValueError:
            continue

def askall(questions):
    answers = []
    for question in questions:
        while True:
            answer = input(f"{question}: ")
            try:
                answers.append(float(answer))
                break
            except ValueError:
                continue
    return answers

def get_variables(formula):
    variables = [formula[i+1:formula[i:].find("]") + i] for i, v in enumerate(formula) if v == "[" and formula[i:].find("]") != -1]
    variables = [x for i, x in enumerate(variables) if x not in variables[:i]]
    return variables

def replace(formula, variables, replacements):
    for i, v in enumerate(variables):
        formula = formula.replace(f"[{v}]", str(replacements[i]))
    return formula.replace("^", "**")

def menu():
    global formulas, zoom, graph_size, half_graph
    while True:
        user_selection = selection(["create new formula", "edit existing formula", "delete formula", "help writing formulas", "graphing calculator zoom", "graphing calculator size", "back to calculator"], title="Menu")
        if user_selection == 1:
            name = input("What would you like to name your formula?: ")
            value = input("What should your formula be?: ")
            formulas[name] = value
            refresh()
        elif user_selection == 2:
            while True:
                formula = selection(keys + ["back"], title = "Choose a formula to edit")
                if formula != len(formulas) + 1:
                    option = selection(["change title", "change formula", "back"])
                    if option == 1:
                        formulas[input("Enter the new name for the formula\n> ")] = values[formula - 1]
                        del formulas[keys[formula - 1]]
                    elif option == 2:
                        formulas[keys[formula - 1]] = input(f"Old formula: {values[formula - 1]}\nEnter the new formula\n> ")
                    else:
                        continue
                    refresh()
                break
        elif user_selection == 3:
            formula = selection(keys + ["back"], title = "Choose a formula to delete")
            if formula != len(formulas) + 1:
                del formulas[keys[formula - 1]]
                refresh()
        elif user_selection == 4:
            cls()
            input("""-- formulas help page --
            
math operations:
    math operations work just like how you would expect, including pemdas.
    ex: 3 * (9 + 2)^8 - 1
variables:
    all variables will be in square brackets and variables with the same name will be filled in with the same value.
    ex: ([number 1]^2 - [number 2]) - [number 1] / [number 2]
math symbols:
    math variables from the python math library like pi can be used like so:
        pi * [radius]^2 - e
python code:
    any code that is valid in python can be used in the formula.
    ex: int(sqrt([number]))
        
press enter to continue.""")
        elif user_selection == 5:
            while True:
                try:
                    zoom = float(input(f"current zoom: {zoom}\nenter the graphing calculator zoom level: "))
                    break
                except ValueError:
                    continue
        elif user_selection == 6:
            while True:
                try:
                    graph_size = int(input(f"current size: {graph_size}\nenter the graphing calculator size: "))
                    half_graph = ceil(graph_size / 2)
                    break
                except ValueError:
                    continue
        else:
            break

def calculator():
    while True:
        user_selection = selection(["-- menu --", "-- graphing calculator --"] + keys, title="Formula Calculator by Augie")
        if user_selection == 1:
            menu()
            continue
        elif user_selection == 2:
            graphing()
            continue
        formula = values[user_selection - 3]
        variables = get_variables(formula)
        replacements = askall(variables)
        try:
            answer = eval(replace(formula, variables, replacements))
            input(f"Answer: {answer}\npress enter to continue.")
        except Exception as e:
            input(f"There was an error excecuting the formula: {e}.\nPlease consult the help page if you need help writing formulas.\npress enter to continue.")

def better_round(number):
    if number % 1 >= .5:
        return ceil(number)
    else:
        return floor(number)

def draw_graph(matrix):
    for index, i in enumerate(reversed(matrix)):
        for index2, j in enumerate(i):
            if j != 0:
                print("# ", end="")
            elif index == half_graph - 1 and index2 == len(matrix) - 1:
                print("- ", end="")
            elif index == half_graph - 1:
                print("--", end="")
            elif index2 == half_graph - 1:
                print("| ", end="")
            else:
                print(". ", end="")
        print(" ")

def generate_matrix(equation, matrix=None):
    if matrix == None:
        matrix = []
        for i in range(graph_size):
            matrix.append([0] * graph_size)

    equation = equation.replace("x", "([x])")
    variables = get_variables(equation)
    
    for i in range(-half_graph, half_graph + 1):
        try:
            y = better_round(eval(replace(equation, variables, [i / zoom])) * zoom)
            if graph_size % 2 == 0:
                y += 1
            if y + half_graph - 1 >= 0 and y + half_graph - 1 < graph_size and i + half_graph - 1 >= 0:
                matrix[y + half_graph - 1][i + half_graph - 1] = 1
        except Exception:
            continue
        
    return matrix

def graph_equations(equations):
    final_matrix = None
    for equation in equations:
        final_matrix = generate_matrix(equation, matrix=final_matrix)
    return final_matrix
        
def get_equations():
    equations = []
    print("type a blank equation and press enter to quit")
    while True:
        user = input("y = ")
        if user != "":
            equations.append(user)
            continue
        break
    return equations

def root(x, n):
    if x >= 0 or n % 2 == 0:
        return x ** (1/n)
    else:
        return -(-x) ** (1/n)

def graphing():
    cls()
    equations = get_equations()
    if equations == []:
        return
    matrix = graph_equations(equations)
    draw_graph(matrix)
    input("press enter to continue.")

if __name__ == "__main__":
    refresh(download=True)
    calculator()
