import urllib.request
import json
import re
from datetime import date
from flask import Flask
from flask import render_template , request
from pymorphy2 import MorphAnalyzer
morph = MorphAnalyzer()




app = Flask(__name__)

def name_search(token, owner_id):
    line = 'https://api.vk.com/method/users.get?user_ids=' + owner_id + '&v=5.74&access_token='  + token
    data = requesting(line)
    print(data)
    if data['response'] == []:
        return 'этот пользователь'
    else:
        return data['response'][0]['first_name']

def home_town_search(owner_id, token):
    line = 'https://api.vk.com/method/users.get?user_ids=' + owner_id + '&fields=home_town&v=5.74&access_token='  + token
    data = requesting(line)
    if data['response'] == []:
        return 'не указан'
    if ('home_town' in data['response'][0]) and data['response'][0]['home_town'] != '':
        return data['response'][0]['home_town']
    else:
        return 'не указан'

def age_search (owner_id, token):
    line = 'https://api.vk.com/method/users.get?user_ids=' + owner_id + '&fields=bdate&v=5.7&access_token=' + token
    data = requesting(line)
    if data['response'] == []:
        return 'не указан'
    if 'bdate' in data['response'][0]:
        if len(data['response'][0]['bdate']) > 5:
            today = date.today()
            born = data['response'][0]['bdate'].split('.')
            return today.year - int(born[2]) - ((today.month, today.day) < (int(born[1]), int(born[0])))
        else:
            return 'не указан'
    else:
        return 'не указан'

def friends_search(owner_id, token):
    line = 'https://api.vk.com/method/friends.get?user_id=' + owner_id + '&fields=name&v=5.7&access_token=' + token
    data = requesting(line)
    if data['response'] == []:
        return 'не указано '
    else:
        return str(data['response']['count'])

def occupation_search (owner_id, token): #род_деятельности
    line = 'https://api.vk.com/method/users.get?user_ids=' + owner_id + '&fields=occupation&v=5.7&access_token=' + token
    data = requesting(line)
    if data['response'] == []:
        return 'не указан '
    if 'occupation' in data['response'][0]:
        return data['response'][0]['occupation']['name']
    else:
        return 'не указан'

def keywords_search (owner_id, token):
    line = 'https://api.vk.com/method/wall.get?owner_id=' + owner_id + '&count=10&v=5.7&access_token=' + token
    data = requesting(line)
    if 'error' in data:
        return 'информация о стене пользователя не доступна'
    print(data)
    discurs =''
    for i in range(0, len(data['response']['items'])):
        discurs += data['response']['items'][i]['text']
    d = frequency(discurs)
    if d != "none":
         return inflection(d)

    else:
        return "кажется, этот пользователь особо сам ничего не пишет"

def frequency(discurs):
    d = {}
    if discurs != '':
        discurs = discurs.split( )
        for word in discurs:
            m = re.search ('', word)
            if m.group(0) != 'None':
                ana = morph.parse(word)
                word = ana[0].normalized
                if (word.tag.POS == 'NOUN') or (word.tag.POS == 'INFN')or (word.tag.POS == 'ADJF') or (word.tag.POS == 'ADJS') or (word.tag.POS == 'PRTF') or (word.tag.POS == 'PRTS') or (word.tag.POS == 'ADVB'):
                    if word not in d:
                        d[word] = 1
                    else:
                        d[word] += 1
        return d
    else:
        return "none"

def inflection(d):
        vowels = ['у', 'а', 'о', 'э', 'и']
        values = sorted(d, key=d.get, reverse=True)[:10]
        # согласовываем с предлогом  "о"
        line = 'Этот пользователь пишет'
        for value in values:
            if value.tag.POS == 'INFN':
                value = "том, чтобы" + " " + value.word
            elif (value.tag.POS == 'NOUN') or (value.tag.POS == 'ADJF') or (value.tag.POS == 'ADJS') or (
                value.tag.POS == 'PRTF') or (value.tag.POS == 'PRTS'):
                # все прилагательные стоят в форме муж. рода, нам нужен средний (говорит о вечном). однако в Пр. падеже средний и мужской всегда совпадают
                word = morph.parse(value.word)[0]
                print(word)
                word = word.inflect({'plur'})
                print(word)
                value = value.inflect({'loct'})
                value = value.word
            else:
                value = value.word
            if value[0] in vowels:
                line = line + ' об ' + value + ','
            else:
                line = line + ' о ' + value + ','
        return line[:-1] #убираем последнюю запятую

def requesting(line):
    req = urllib.request.Request(line)
    response = urllib.request.urlopen(req)
    result = response.read().decode('utf-8')
    data = json.loads(result)
    return data


def digital_id(id, token):
    m = re.search ('(https://)?(vk.com/)?(.*)', str(id))
    if m.group(3) != 'None':
                if (str(m.group(3))[:2] == 'id') and (re.search('[\w]',str(m.group(3))[2:]) == 'None'):
                    return str(m.group(3))
                else:
                    line = 'https://api.vk.com/method/utils.resolveScreenName?screen_name=' + str(m.group(3)) + '&v=5.7&access_token=' + token
                    dig_id = requesting(line)
                    return str(dig_id['response']['object_id'])
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result')
def result():
    token = '21d1226521d1226521d12265c221b23843221d121d122657acc6ba4a4ef173beef689f5'
    if request.args:
        owner_id = request.args['id']
        owner_id = digital_id(owner_id, token)
        name = name_search(token, owner_id)
        home_town = home_town_search(owner_id, token)
        age = age_search(owner_id, token)
        friends = friends_search(owner_id, token)
        occupation = occupation_search(owner_id, token)
        keywords = keywords_search(owner_id, token)
        return render_template('result.html', name = name, home_town = home_town, age=age,friends =friends, occupation =occupation, keywords =keywords  )


if __name__ == '__main__':
    import os
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)