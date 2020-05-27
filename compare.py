# В коде две части: первая исправляет предложения с "än tidigare", а вторая - остальные случаи

import re

# разделяет считанный текст на предложения с их разбором
def get_sentences():
    with open('corpora.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    sentences = text.split('\n\n')
    return sentences

# основная функция, изменяющая адвербиальные клаузы
def fix_adverbial(dep_line, lines, placing_num, line):
    main_line = find_line_with_num(dep_line, lines)     # линия, от которой зависит сравнительная клауза
    main_parts = main_line.split('\t')
    if 'obl' in main_parts[8] or 'obj' in main_parts[8]:                          # из-за ошибок в разметке она может находится дальше, чем ожидалось
        main_line = find_line_with_num(main_line, lines)

    other_deps = adv_other_deps(main_line, lines)       # строки, которые нужно восстановить вместе с главной строкой
    new_lines, new_main_line = change_lines_adv(dep_line, main_line, other_deps) # список измененных строк, которые должны быть восстановлены
    new_dep_line = change_depend_adv(dep_line, new_main_line)   # измененная существующая (не требующая восстановл.) строка в сравнительной клаузе

    for i in range(len(new_lines)):
        lines.insert(placing_num + i, new_lines[i])  # вставляем восстановленные строки

    new_mark_line = change_mark_line(line, new_main_line)   # измененная строка с союзом
    mark_num = line.split('\t')[0]
    for i in range(len(lines)):                             # вставим ее на место
        if lines[i] != '' and lines[i][0].isdigit():
            if lines[i].split('\t')[0] == mark_num:
                lines[i] = new_mark_line

    depend_num = dep_line.split('\t')[0]                #вставим на измененную существующую строку сравнительной клаузы
    for i in range(len(lines)):
        if lines[i] != '' and lines[i][0].isdigit():
            if lines[i].split('\t')[0] == depend_num:
                lines[i] = new_dep_line
    return lines


def change_depend_adv(dep_line, new_main_line):     # изменяет существующую строку сравнительной клаузы
    num = new_main_line.split('\t')[0]
    parts = dep_line.split('\t')
    parts[8] = num + ':' + 'advmod'
    return '\t'.join(parts)


def adv_other_deps(main_line, lines):       # находит зависимости главной строки, которые тоже нужно восстанавливать
    needed = {'cop', 'compound:prt', 'ref', 'nsubj'}    # этот список нужно обсудить
    other_deps = []                                     # например, нужно восстанавливать отрицательную частицу, но остальные
                                                        # advmod восстанавливать не нужно
    main_num = main_line.split('\t')[0]
    for line in lines:
        if line != '' and line[0].isdigit():
            dep = line.split('\t')[8]
            match = re.search(r'(\d+):(\D+)', dep)
            if match.group(1) == main_num:
                if match.group(2) in needed:
                    other_deps.append(line)
    return other_deps


def change_lines_adv(dep_line, main_line, other_deps):  # изменяет восстанавливаемые линии
    new_lines = []
    new_num = str(int(dep_line.split('\t')[0]) - 1)

    main_parts = main_line.split('\t')
    main_num = main_parts[0]
    main_parts[6] = '_'
    main_parts[7] = '_'
    main_parts[8] = main_num + ':advcl:än'

    first_deps = []
    for dep in other_deps:
        if dep.split('\t')[0] < main_num:
            first_deps.append(dep)
            other_deps.remove(dep)

    main_parts[0] = new_num + '.' + str(len(first_deps) + 1)
    for i in range(len(first_deps)):
        first_parts = first_deps[i].split('\t')
        first_parts[0] = new_num + '.' + str(i + 1)
        first_parts[6] = '_'
        first_parts[7] = '_'
        dep = first_parts[8]
        first_parts[8] = re.sub(r'\d+', main_parts[0], dep)
        new_lines.append('\t'.join(first_parts))

    main_line = '\t'.join(main_parts)
    new_lines.append(main_line)

    sec_num = 2 + len(first_deps)
    for i in range(len(other_deps)):
        parts = other_deps[i].split('\t')
        parts[0] = new_num + '.' + str(sec_num + i)
        parts[6] = '_'
        parts[7] = '_'
        dep = parts[8]
        parts[8] = re.sub(r'\d+', main_parts[0], dep)
        new_lines.append('\t'.join(parts))
    return new_lines, main_line

# ---------------------------------------------------------------
# Часть 2
# ---------------------------------------------------------------

# находит строку, от которой зависит данная строка
def find_line_with_num(line, lines):
    depend = line.split('\t')[8]
    match = re.search(r'(\d+):', depend)
    depend_num = match.group(1)
    for l in lines:
        if l.split('\t')[0] == depend_num:
            depend_line = l
    return depend_line


# находит зависимости главной строки, которые тоже надо восстанавливать
def find_main_deps(main_line, lines, depend_line):
    needed = {'cop', 'aux', 'compound:prt'}     # тоже нужно обсудить
    if 'än' not in depend_line.split('\t')[8]:              # заметила, что нужно восстанавливать еще и подл., если в зависимости
        needed = {'cop', 'aux', 'compound:prt', 'nsubj'}    # не указан нужный союз än, но, может быть, есть исключения
    other_deps = []

    main_num = main_line.split('\t')[0]
    for line in lines:
        if line != '' and line[0].isdigit():
            dep = line.split('\t')[8]
            match = re.search(r'(\d+):(\D+)', dep)
            if match.group(1) == main_num:
                if match.group(2) in needed:
                    other_deps.append(line)
    return other_deps


# изменяет существующий кусочек сравнительной клаузы
def change_depend_line(depend_line, main_line):
    num = main_line.split('\t')[0]
    parts = depend_line.split('\t')
    if 'än' in parts[8]:
        parts[8] = num + ':' + 'nsubj'  # нужно придумать, как определять nsubj:pass
    else:
        parts[8] = num + ':' + 'obl'    # нужно придумать, как восстанавливать предлог
    return '\t'.join(parts)


# изменяет строку с союзом
def change_mark_line(line, main_line):
    num = main_line.split('\t')[0]
    parts = line.split('\t')
    parts[8] = num + ':mark'
    return '\t'.join(parts)


# меняет вставляемую линию и ее зависимые
# очень длинная функция, потому что учитывается порядок постановки зависимых и главной клаузы
def change_lines(main_line, other_deps, new_number):
    new_other_deps = []
    placing_lines = []
    if other_deps != []:
        for i in range(len(other_deps)):
            other_parts = other_deps[i].split('\t')
            other_parts[6] = '_'
            other_parts[7] = '_'
            dep = other_parts[8]
            if int(main_line.split('\t')[0]) < int(other_parts[0]):
                other_parts[0] = new_number + '.' + str(i + 2)
                other_parts[8] = re.sub(r'\d+', new_number + '.1', dep)
            else:
                other_parts[0] = new_number + '.' + str(i + 1)
                other_parts[8] = re.sub(r'\d+', new_number + '.' + str(len(other_deps) + 1), dep)
            new_other_deps.append('\t'.join(other_parts))

        main_parts = main_line.split('\t')
        main_num = main_parts[0]
        main_parts[7] = '_'
        main_parts[6] = '_'
        main_parts[8] = main_num + ':advcl:än'
        if int(main_num) < int(other_deps[0].split('\t')[0]):
            main_parts[0] = new_number + '.1'
            new_main_line = '\t'.join(main_parts)
            placing_lines.append(new_main_line)
            for dep in new_other_deps:
                placing_lines.append(dep)
        else:
            main_parts[0] = new_number + '.' + str(len(other_deps) + 1)
            new_main_line = '\t'.join(main_parts)
            for dep in new_other_deps:
                placing_lines.append(dep)
            placing_lines.append(new_main_line)

    else:
        main_parts = main_line.split('\t')
        main_num = main_parts[0]
        main_parts[7] = '_'
        main_parts[6] = '_'
        main_parts[8] = main_num + ':advcl:än'
        main_parts[0] = new_number + '.1'
        new_main_line = '\t'.join(main_parts)
        placing_lines.append(new_main_line)

    return placing_lines, new_main_line


# основная функция (для обеих частей)
def fix_construction(line, lines, k, placing_num):
    new_number = line.split('\t')[0]                # номер, который получит строка которую восстановим
    depend_line = find_line_with_num(line, lines)
    if check_sentence(depend_line, lines):          # проверка, нужно ли вообще менять это предложение
        return 0, lines

    if depend_line.split('\t')[3] == 'ADV': #and depend_line.split('\t')[5] == 'Degree=Cmp':    # если предложение с  tidigare, то используем первую часть кода
        lines = fix_adverbial(depend_line, lines, placing_num, line)

    else:
        main_line = find_line_with_num(depend_line, lines) # линия, от которой зависит сравнительная клауза
        main_parts = main_line.split('\t')
        if 'obl' in main_parts[8] or 'obj' in main_parts[8]:
            main_line = find_line_with_num(main_line, lines)

        if 'Degree=Cmp' in main_line.split('\t')[5]:    # дополнительная проверка
            return 0, lines                             # если в главное слово в сравнит. степени, то не исправляем предложение

        other_deps = find_main_deps(main_line, lines, depend_line)

        if 'än' in depend_line.split('\t')[8]:         # из-за непостоянности в разметке, возможно придется изменить...
            placing_num = int(depend_line.split('\t')[0]) + k   # место, куда вставляем строки
            new_number = depend_line.split('\t')[0]             # номер для новых строк

        new_lines, new_main_line = change_lines(main_line, other_deps, new_number) # измененные строки, готовые к восстановлению

        for i in range(len(new_lines)):         # вставляем восстановленные строки
            lines.insert(placing_num + i, new_lines[i])

        new_mark_line = change_mark_line(line, new_main_line) # изменяем строку с союзом, вставляем на место
        mark_num = line.split('\t')[0]
        for i in range(len(lines)):
            if lines[i] != '' and lines[i][0].isdigit():
                if lines[i].split('\t')[0] == mark_num:
                    lines[i] = new_mark_line

        new_depend_line = change_depend_line(depend_line, new_main_line) # вставляем измененную строку из сравнительной клаузы
        depend_num = depend_line.split('\t')[0]
        for i in range(len(lines)):
            if lines[i] != '' and lines[i][0].isdigit():
                if lines[i].split('\t')[0] == depend_num:
                    lines[i] = new_depend_line
    return 1, lines


# Записывает полученные предложения в файл
def write_to_file(text):
    with open('compare_result.txt', 'w', encoding='utf-8') as f:
         f.write(text)
    return

# главная функция, запускает все изменения, если они необходимы
def choose_sentence(sentences):
    count = 0
    new_sents = []
    for sent in sentences:
        k = 0
        f = 0
        should_count = False
        lines = sent.split('\n')
        for i in range(len(lines)):
            if lines[i] != '' and lines[i][0].isdigit():
                parts = lines[i].split('\t')
                if parts[1] == 'än' and parts[7] != 'fixed' and parts[7] != 'advmod': # изменения будут только в предложениях, где есть нужный союз
                    f, lines = fix_construction(lines[i], lines, k, i + 1) # втрой этап проверки предложения уже в этой функции
                    should_count = True
            elif lines[i][0] == '#':
                k += 1
        new_sents.append('\n'.join(lines))
        if should_count and f == 1:
            count += 1
    write_to_file('\n\n'.join(new_sents))
    return count


# второй этап проверки, нужно ли менять предложение
def check_sentence(dep_line, lines):
    if 'nsubj' in dep_line.split('\t')[8]:  # если существующая часть сравнительной клаузы является подлежащим,
        return True                         # то не меняем

    dep_num = dep_line.split('\t')[6]       # ниже набор условий, помогающий определить необходимость изменений
    for line in lines:                      # каждое условие постараюсь объяснить с примерами в части описания программ
        if line != '' and line[0].isdigit():
            if line.split('\t')[6] == dep_num and line.split('\t')[2] == 'annan':
                return True
            elif line.split('\t')[0] == dep_num and line.split('\t')[2] == 'annan':
                return True
            elif line.split('\t')[0] == dep_num and 'Degree=Cmp' in line.split('\t')[5]:
                return True
            elif line.split('\t')[0] == dep_num and line.split('\t')[2] == 'fler':
                return True
            elif line.split('\t')[6] == dep_line.split('\t')[0] and line.split('\t')[7] == 'nummod':
                return True

    num = dep_line.split('\t')[0]

    for line in lines:                          # если у существующей части сравнительной клаузы есть свое подлежащее,
        if line != '' and line[0].isdigit():    # то восстанавливать и менять ничего не нужно
            dep = line.split('\t')[8]
            deps = dep.split('|')
            for d in deps:
                match = re.search(r'(\d+):(\D+)', d)
                if match:
                    if match.group(1) == num and 'nsubj' in match.group(2):
                        return True
    return False

if __name__ == '__main__':
    sentences = get_sentences()
    count = choose_sentence(sentences)
    print(count)
