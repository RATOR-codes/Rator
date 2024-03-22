import numpy as np
import javalang
from javalang.ast import Node
from anytree import AnyNode
import time
import os
from multiprocessing import Pool
from functools import partial


nodetypedict = {'MethodDeclaration': 0, 'Modifier': 1, 'FormalParameter': 2, 'ReferenceType': 3, 'BasicType': 4,
     'LocalVariableDeclaration': 5, 'VariableDeclarator': 6, 'MemberReference': 7, 'ArraySelector': 8, 'Literal': 9,
     'BinaryOperation': 10, 'TernaryExpression': 11, 'IfStatement': 12, 'BlockStatement': 13, 'StatementExpression': 14,
     'Assignment': 15, 'MethodInvocation': 16, 'Cast': 17, 'ForStatement': 18, 'ForControl': 19,
     'VariableDeclaration': 20, 'TryStatement': 21, 'ClassCreator': 22, 'CatchClause': 23, 'CatchClauseParameter': 24,
     'ThrowStatement': 25, 'WhileStatement': 26, 'ArrayInitializer': 27, 'ReturnStatement': 28, 'Annotation': 29,
     'SwitchStatement': 30, 'SwitchStatementCase': 31, 'ArrayCreator': 32, 'This': 33, 'ConstructorDeclaration': 34,
     'TypeArgument': 35, 'EnhancedForControl': 36, 'SuperMethodInvocation': 37, 'SynchronizedStatement': 38,
     'DoStatement': 39, 'InnerClassCreator': 40, 'ExplicitConstructorInvocation': 41, 'BreakStatement': 42,
     'ClassReference': 43, 'SuperConstructorInvocation': 44, 'ElementValuePair': 45, 'AssertStatement': 46,
     'ElementArrayValue': 47, 'TypeParameter': 48, 'FieldDeclaration': 49, 'SuperMemberReference': 50,
     'ContinueStatement': 51, 'ClassDeclaration': 52, 'TryResource': 53, 'MethodReference': 54,
     'LambdaExpression': 55, 'InferredFormalParameter': 56}
tokendict = {'DecimalInteger': 57, 'HexInteger': 58, 'Identifier': 59, 'Keyword': 60, 'Modifier': 61, 'Null': 62,
             'OctalInteger': 63, 'Operator': 64, 'Separator': 65, 'String': 66, 'Annotation': 67, 'BasicType': 68,
             'Boolean': 69, 'DecimalFloatingPoint': 70, 'HexFloatingPoint': 71}


def listdir(path, list_name):
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            listdir(file_path, list_name)
        else:
            list_name.append(file_path)


def get_token(node):
    token = ''
    # print(isinstance(node, Node))
    # print(type(node))
    if isinstance(node, str):
        token = node
    elif isinstance(node, set):
        token = 'Modifier'
    elif isinstance(node, Node):
        token = node.__class__.__name__
    # print(node.__class__.__name__,str(node))
    # print(node.__class__.__name__, node)
    return token

def get_child(root):
    # print(root)
    if isinstance(root, Node):
        children = root.children
    elif isinstance(root, set):
        children = list(root)
    else:
        children = []

    def expand(nested_list):
        for item in nested_list:
            if isinstance(item, list):
                for sub_item in expand(item):
                    # print(sub_item)
                    yield sub_item
            elif item:
                # print(item)
                yield item
    return list(expand(children))


def createtree(root, node, nodelist, parent=None):
    id = len(nodelist)
    # print(id)
    token, children = get_token(node), get_child(node)
    if id == 0:
        root.token = token
        root.data = node
    else:
        newnode = AnyNode(id=id, token=token, data=node, parent=parent)
    nodelist.append(node)
    for child in children:
        if id == 0:
            createtree(root, child, nodelist, parent=root)
        else:
            createtree(root, child, nodelist, parent=newnode)

def getnodeandedge(node, src, tgt):
    for child in node.children:
        src.append(node.token)
        tgt.append(child.token)
        getnodeandedge(child, src, tgt)

def getdofcode(src, tgt, typedict):
    # get Dof value
    matrix = [0 for col in range(72)]
    for i in range(len(src)):
        m = nodetypedict[src[i]]
        matrix[m] += 1
        name = tgt[i]
        try:
            n = nodetypedict[name]
        except KeyError:
            try:
                n = tokendict[typedict[name]]
            except KeyError:
                n = 62
        if n > 56:
            matrix[n] += 1
    total = 0
    for l in range(72):
        total += matrix[l]
    if total != 0:
        for p in range(72):
            matrix[p] = matrix[p] / total
    return matrix


