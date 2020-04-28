from time import time as timer
import time
import vk
import re
import random
from selenium import webdriver
from bs4 import BeautifulSoup
from bisect import bisect
from numpy.ma.core import log

#Неактуальный устаревший парсер групп
def parse(file_in, file_out, class_number=1):
    driver = webdriver.Firefox()
    options = webdriver.FirefoxOptions()
    options.add_argument('headless')
    cin = open(file_in, 'r', encoding='utf-8')
    cout = open(file_out, 'w', encoding='utf-8')
    line = cin.readline()
    while line:
        driver.get(line)
        try:
            driver.find_elements_by_xpath("//*[contains(text(),'Подписки')]")[0].click()
        except:
            line = cin.readline()
            continue
        str = [line[0:len(line) - 1] + "; "]
        publics = []
        k = 0
        while len(publics) == 0:
            requiredHtml = driver.page_source
            soup = BeautifulSoup(requiredHtml, "html5lib")
            publics = soup.find_all(class_ = 'fans_idol_lnk', limit=30)
            k += 1
            if(k > 5):
                break
        for p in publics:
            try:
                str.append(p.contents[0] + "; ")
            except:
                continue
        #str.append(class_number)
        str.append("\n")
        res = "".join(str)
        cout.write(res)
        line = cin.readline()
    cin.close()
    cout.close()
    driver.close()

#Получение айдишников подписчиков группы по id
def get_members(groupid):
    first = vk_api.groups.getMembers(group_id=groupid, v=5.92) 
    data = first["items"] 
    count = first["count"] // 1000 
    for i in range(1, count+1):  
        data = data + vk_api.groups.getMembers(group_id=groupid, v=5.92, offset=i*1000)["items"]
    return data

#сохранение данных в файл
def save_data(data, filename="data.txt"): 
    with open(filename, "w", encoding='utf-8') as file: 
        for item in data:   
            file.write(str(item) + "\n") 

#выгрузка данных из файла
def enter_data(filename="data.txt"): 
    with open(filename, 'r', encoding='utf-8') as file: 
        b = [] 
        for line in file:   
            k = []
            s = line[1:-2].split('\'')
            k.append(int(s[0][0:-2]))  
            k.append(s[1])
            k.append(int(s[-1][1:len(s[-1])]))
            b.append(k)
    return b

#пересечение множеств
def get_intersection(group1, group2):
    group1 = set(group1)  
    group2 = set(group2)  
    intersection = group1.intersection(group2)
    return list(intersection)

#объединение множеств
def get_union(group1, group2):
    group1 = set(group1)  
    group2 = set(group2)  
    union = group1.union(group2) 
    return list(union) 

#предобработка списка групп пользователей из файла (исправить)
def preprocessing(file_in, file_out):
    cin = open(file_in, 'r', encoding='utf-8')
    cout = open(file_out, 'w', encoding='utf-8')
    cities = open('files/city.txt', 'r', encoding='utf-8')
    line = cin.readline()
    while line:
        s = line.split(';')
        if not len(s) == 2:
            for i in range(1, len(s) - 1):
                s[i] = s[i].lower()
                s[i] = re.sub(r'\s+', '', s[i])
                s[i] = re.sub(r'[^a-zA-Zа-яА-Я ]', '', s[i])
                s[i] += ";"
                line = cities.readline().lower()
                while line:
                    if s[i].find(line) > -1:
                        s[i] = ""
                        break
                    line = cities.readline().lower()
            s[0] = s[0] + ';'
            s[-1] = re.sub(r'\s+', '', s[-1])
            s[-1] += '\n'
            str = ''.join(s)
            cout.write(str)
        line = cin.readline()
    cin.close()
    cout.close()

#перемешивание данных из файлов
def shake_files(file_in_1, file_in_2, file_out):
    file1 = open(file_in_1, 'r', encoding='utf-8')
    file2 = open(file_in_2, 'r', encoding='utf-8')
    cout = open(file_out, 'w', encoding='utf-8')
    line = file1.readline()
    while line:
        cout.write(line)
        if(random.random() < 0.5):
            line = file1.readline()
        else:
            line = file2.readline()
    if file1.readline():
        line = file1.readline()
        while line:
            cout.write(line)
            line = file1.readline()
    elif file2.readline(): 
        line = file2.readline()
        while line:
            cout.write(line)
            line = file2.readline()

#словарь для классификатора
def get_dictionary(path, count_of_docs):
    dic = set()
    with open(path, "r", encoding="utf-8") as file:
        k = 0
        while k < count_of_docs:
            line = file.readline()
            tokens = line.split(';')
            for i in range(1, len(tokens) - 1):
                dic.add(tokens[i])
            k += 1
        s = list(dic)
        s.sort()
    return s

#обучение классификатора
def learning(classes, documents_path, count, count_skip):
    p_c = []
    p_c_count = []
    for i in range(0, len(classes)):
        p_c.append(0)
        p_c_count.append(0)
    with open(documents_path, "r", encoding="utf-8") as file:
        # count class prior
        itt = 0
        skiper = 0
        while skiper < count_skip:
            file.readline()
            skiper += 1
        while itt < count:
            line = file.readline().replace("\n", "").split(';')
            class_num = int(line[-1])
            if class_num <= 0:
                class_num = 0
            p_c_count[class_num] += 1
            itt += 1
        for i in range(0, len(p_c)):
            p_c[i] = p_c_count[i] / count
    dictionary = get_dictionary(documents_path, count)
    
    return dictionary, classes, p_c, p_c_count

