# -*- coding: utf-8 -*-

from __future__ import division
import codecs
import os
import re
 
# Задаём расположение файлов для сравнения
SOURCE_PATH = './Arno_Cart'  # название папки, в которой лежат варианты, которые нужно сравнить с каноническим
CANON = './Arno_Cart_kanon.txt'  # название файла, в котором лежит канонический текст
 
beg_g = '<font color="#008000">'   # начало выделения зеленым цветом в html
beg_r = '<font color="#E80000">'  # начало выделения красным цветом в html
end = '</font>'  # конец выделения цветом в html
 
 
# Вычисление расстояния Левенштейна между двумя текстами
 
# Принимает имена файлов t. Возвращает список дескрипторов открытых файлов.
def open_files(t):
    text_open1 = codecs.open(t[0], 'r', 'utf-8')
    text_open2 = codecs.open(t[1], 'r', 'utf-8')
    text_write1 = codecs.open(t[2], 'w', 'utf-8')
    return [text_open1, text_open2, text_write1]
 
 
# Закрывает открытые файлы
def close_files(t):
    for k in t:
        k.close()
 
 
# Возвращает общую последовательность подряд идущих символов - для случаев, когда слова совпадают не полностью
def common_s(s1, s2):
    m = [[0] * (1 + len(s2)) for _ in xrange(1 + len(s1))]
    longest, x_longest = 0, 0
    for x in xrange(1, 1 + len(s1)):
        for y in xrange(1, 1 + len(s2)):
            if s1[x - 1] == s2[y - 1]:
                m[x][y] = m[x - 1][y - 1] + 1
                if m[x][y] > longest:
                    longest = m[x][y]
                    x_longest = x
            else:
                m[x][y] = 0
    return s1[x_longest - longest: x_longest]
 
 
# Сравнивает строку l1 со строкой l2 ( Без '\n' !)
# - ТОЛЬКО для формировния perc и выделения частичн. совп. 
# Возвращает список - исходную l1 строку [0] и процент совпадения [1]. либо ''. 
def compare(l1, l2):
    same = ''  # строка с совпадениями
    diff = ''  # строка с несовпадениями с первой строке
    new1 = ''
    # print "L1 = ", l1
    # print "L2 = ", l2
    l1 = l1.strip()
    l2 = l2.strip()
    if (len(l1) == 0) or (len(l2) == 0):
        return ''  # вернем ''
    for i in l1.split():  # цикл по словам в 1й строке
        match_ij = False  # Совпадение слов i, j
        full_match = False
        for j in l2.split():
            if i == j:
                same += i + '\n'
                full_match = match_ij = True
                break
        for j in l2.split():
            if not full_match:
                if len(common_s(i, j)) != 0:
                    if len(common_s(i, j)) >= 4 or len(i) == 2 or (len(common_s(i, j))/len(i)) >= 0.75:
                        punct_arr = ['.', ',', ';', ':', '!', '?']
                        if j[-1] in punct_arr and i[-1] not in punct_arr:
                            newi = i.split(common_s(i, j))
                            newii = u'<r>' + newi[0] + u'</r>' + common_s(i, j) + u'<r>' + \
                                    newi[1] + u'</r>' + u'<r>_</r>'
                        else:
                            newi = i.split(common_s(i, j))
                            newii = u'<r>' + newi[0] + u'</r>' + common_s(i, j) + u'<r>' + newi[1] + u'</r>'
                        same += newii + '\n'
                        l1 = l1.replace(i, newii)
                        match_ij = True
                        break
        if not match_ij:
            diff += i + '\n'
    # Условие про минимум одинаковых слов в строках (60% или 75% ?)
    p = len(same.split())/len(l1.split())
    if len(same.split()) > 0:
        if p >= 0.6:
            # print "MATCHED!", l1
            # print "SAME =", same
            # print len(same.split())/len(l1.split())
            match = True
        else:
            diff += same
            same = ''
            match = False
    else:
        match = False
 
    if match:
        for e in l1.split():
            if e in same:
                new1 += e + ' '
            else:
                e = beg_r + e + end
                new1 += e + ' '
        new1 = re.sub(u'<r>', beg_r, new1)
        new1 = re.sub(u'<g>', beg_g, new1)
        new1 = re.sub(u'</r>', end, new1)
        new1 = re.sub(u'</g>', end, new1)
        print "return new1: ", new1
        return [new1, p] # Возвращает список - исходную l1 строку [0] и процент совпадения [1].
    else:
        return '' #  либо возвращает пустую строку
 
 