def dof_matrix(path, pkl_path=None):
    programfile = open(path, encoding='utf-8')
    programtext = programfile.read()
    programtokens = javalang.tokenizer.tokenize(programtext)
    parser = javalang.parse.Parser(programtokens)
    tree = parser.parse_member_declaration()
    programfile.close()

    file = open(path, "r", encoding='utf-8')
    tokens = list(javalang.tokenizer.tokenize(file.read()))
    file.close()

    # create tree
    nodelist = []
    newtree = AnyNode(id=0, token=None, data=None)
    createtree(newtree, tree, nodelist)

    if pkl_path != None:
        out_pkl = pkl_path + path.split('/')[-1].split('.java')[0] + '.pkl'
        WriteAndRead.write_pkl(out_pkl, newtree)

    typedict = {}
    for token in tokens:
        token_type = str(type(token))[:-2].split(".")[-1]
        token_value = token.value
        if token_value not in typedict:
            typedict[token_value] = token_type
        else:
            if typedict[token_value] != token_type:
                print('!!!!!!!!')

    src = []
    tgt = []
    getnodeandedge(newtree, src, tgt)

    sub_root = []
    sub_id = []
    root_nod = src[0]
    for i in range(len(src)-1):
        if 'MethodDeclaration' in src:
            if src[i] == 'MethodDeclaration':
                sub_root.append(src[i + 1])
                sub_id.append(i + 1)
        elif src[i] == root_nod:
            sub_root.append(src[i+1])
            sub_id.append(i+1)
    sub_id.append(len(src)+1)

    src_if = []
    tgt_if = []
    src_for = []
    tgt_for = []
    src_try = []
    tgt_try = []
    src_whi = []
    tgt_whi = []
    src_swi = []
    tgt_swi = []
    src_struc = []
    tgt_struc = []
    for j in range(len(sub_root)):
        if sub_root[j] == 'IfStatement':
            if_sta = sub_id[j]
            if_end = sub_id[j+1] - 1
            for k in range(if_sta, if_end):
                src_if.append(src[k])
                tgt_if.append(tgt[k])
        elif sub_root[j] == 'ForStatement':
            for_sta = sub_id[j]
            for_end = sub_id[j+1] - 1
            for k in range(for_sta, for_end):
                src_for.append(src[k])
                tgt_for.append(tgt[k])
        elif sub_root[j] == 'TryStatement':
            try_sta = sub_id[j]
            try_end = sub_id[j + 1] - 1
            for k in range(try_sta, try_end):
                src_try.append(src[k])
                tgt_try.append(tgt[k])
        elif sub_root[j] == 'WhileStatement':
            whi_sta = sub_id[j]
            whi_end = sub_id[j + 1] - 1
            for k in range(whi_sta, whi_end):
                src_whi.append(src[k])
                tgt_whi.append(tgt[k])
        elif sub_root[j] == 'SwitchStatement':
            swi_sta = sub_id[j]
            swi_end = sub_id[j + 1] - 1
            for k in range(swi_sta, swi_end):
                src_swi.append(src[k])
                tgt_swi.append(tgt[k])
        else:
            struc_sta = sub_id[j]-1
            struc_end = sub_id[j+1]-1
            for k in range(struc_sta, struc_end):
                src_struc.append(src[k])
                tgt_struc.append(tgt[k])
    struc_vecter = getdofcode(src_struc, tgt_struc, typedict)
    if_vecter = getdofcode(src_if, tgt_if, typedict)
    for_vecter = getdofcode(src_for, tgt_for, typedict)
    try_vecter = getdofcode(src_try, tgt_try, typedict)
    whi_vecter = getdofcode(src_whi, tgt_whi, typedict)
    swi_vecter = getdofcode(src_swi, tgt_swi, typedict)
    matrix1 = [struc_vecter] + [for_vecter] + [whi_vecter] + [if_vecter] + [try_vecter] + [swi_vecter]

    src_if_sub = []
    tgt_if_sub = []
    src_for_sub = []
    tgt_for_sub = []
    src_try_sub = []
    tgt_try_sub = []
    src_whi_sub = []
    tgt_whi_sub = []
    src_swi_sub = []
    tgt_swi_sub = []
    sub_root_if = []
    sub_id_if = []
    for x in range(len(src_if)-1):
        if src_if[x] == 'IfStatement':
            sub_root_if.append(src_if[x+1])
            sub_id_if.append(x+1)
    sub_id_if.append(len(src_if)+1)
    for q in range(len(sub_root_if)):
        if sub_root_if[q] == 'BlockStatement':
            if_blo_start = sub_id_if[q]
            if_blo_end = sub_id_if[q+1] - 1
            for p in range(if_blo_start, if_blo_end):
                src_if_sub.append(src_if[p])
                tgt_if_sub.append(tgt_if[p])
    sub_root_for = []
    sub_id_for = []
    for x in range(len(src_for) - 1):
        if src_for[x] == 'ForStatement':
            sub_root_for.append(src_for[x + 1])
            sub_id_for.append(x + 1)
    sub_id_for.append(len(src_for) + 1)
    for q in range(len(sub_root_for)):
        if sub_root_for[q] == 'BlockStatement':
            for_blo_start = sub_id_for[q]
            for_blo_end = sub_id_for[q + 1] - 1
            for p in range(for_blo_start, for_blo_end):
                src_for_sub.append(src_for[p])
                tgt_for_sub.append(tgt_for[p])
    sub_root_try = []
    sub_id_try = []
    for x in range(len(src_try) - 1):
        if src_try[x] == 'TryStatement':
            sub_root_try.append(src_try[x + 1])
            sub_id_try.append(x + 1)
    sub_id_try.append(len(src_try) + 1)
    for q in range(len(sub_root_try)):
        if sub_root_try[q] == 'ForStatement':
            try_for_start = sub_id_try[q]
            try_for_end = sub_id_try[q + 1] - 1
            for p in range(try_for_start, try_for_end):
                src_try_sub.append(src_try[p])
                tgt_try_sub.append(tgt_try[p])
    sub_root_whi = []
    sub_id_whi = []
    for x in range(len(src_whi)-1):
        if src_whi[x] == 'WhileStatement':
            sub_root_whi.append(src_whi[x+1])
            sub_id_whi.append(x+1)
    sub_id_whi.append(len(src_whi)+1)
    for q in range(len(sub_root_whi)):
        if sub_root_whi[q] == 'BlockStatement':
            whi_blo_start = sub_id_whi[q]
            whi_blo_end = sub_id_whi[q+1] - 1
            for p in range(whi_blo_start, whi_blo_end):
                src_whi_sub.append(src_whi[p])
                tgt_whi_sub.append(tgt_whi[p])
    sub_root_swi = []
    sub_id_swi = []
    for x in range(len(src_swi) - 1):
        if src_swi[x] == 'SwitchStatement':
            sub_root_swi.append(src_swi[x + 1])
            sub_id_swi.append(x + 1)
    sub_id_swi.append(len(src_swi) + 1)
    for q in range(len(sub_root_swi)):
        if sub_root_swi[q] == 'SwitchStatementCase':
            swi_Swi_start = sub_id_swi[q]
            swi_Swi_end = sub_id_swi[q + 1] - 1
            for p in range(swi_Swi_start, swi_Swi_end):
                src_swi_sub.append(src_swi[p])
                tgt_swi_sub.append(tgt_swi[p])
    for_sub_vecter = getdofcode(src_for_sub, tgt_for_sub, typedict)
    whi_sub_vecter = getdofcode(src_whi_sub, tgt_whi_sub, typedict)
    if_sub_vecter = getdofcode(src_if_sub, tgt_if_sub, typedict)
    try_sub_vecter = getdofcode(src_try_sub, tgt_try_sub, typedict)
    swi_sub_vecter = getdofcode(src_swi_sub, tgt_swi_sub, typedict)
    matrix2 = [for_sub_vecter] + [whi_sub_vecter] + [if_sub_vecter] + [try_sub_vecter] + [swi_sub_vecter]
    matrix = matrix1 + matrix2
    matrix = np.array(matrix)
    filename = path.split('/')[-1].split('.java')[0]
    print(filename)
    npypath = './dof/' + filename
    np.save(npypath, matrix)
    return matrix


javapath = './dataset/googlejam4/'

def allmain():
    # Read all java files from a folder
    javalist = []
    listdir(javapath, javalist)

    for javafile in javalist:
        try:
            dof_matrix(javafile)
        except (UnicodeDecodeError, javalang.parser.JavaSyntaxError, javalang.tokenizer.LexerError):
            print(javafile)


if __name__ == '__main__':
    allmain()

