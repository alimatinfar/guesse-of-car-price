import re
from bs4 import BeautifulSoup
import requests
import mysql.connector
from sklearn import tree

r = requests.get('https://bama.ir/car')

soup = BeautifulSoup(r.text, 'html.parser')

name = soup.find_all('select', attrs={'name':'selectedTopBrand'})

res = re.findall(r'<option value=".+,(.+)">(.+)</option>', str(name[0]))# اولی:اسم لاتین ماشین. دومی:اسم فارسی ماشین

while True:
    l = []
    a = dict()

    for i in range (0, len(res)):
        a[str(res[i][1]).strip()] = str(res[i][0]) #دیکشنری اسم فارسی
        l.append(res[i][1].strip()) 
        print (res[i][1].strip())


    x = input('لطفا برند مورد نظر را از لیست بالا وارد بفرمایید:  ')
    while True:
        if not x in l:
            x = input('برند وارد شده موجود نیست لطفا دوباره برند را وارد بفرمایید: ')
        if x in l:
            break

    m0 = requests.get('https://bama.ir/car/%s' %(a[x]))#جهت گرفتن مدلها
    soup0 = BeautifulSoup(m0.text, 'html.parser')
    model1 = soup0.find_all('li')
    res1 = re.findall(r'<li class=.+id="model.+">\s+<a href="/car/.+/(.+)">\s+<span class="navigation-name">(.+)</span>', str(model1))
    
    j = 'no'
    h = []
    b = dict()
    if res1 != []:#اگر res1 یک لیست خالی باشد به این معناست که برند مورد نظر فقط یک مدل دارد بنابراین میتوان در همان صفحه ی برند جستجو کرد
        for i in range (0, len(res1)):
            h.append(res1[i][1].strip())
            b[str(res1[i][1]).strip()] = str(res1[i][0])
            print(res1[i][1].strip())
        j = 'yes'
        y = input('لطفا مدل مورد نظر را از لیست بالا وارد بفرمایید: ')
        while True:
            if not y in h:
                y = input('مدل وارد شده موجود نیست لطفا مدل را دوباره وارد بفرمایید: ')
            if y in h:
                break
    sa = int(input('لطفا سال تولید را وارد بفرمایید: '))
    ka = int(input('لطفا کارکرد را وارد بفرمایید: '))
    if j == 'yes':
        m1 = requests.get('https://bama.ir/car/%s/%s?page=1' %(a[x], b[y]))
        soup1 = BeautifulSoup(m1.text, 'html.parser')
    if j == 'no':
        res1 = re.findall(r'<li class="" id="model-0">\s+<span class="single-data-rightnavigation">\s+<span class="navigation-name">همه (.+)</span>', str(model1))
        m1 = requests.get('https://bama.ir/car/%s' %(a[x]))
        soup1 = BeautifulSoup(m1.text, 'html.parser')
        print ('فقط یک مدل دارد : %s'%(res1[0]))

    page = soup1.find_all('h4')
    res2 = re.findall(r'<h4>صفحه \d+ \[ \d+ تا \d+ از (.+) \]</h4>', str(page))#تعداد اگهی های موجود برای برند و مدل انتخاب شده
    
    f = 0

    if res2 == []:
        c = 1
    if res2 != []:
        res2[0] = re.sub(r',','', str(res2[0]))
        s = int(res2[0])//12
        if s >= 40:
            c = 40
        if s < 40:
            if (int(res2[0])%12) == 0:
                c = s
            elif (int(res2[0])%12) != 0:
                c = s + 1
    for i in range(0, c):
        if j == 'yes':
            m1 = requests.get('https://bama.ir/car/%s/%s?page=%i' %(a[x], b[y], i+1))
            soup1 = BeautifulSoup(m1.text, 'html.parser')
        if j == 'no':
            m1 = requests.get('https://bama.ir/car/%s?page=%i' %(a[x], i+1))
            soup1 = BeautifulSoup(m1.text, 'html.parser')
        
        karkard1 = soup1.find_all('p', attrs={'class':'price hidden-xs'})
        gheymat1 = soup1.find_all('p', attrs={'class':'cost'})

        sal = soup1.find_all('h2', attrs = {'class':'persianOrder'})
        e = []
        e1 = []
        for i in sal:
            e.append(re.sub(r'\s+','', i.text))
        for i in e:
            e1.append(re.findall(r'(\d+).+', str(i)))

        l1 = []
        for i in karkard1:
            res2 = re.findall(r'کارکرد (.+) کیلومتر', i.text)
            if res2 == ['صفر']:
                l1.append('0')
            elif res2 == []:
                l1.append('invalid')
            elif res2 != []:        
                l1.append(res2[0])

        g1 = []
        for i in gheymat1:
            res2 = re.findall(r'(.+) تومان', i.text)
            if res2 == []:
                g1.append('invalid')
            else:
                g1.append(res2[0])

        cnx = mysql.connector.connect(user='root', password='201747mat', host='127.0.0.1', database='test')
        cursor = cnx.cursor()
        
        for i in range (0, len(g1)):
            if g1[i] != 'invalid':
                if l1[i] != 'invalid':
                    cursor.execute('INSERT INTO machin1 VALUES(\'%s %s\', \'%s\',\'%s\', \'%s\')' %(x, y, e1[i][0], l1[i], g1[i]))
                    cnx.commit()
                    f += 1#تعداد داده های ذخیره شده در دیتابیس
    if f < 30:
        print ('تعداد داده های برند و مدل انتخاب شده کافی نیست لطفا برند و مدل دیگری وارد بفرمایید!')
        cnx = mysql.connector.connect(user='root', password='201747mat', host='127.0.0.1', database='test')
        cursor = cnx.cursor()
        cursor.execute('DELETE FROM machin1;')
        cnx.commit()
    elif f >= 30:
        break

cursor.execute('SELECT * FROM machin1')
q = []
w = []
for (x , y, z, k) in cursor:
    q.append([y,re.sub(',','',z)])
    w.append(re.sub(',','',k))

for i in range(0, len(q)):
    q[i][0] = int(q[i][0])
    q[i][1] = int(q[i][1])
    w[i] = int(w[i])

clf = tree.DecisionTreeClassifier()
clf = clf.fit(q,w)

new_data = [[sa, ka]]
answer = clf.predict(new_data)

print('قیمت حدودی ماشین برابر است: %i' %(answer[0]))

