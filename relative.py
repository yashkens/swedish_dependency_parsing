# разделяет файл на предложения с их разбором
def extract_sentences(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()
    return text.split('\n\n')


# составляет список со строками, содержащими союз
def extract_soms(lines):
    som_list = []

    for l in lines:
        if l != '' and l[0].isdigit():
            parts = l.split('\t')
            if parts[2] == 'som' and (parts[7] == 'nsubj' or parts[7] == 'nsubj:pass'): # важно, что первичные завиимости должны быть nsubj
                if len(som_list) != 0 and 'ref' not in parts[8]:
                    som_list.append(l)
                elif len(som_list) != 0 and 'ref' in parts[8] and check_if_more(l, lines):
                    som_list[0] = l
                elif len(som_list) == 0:
                    som_list.append(l)
    return som_list


# проверяет, есть ли еще союзы som после определенной строки
def check_if_more(l, lines):
    num = int(l.split('\t')[0])
    left_lines = lines[num + 3:]
    for line in left_lines:
        if line.split('\t')[2] == 'som':
            return True
    return False


# проверяет рядом стоящую пару строк с союзами на то, являются ли они однородными
def check_pair(first, second, lines):
    first_parts = first.split('\t')
    second_parts = second.split('\t')
    for line in lines:
        if line.split('\t')[0] == second_parts[6]:
            second_depend = line
    depend_parts = second_depend.split('\t')
    if depend_parts[7] == 'conj' and depend_parts[6] == first_parts[6]:
        return True
    else:
        return False


# изменяет зависимость строки, являющейся референтом для обоих союзов
def change_reference(sentence, dep_num, second):
    for l in sentence.split('\n'):
        parts = l.split('\t')
        if parts[0] == dep_num:
            parts[8] = parts[8] + '|' + second.split('\t')[8]
            return '\t'.join(parts)
    return ''


# изменяет строку с вторым в нужной паре союзом
def change_second_som(first, second):
    first_parts = first.split('\t')
    second_parts = second.split('\t')
    second_parts[8] = first_parts[8]    # его вторичная зависимость будет такой же, как у первого союза
    return '\t'.join(second_parts)


# основная функция
def fix_relative(sentence):
    lines = sentence.split('\n')
    som_list = extract_soms(lines)
    if len(som_list) <= 1:
        return 0, lines
    count = 0
    for i in range(1, len(som_list)):
        if check_pair(som_list[i-1], som_list[i], lines):
            count = 1
            dep_num = som_list[i-1].split('\t')[8].split(':')[0]
            reference = change_reference(sentence, dep_num, som_list[i])
            second = change_second_som(som_list[i-1], som_list[i])
            second_num = som_list[i].split('\t')[0]
            ref_num = reference.split('\t')[0]
            lines = replace_line(lines, ref_num, reference)
            lines = replace_line(lines, second_num, second)
            som_list[i] = second

        elif count == 1 and 'ref' in som_list[i-1].split('\t')[8]:
            ref_parts = reference.split('\t')
            ref_parts[8] = ref_parts[8] + '|' + som_list[i].split('\t')[8]
            new_ref = '\t'.join(ref_parts)
            ref_num = reference.split('\t')[0]
            lines = replace_line(lines, ref_num, new_ref)
            other = change_second_som(som_list[i-1], som_list[i])
            other_num = som_list[i].split('\t')[0]
            lines = replace_line(lines, other_num, other)
    return count, lines



# заменяет строку в разборе предложения
def replace_line(lines, num, new_line):
    for i in range(len(lines)):
        if lines[i].split('\t')[0] == num:
            lines[i] = new_line
    return lines


# записывает предложения в файл
def write_sentences(text, filename):
    with open(filename, 'a+', encoding='utf-8') as f:
        f.write(text)

if __name__ == '__main__':
    sentences = extract_sentences('corpora.txt')
    count = 0
    new_sents = []
    for sent in sentences:
        num, lines = fix_relative(sent)
        count += num
        new_sents.append('\n'.join(lines))
    write_sentences('\n\n'.join(new_sents), 'relative_result.txt')
    print(count)


