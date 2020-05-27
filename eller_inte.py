import re


# разделяет считанный текст на предложения с их разбором
def get_sentences():
    with open('corpora.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    sentences = text.split('\n\n')
    return sentences


# находит номер вершины, от которой зависит нужная конструкция
def find_root_number(lines, i):
    sec_dep = lines[i].split('\t')[8]
    match = re.search(r'(\d+):conj', sec_dep)   # зависимость conj может быть у eller или у inte, а нужный номер слова будет именно в завис. conj
    if match:
        root_number = match.group(1)
    else:
        other_sec_dep = lines[i + 1].split('\t')[8]
        match = re.search(r'(\d+):conj', other_sec_dep) # если не нашлось conj у eller, то берем ее у inte
        root_number = match.group(1)
    return root_number


# находит слова, зависящие от вершины нужной конструкции, которые тоже следует воостановить
def find_root_deps(root_number, lines):
    useful_deps = {'cop', 'advmod', 'aux'}
    root_deps = []
    for l in lines:
        if l != '' and l[0].isdigit():
            parts = l.split('\t')
            numbers = re.findall(r'(\d+)', parts[8])
            for n in numbers:
                if n == root_number:
                    dep = re.search(r'\d+:(\w+)', parts[8]).group(1)
                else:
                    dep = ''
            if dep in useful_deps:
                root_deps.append(l)
    return root_deps


# заменяет зависимости eller и inte
def change_eller_inte_deps(lines, i, new_line_number, root_deps):
    parts_eller = lines[i].split('\t')
    parts_eller[8] = str(new_line_number) + '.' + str(len(root_deps) + 1) + ':cc' # eller размечается сс, зависящее от восстановленной вершины
    lines[i] = '\t'.join(parts_eller)
    parts_inte = lines[i + 1].split('\t')
    parts_inte[8] = str(new_line_number) + '.' + str(len(root_deps) + 1) + ':advmod' # inte размечеается как advmod, завис. от восстановленной вершины
    lines[i + 1] = '\t'.join(parts_inte)
    return lines[i], lines[i+1]


# создает зависимости восстановленной вершины
def change_root_deps(lines, new_line_number, root_number):
    for i in range(len(lines)):
        parts = lines[i].split('\t')
        if parts[0] == root_number:
            parts[6] = '_'                         # на месте первичных зависимостей - прочерки
            parts[7] = '_'
            parts[8] = root_number + ':conj:eller' # вторичная зависимость conj:eller
            root_line = '\t'.join(parts[1:])
            new_line = str(new_line_number) + '.1\t' + root_line # номер строки также меняется
    return new_line


# вставляет восстановленную вершину в предложение
def insert_new_root(lines, new_line, root_deps, placing_line_number):
    if root_deps == []:
        lines.insert(placing_line_number, new_line)
    else:
        new_parts = new_line.split('\t')  # если у восстановленной вершины восстанавливаются какие-то зависимости, то номер вершины изменяется
        num = new_parts[0].split('.')[0]
        new_parts[0] = num + '.' + str(len(root_deps) + 1)
        new_line = '\t'.join(new_parts)
        lines.insert(placing_line_number, new_line)
    return lines


# вставляет восстановленные зависимые вершины
def insert_other_root_deps(lines, root_deps, new_line, new_line_number, placing_line_number):
    for i in range(len(root_deps)-1, -1, -1):
        deps_parts = root_deps[i].split('\t')
        deps_parts[0] = str(new_line_number) + '.' + str(i+1) # изменяет номер строки
        dep_dep = deps_parts[8].split(':')[1]
        deps_parts[8] = new_line.split('\t')[0] + ':' + dep_dep # изменяет номер в зависимости
        root_deps[i] = '\t'.join(deps_parts)
        lines.insert(placing_line_number, root_deps[i])
    return lines


# записывает предложения в новый файл
def write_sentence(text):
    with open('eller_inte_result.txt', 'w', encoding='utf-8') as f:
        f.write(text)


# основная функция
def fix_construction(sentences):
    f = 0
    count = 0
    new_sents = []
    for sentence in sentences:
        lines = sentence.split('\n')
        for i in range(len(lines)-2):
            if lines[i] != '' and lines[i][0].isdigit(): # находятся конструкции eller inte + любой знак пунктуации после
                if lines[i].split('\t')[2] == 'eller' and lines[i+1].split('\t')[2] == 'inte' and lines[i+2].split('\t')[3] == 'PUNCT':
                    root_number = find_root_number(lines, i)  # ищет номер вершины конструкции

                    new_line_number = lines[i].split('\t')[0] # номер, который получит восстановленная вершина
                    new_line_number = int(new_line_number) + 1
                    placing_line_number = i + 2               # реальный номер строки, куда вставится восстановленная вершина

                    root_deps = find_root_deps(root_number, lines) # находятся нужные зависимости восстановленной вершины

                    lines[i], lines[i+1] = change_eller_inte_deps(lines, i, new_line_number, root_deps)
                    f = 1
        if f == 1:
            if root_number != '':
                new_line = change_root_deps(lines, new_line_number, root_number)
                lines = insert_new_root(lines, new_line, root_deps, placing_line_number)
                lines = insert_other_root_deps(lines, root_deps, new_line, new_line_number, placing_line_number)
                count += 1
        new_sents.append('\n'.join(lines))
        root_number = ''
    write_sentence('\n\n'.join(new_sents))
    return count


if __name__ == '__main__':
    sentences = get_sentences()
    count = fix_construction(sentences)
    print(count)