#получение списка признаков для словаря по мультиномиальному методу
def get_frec_multinomial(dictionary, path, count):
    frec = []
    for word in dictionary:
        frec.append([word, 0, 0])
    with open(path, "r", encoding="utf-8") as file:
        for i in range(0, count):
            line = file.readline().replace("\n", "")
            strings = line.split(';')
            for j in range(1, len(strings) - 1):
                itt = bisect(dictionary, strings[j], 0, len(dictionary)) - 1
                class_num = int(strings[-1])
                if class_num <= 0:
                    class_num = 1
                else:
                    class_num = 2
                if itt >= 0:
                    frec[itt][class_num] += 1
    return frec 

#Наивный байесовский классификатор
def classify(classifier, frec, document):
    dictionary, classes, p_c, p_c_count = classifier
    words = document.split(';')
    score = []
    for ck in range(0, len(classes)):
        score.append(log(p_c[ck]))
        for i in range(1, len(words)):
            index = bisect(dictionary, words[i], 0, len(dictionary)) - 1
            # laplass
            arg = (frec[index][ck + 1] + 1) / (p_c_count[ck] + len(dictionary))
            score[ck] += log(arg)
    value = max(score)
    return classes[score.index(value)]

#тестирование классификатора (мусор)
def testing():
    classes = [0, 1]
    path = 'files/mistake_dataset_withoutcities.txt'
    #path = 'files/mistake_dataset.txt'
    count = 1000
    count_skip = 2000
    classifier = learning(classes, path, count, count_skip)
    dictionary = classifier[0]
    frec_multinomial = get_frec_multinomial(dictionary, path, count)
    cin = open(path, 'r', encoding='utf-8')
    line = cin.readline()
    count_all = 0
    count_true = 0
    while line:
        count_all += 1
        rate = classify(classifier, frec_multinomial, line)
        r_num = int(line.replace('\n', '').split(';')[-1])
        if(rate == r_num):
            count_true += 1
        line = cin.readline()
    print(count_true/count_all)

#фильтрация юзеров по признаку: в топ-30 подписках есть группы по программированию
def filter(file_in, file_out):
    current = ['Программист', 'программист']
    cin = open(file_in ,'r', encoding='utf-8')
    cout = open(file_out, 'w', encoding='utf-8')
    line = cin.readline()
    while line:
        st = line.split(';')
        for i in range(1, len(st)):
            if not st[i].find(current[0])*st[i].find(current[1]) == 1:
                cout.write(line)
                break
        line = cin.readline()
    
#парсер списка групп пользователей (айдишники в file_in)
def superparser(file_in, file_out):
    cin = open(file_in, 'r', encoding='utf-8')
    cout = open(file_out, 'w', encoding='utf-8')
    line = cin.readline()
    succes = 0
    while line:
        st = [line[17:-1] + ';']
        line = int(line[17:-1])
        try:
            sub = vk_api.users.getSubscriptions(user_id=line, extended=1, count=30, v=5.92)
        except:
            line = cin.readline()
            continue
        for t in sub['items']:
            try:
                st.append(t['name'] + ';')
            except:
                continue
        st.append('\n')
        cout.write(''.join(st))
        succes += 1
        line = cin.readline()
    cin.close()
    cout.close()
    print('success')

#получение живых подписчиков группы
def getTrueUsersCount(group_id):
    itt = vk_api.groups.getMembers(group_id=group_id, v=5.92)['count'] // 1000
    count = 0
    for i in range(0, itt+1):
        data = vk_api.groups.getMembers(group_id=group_id, v=5.92, offset=i*1000)['items']
        users = vk_api.users.get(user_ids=data, v=5.92)
        for user in users:
            try:
                user['deactivated']
            except:
                count += 1
    return count

#получение лайков, комментов, репостов и просмотров на последних count записях группы
def getLCRV(group_id, count):
    res = vk_api.wall.get(domain=group_id, count=count, v=5.92)
    resultSet = []
    for post in res['items']:
        p = []
        p.append(str(post['likes']['count']))
        p.append(str(post['comments']['count']))
        p.append(str(post['reposts']['count']))
        p.append(str(post['views']['count']))
        resultSet.append(p)
    return resultSet

#поиск групп по ключевому слову
def search(keyword, count):
    res = []
    groups = vk_api.groups.search(q=keyword, sort=0, count=count, v=5.9)['items']
    stoper = 1
    tic = timer()
    for group in groups:
        p = []
        stoper += 1
        id = group['id']
        if(stoper % 3 == 0):
            time.sleep(1)
        try:
            count_members = vk_api.groups.getMembers(group_id=id, v=5.9)['count']
            if(count_members < 2000):
                continue
        except:
            continue
        p.append(id)
        p.append(group['name'])
        p.append(count_members)
        res.append(p)
    toc = timer()
    print(toc-tic)

    res.sort(key=lambda list: list[2], reverse=True) 
    return res


if __name__ == '__main__':
    """
    token = "dca35078dca35078dca35078d8dcd21bcdddca3dca35078823cbbd86c8f9b80a31e49a6"
    session = vk.Session(access_token=token)
    vk_api = vk.API(session)
    vk_api.auth()
    """
    session = vk.AuthSession(app_id=7424949, user_login=89088641931, user_password='Rustam120100!')
    vk_api = vk.API(session)

