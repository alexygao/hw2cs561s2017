# prefix 1=positive -1=negative
class Literal:
    prefix = 1
    guest = 0
    table = 0

    def __init__(self, p, g, t):
        self.prefix = p
        self.guest = g
        self.table = t
        pass


class Clause:
    literals = []

    def __init__(self, ls):
        self.literals = ls
        pass


# read from input file
input_file = open('input.txt', 'r')  # initialize the number of guests and tables
new_line = input_file.readline()
total_guests = int(new_line.split(' ')[0])
total_tables = int(new_line.split(' ')[1])

# initialize kb
kb = []
for i in range(total_guests):
    # a guest must be at some table
    guest_at_some_table_clause = Clause([])
    for j in range(total_tables):
        literal = Literal(1, i, j)
        # a guest must be at some table
        guest_at_some_table_clause.literals.append(literal)
        literal = Literal(-1, i, j)
        for k in range(j + 1, total_tables):
            # a guest can only be at one table = cannot be at two tables at the same time
            literal2 = Literal(-1, i, k)
            guest_at_one_table_clause = Clause([literal, literal2])
            kb.append(guest_at_one_table_clause)
    kb.append(guest_at_some_table_clause)
# read relationships from input file
new_line = input_file.readline()
while new_line != '':
    a = int(new_line.split(' ')[0]) - 1
    b = int(new_line.split(' ')[1]) - 1
    # friends must be at the same table
    relationship = len(new_line.split(' ')[0]) + len(new_line.split(' ')[1]) + 2
    if new_line[relationship] == 'F':
        for i in range(total_tables):
            guest1_literal = Literal(-1, a, i)
            guest2_literal = Literal(1, b, i)
            clause = Clause([guest1_literal, guest2_literal])
            kb.append(clause)
            guest1_literal = Literal(1, a, i)
            guest2_literal = Literal(-1, b, i)
            clause = Clause([guest1_literal, guest2_literal])
            kb.append(clause)
    # enemies cannot be at the same table
    if new_line[relationship] == 'E':
        for i in range(total_tables):
            guest1_literal = Literal(-1, a, i)
            guest2_literal = Literal(-1, b, i)
            clause = Clause([guest1_literal, guest2_literal])
            kb.append(clause)
    new_line = input_file.readline()
# initialize assignment
model = [[]] * total_guests
for i in range(total_guests):
    model[i] = [0] * total_tables


# doesn't care about the positiveness or negativeness of the literal
def is_same_symbol(symbol1, symbol2):
    if symbol1.guest == symbol2.guest and symbol1.table == symbol2.table:
        return True
    else:
        return False


# return the set of symbols in the sentence
def get_symbols_from_sentence(s):
    symbols = []
    for clause in s:
        for literal in clause.literals:
            already_exists = False
            for exist in symbols:
                if is_same_symbol(exist, literal):
                    already_exists = True
                    break
            if not already_exists:
                symbols.append(literal)
    return symbols


# 0=undecided 1=True -1=False
def literal_status_in_model(l, m):
    if m[l.guest][l.table] == 0:
        return 0
    elif l.prefix == m[l.guest][l.table]:
        return 1
    else:
        return -1


# for CNF, in a clause, if one literal is True then the clause is True
# 0=undecided 1=True -1=False
def is_clause_true(cl, m):
    exist_undecided = False
    for l in cl.literals:
        if literal_status_in_model(l, m) == 1:
            return 1
        if literal_status_in_model(l, m) == 0:
            exist_undecided = True
    if exist_undecided:
        return 0
    else:
        return -1


# check if every clauses is true in the given model
def every_clause_is_true(cls, m):
    for cl in cls:
        if is_clause_true(cl, m) != 1:
            return False
    return True


# check if exist some clause is false in the given model
def some_clause_is_false(cls, m):
    for cl in cls:
        if is_clause_true(cl, m) == -1:
            return True
    return False


# return positive symbols for a given clause
def get_positive_symbols(cl):
    positive = []
    for l in cl.literals:
        if l.prefix == 1:
            positive.append(l)
    return positive


# return negative symbols for a given clause
def get_negative_symbols(cl):
    negative = []
    for l in cl.literals:
        if l.prefix == -1:
            negative.append(l)
    return negative