# t - список дескрипторов 3 файлов. Сравнивает t[0] с t[1]. Но не наоборот. Формирует t[2]. global perc - модифицируется!
def analysis(t, compare_function):
    header = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">\n'
    header += '<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8" />'
    header += '\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n'
    header += '<title></title></head>\n<body>'
    footer = str('</body>\n</html>')
    text1 = t[0].read()
    text1 = unicode(text1)
    text2 = t[1].read()
    text2 = unicode(text2)
    a1 = text1.split('\n')
    a2 = text2.split('\n')
    t[2].write(header)
    for i1 in a1:   # Перебирает строки в t[0]
        line_to_all(i1, a2, t, compare_function) # Сравнивать i1 со ВСЕМИ строками из a2. Результат писать в файл t[2].
    t[2].write(footer)

# Сравнивать i1 со ВСЕМИ строками из a2. Результат писать в файл t[2]. global perc - модифицируется!
def line_to_all(i1, a2, t, compare_function):
    found = check_full_match(i1, a2, t)
    if not found: # Если нет полного соответствия строк, то проверяем частичное соответствие. 
        found = check_compare_function(i1, a2, compare_function)  # Модифицирует global perc
        check_max_percent(t) 
    if not found:
        t[2].write(beg_r + i1 + end + '<br>\n')

# 1. Сравнивает строки на полное соответствие. Возвращает найдено или нет. Записывает в t[2]. Вызывается из line_to_all.
def check_full_match(i1, a2, t):
    for i2 in a2:
        if i1 == i2:
            t[2].write(i1 + '<br>\n')
            return True
    return False

# 2. Сравнивает строки на полное соответствие. Возвращает найдено или нет. Вызывается из line_to_all.
def check_compare_function(i1, a2, compare_function):
    global perc
    perc = [] # Массив заполняется [0] совпадающими (в i1 и a2) словами и [1] процентом совпадения с строкой i1.
    found = False
    for i2 in a2:
        match = compare_function(i1, i2)
        if len(match) > 0:
            perc.append(match)
            found = True
            # print 'perc1=', perc
    # print 'perc2=', perc
    return found

# 3. Сравнивает строки на максимальный % соответствия в perc[i][1]. Записывает в t[2]. Вызывается из line_to_all.
def check_max_percent(t):
    global perc
    if len(perc)>1: # Длина массива совпадений perc > 1
        line_index = 0 # Номер (индекс) максимума
        for elem in perc:
            if(elem[1]>elem[line_index]): # Нашли максимум perc[i][1]
                line_index=elem
        print 'line_index=', line_index
        print 'maximum=', perc[line_index][1]
        t[2].write(perc[line_index][0] + '<br>\n')
    elif len(perc)>0: # не выбирая - печатаем единственно возможный 
        t[2].write(perc[0][0] + '<br>\n')
        print "perc[0][0]=", perc[0][0]
            
 
# Анализировать 3 файла
def proceed(file_list, compare_function):
    descriptor_list = open_files(file_list)
    analysis(descriptor_list, compare_function)  # Сравнивает t[0] с t[1]. Формирует t[2].
    close_files(descriptor_list)
 
 
# Сравнение канонического CANON с вариантами из SOURCE_PATH . Требует наличия и файла, и папки
perc=[]
lst = os.listdir(SOURCE_PATH)
if '.DS_Store' in lst:          # фикс скрытого файла изменения папки в MacOS
    lst.remove('.DS_Store')
print 'Канонический вариант', CANON.split('/')[1], 'сравнивается с вариантами в папке', \
    SOURCE_PATH.split('/')[1], ' : ', lst
for q in range(0, len(lst)): # Сравнивает вариант t[0] с каноном t[1]. Но не наоборот. Формирует t[2].
    proceed([SOURCE_PATH+'/'+lst[q], CANON, (lst[q].split('.'))[0]+'.html'], compare)
