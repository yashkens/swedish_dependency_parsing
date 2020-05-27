import re

# разделяет считанный текст на предложения с их разбором
def get_sentences():
    with open('corpora.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    sentences = text.split('\n\n')
    return sentences


# изменяет строку с числительным
def change_dep(number_line, lines):
    parts = number_line.split('\t')
    dep_num = parts[6]
    for line in lines:
        if line.split('\t')[0] == dep_num:
            if line.split('\t')[3] == 'NOUN':   # если строка зависит от сущ., то зависимость nmod
                parts[8] = dep_num + ':nmod'    # во всех остальных случаях obl
            else:
                if 'obl' not in parts[8]:       # если зависимость изначально была obl
                    parts[8] = dep_num + ':obl' # то не изменяем, чтобы сохранить возможное уточнение предлога
    return '\t'.join(parts)


# основная функция
def fix_year(sentences):
    count = 0
    new_sents = []
    for sent in sentences:
        f = 0
        lines = sent.split('\n')
        for i in range(len(lines)):
            if lines[i] != '' and lines[i][0].isdigit():
                parts = lines[i].split('\t')
                match = re.search(r'\b\d{4}\b', parts[1])
                if match:
                    if check_number(match.group(), lines[i], lines): # проверка, похоже ли числительное на год
                        count += 1
                        new_line = change_dep(lines[i], lines)
                        lines[i] = new_line
        new_sents.append('\n'.join(lines))
    write_sentence('\n\n'.join(new_sents))
    return count


# проверка числительного на то, является ли оно годом
def check_number(number, number_line, lines):
    needed_nums = {'1', '2'}
    if number[0] not in needed_nums:    # не является, если первая цифра не 1 или 2
        return False
    dep_num = number_line.split('\t')[6]
    for line in lines:
        if line.split('\t')[0] == dep_num:  # не является, если зависит от слова в мн.ч. или аббревиатуры
            if 'Plur' in line.split('\t')[5] or 'Abbr' in line.split('\t')[5]:
                return False
    return True


# записывает в файл
def write_sentence(text):
    with open('years_result.txt', 'w', encoding='utf-8') as f:
        f.write(text)


if __name__ == '__main__':
    sentences = get_sentences()
    count = fix_year(sentences)
    print(count)