# check if a set of symbols contains one particular symbol
def contain_symbol(sbls, sbl):
    for s in sbls:
        if is_same_symbol(s, sbl):
            return True
    return False


# delete every symbol that is equal to l from clause
def delete_literal_from_clause(cl, l):
    length = len(cl)
    i = 0
    while i < length:
        if is_same_symbol(cl[i], l):
            del cl[i]
            length -= 1
        else:
            i += 1
    return cl


# get pure symbol set
def get_pure_symbols(sbls, cls, m):
    result = []
    candidate_pure_positive_symbol = []
    candidate_pure_negative_symbol = []
    for cl in cls:
        if is_clause_true(cl, m) == 1:
            continue
        positive_sbls = get_positive_symbols(cl)
        negative_sbls = get_negative_symbols(cl)
        for p in positive_sbls:
            if contain_symbol(sbls, p) and not contain_symbol(candidate_pure_positive_symbol, p):
                candidate_pure_positive_symbol.append(p)
        for n in negative_sbls:
            if contain_symbol(sbls, n) and not contain_symbol(candidate_pure_negative_symbol, n):
                candidate_pure_negative_symbol.append(n)
    for s in sbls:
        if contain_symbol(candidate_pure_positive_symbol, s) and contain_symbol(candidate_pure_negative_symbol, s):
            candidate_pure_positive_symbol = delete_literal_from_clause(candidate_pure_positive_symbol, s)
            candidate_pure_negative_symbol = delete_literal_from_clause(candidate_pure_negative_symbol, s)
    for p in candidate_pure_positive_symbol:
        result.append(Literal(1, p.guest, p.table))
    for n in candidate_pure_negative_symbol:
        result.append(Literal(-1, n.guest, n.table))
    return result


# check whether a clause is a unit clause: only have one literal
def is_unit_clause(cl):
    if len(cl.literals) == 1:
        return True
    else:
        return False


# get unit clause set :symbols and their prefix are their values
def get_unit_clause(cls, m):
    result = []
    for cl in cls:
        if is_clause_true(cl, m) == 0:
            unassigned = Literal(0, -1, -1)
            # traditional definition of unit clause
            if is_unit_clause(cl):
                unassigned = cl.literals[0]
            # unit clause in DPLL context = has a single unassigned literal
            else:
                for l in cl.literals:
                    if literal_status_in_model(l, m) == 0:
                        if is_same_symbol(unassigned, Literal(0, -1, -1)):
                            unassigned = l
                        # more than one unassigned literal
                        else:
                            unassigned = Literal(0, -1, -1)
                            break
            if not is_same_symbol(unassigned, Literal(0, -1, -1)):
                result.append(unassigned)
    return result


# super set of symbols minus subset of symbols
def minus(super, sub):
    for sub_sbl in sub:
        length = len(super)
        i = 0
        while i < length:
            if is_same_symbol(super[i], sub_sbl):
                del super[i]

                length -= 1
            else:
                i += 1
    return super


# update model by assigning values to some symbol
def model_union(m, sbls):
    for s in sbls:
        m[s.guest][s.table] = s.prefix
    return m


def dpll(cls, sbls, m):
    # if every clause is true in this partial model, then terminate
    if every_clause_is_true(cls, m):
        return True
    # if exist some clause is false in this partial model, then terminate
    if some_clause_is_false(cls, m):
        return False
    # pure symbol rule
    pure_symbols = get_pure_symbols(sbls, cls, m)
    if len(pure_symbols) > 0:
        return dpll(cls, minus(sbls, pure_symbols), model_union(m, pure_symbols))
    # unit clause rule
    unit_clause_symbols = get_unit_clause(cls, m)
    if len(unit_clause_symbols) > 0:
        return dpll(cls, minus(sbls, unit_clause_symbols), model_union(m, unit_clause_symbols))
    s = [sbls[0]]
    sn = [Literal(0 - sbls[0].prefix, sbls[0].guest, sbls[0].table)]
    return dpll(cls, minus(sbls, s), model_union(m, s)) or dpll(cls, minus(sbls, s), model_union(m, sn))
