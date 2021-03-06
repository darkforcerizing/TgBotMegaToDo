import telebot
from DBwork import DBwork
import flask
import json


def getUserId(message):
    user_id = message.from_user.id
    return user_id


def getCommand(message):
    m = message.text
    par = m.split(' ')
    mcom = par[0]
    if mcom[0] == '/':
        command = mcom
    else:
        command = '-'
    return command


def getMessage(message):
    m = message.text
    par = m.split(' ')
    mcom = par[0]
    if mcom[0] != '/':
        mes = ' '.join(par)
    else:
        i = par.pop(0)
        mes = ' '.join(par)
    return mes


def isAuthorized(user_id):
    for i in authUsers:
        if not authUsers[i][user_id] and authUsers[i][user_id] != '':
            return True
    return False


def getToken(user_id):
    for i in authUsers:
        if not authUsers[i][user_id]:
            return authUsers[i][user_id]
    return ''


def taskOutput(dct):
    lst = []
    for i in dct['tasks']:
        lst.append('id: ' + str(i['id']))
        lst.append('title: ' + i['title'])
        lst.append('дата создания: ' + i['creation_date'])
        
        if i['deadline'] is None:
            lst.append('до: не указано')
        else:
            lst.append('до: ' + str(i['deadline']))
            
        if i['description'] is None:
            lst.append('описание: не указано')
        else:
            lst.append('описание: ' + str(i['description']))
            
        if i['complete'] is False:
            lst.append('выполнено')
        else:
            lst.append('не выполнено')
            
        lst.append('')
        tx = '\n'.join(lst)
        return tx


bot = telebot.TeleBot('5134643212:AAEEpmRMTygRHmx61KCPGem7JYo2dhEHHs0')

authUsers = []

HELP_message = 'Вы вызвлали команду "help"\n ' \
    'команда /authorization позволяет авторизоваться пользователю, ' + \
    'необходимо указать через пробел после команды email и пароль для сайта \n'\
    'Лишь после успешной авторизации вам будут доступны следующие функции \n' \
    'команда /delete позволяте безвозвратно удалить задачу\n' \
    'команда /showall позволяет посмотреть все задачи\n' \
    'команда /completed позволяет посмотреть все выполненные задачи\n' \
    'команда /unfulfilled позволяет посмотреть все невыполненные задачи \n' \
    'команда /changestatus позволяет изменить статус задачи \n' \
    'команда /deletecomp позволяет удалить все выполненные задачи\n' 


@bot.message_handler(commands=['help'])
def help(message, res=False):
    bot.send_message(message.chat.id, HELP_message)
    errorsLst = DBwork.addToDB(getUserId(message), getCommand(message),
                               getMessage(message))
    print(errorsLst)


@bot.message_handler(commands=["start"])
def start(message, res=False):
    errorsLst = DBwork.addToDB(getUserId(message), getCommand(message),
                               getMessage(message))
    bot.send_message(message.chat.id, 'Я на связи.' +
                     'Для того чтобы узнать мои воозможности, вызовите /help')


@bot.message_handler(commands=['delete'])
def delete(message, res=False):
    errorsLst = DBwork.addToDB(getUserId(message), getCommand(message),
                               getMessage(message))
    if isAuthorized(message.from_user.id) is True:
        m = message.text
        par = m.split(' ')
        target = str(par[1])
        response = requests.delete('http://pipeweb.ru/api/task/delete',
                                   headers={'authorization': 'Bearer ' +
                                            getToken(message.from_user.id)},
                                   json={'title': target})
    else:
        bot.send_message(message.chat.id, 'Пoльзователь не авторизован')


@bot.message_handler(commands=['showall'])
def showall(message, res=False):
    errorsLst = DBwork.addToDB(getUserId(message), getCommand(message),
                               getMessage(message))
    if isAuthorized(message.from_user.id) is True:
        response = requests.get('http://pipeweb.ru/api/users/tasks',
                                headers={'authorization': 'Bearer ' +
                                         getToken(message.from_user.id)})
        res = json.loads(response)
        mess = taskOutput(res)
        bot.send_message(message.chat.id, mess)
    else:
        bot.send_message(message.chat.id, 'ПОльзователь не авторизован')


@bot.message_handler(commands=['completed'])
def completed(message, res=False):
    errorsLst = DBwork.addToDB(getUserId(message), getCommand(message),
                               getMessage(message))
    if isAuthorized(message.from_user.id) is True:
        response = requests.get('http://pipeweb.ru/api/users/tasks',
                                headers={'authorization': 'Bearer ' +
                                         getToken(message.from_user.id)})
        res = json.loads(response)
        lst = []
        for i in res['tasks']:
            if i['complete'] is True:
                lst.append('id: ' + str(i['id']))
                lst.append('title: ' + i['title'])
                lst.append('дата создания: ' + i['creation_date'])
                
                if i['deadline'] is None:
                    lst.append('до: не указано')
                else:
                    lst.append('до: ' + str(i['deadline']))
                    
                if i['description'] is None:
                    lst.append('описание: не указано')
                else:
                    lst.append('описание: ' + str(i['description']))
                    
                if i['complete'] is True:
                    lst.append('выполнено')
                
                lst.append('')
        
        if len(lst) == 0:
            bot.send_message(message.chat.id, 'Нет выполненных задач')
        else:
            tx = '\n'.join(lst)
            bot.send_message(message.chat.id, tx)
    else:
        bot.send_message(message.chat.id, 'ПОльзователь не авторизован')


@bot.message_handler(commands=['unfulfilled'])
def unfulfilled(message, res=False):
    errorsLst = DBwork.addToDB(getUserId(message), getCommand(message),
                               getMessage(message))
    if isAuthorized(message.from_user.id) is True:
        response = requests.get('http://pipeweb.ru/api/users/tasks',
                                headers={'authorization': 'Bearer ' +
                                         getToken(message.from_user.id)})
        res = json.loads(response)
        lst = []
        for i in res['tasks']:
            if i['complete'] is False:
                lst.append('id: ' + str(i['id']))
                lst.append('title: ' + i['title'])
                lst.append('дата создания: ' + i['creation_date'])
                
                if i['deadline'] is None:
                    lst.append('до: не указано')
                else:
                    lst.append('до: ' + str(i['deadline']))
                    
                if i['description'] is None:
                    lst.append('описание: не указано')
                else:
                    lst.append('описание: ' + str(i['description']))
                    
                if i['complete'] is False:
                    lst.append('не выполнено')
                
                lst.append('')
        
        if len(lst) == 0:
            bot.send_message(message.chat.id, 'Нет выполненных задач')
        else:
            tx = '\n'.join(lst)
            bot.send_message(message.chat.id, tx)
    else:
        bot.send_message(message.chat.id, 'ПОльзователь не авторизован')


@bot.message_handler(commands=['changestatus'])
def changestatus(message, res=False):
    errorsLst = DBwork.addToDB(getUserId(message), getCommand(message),
                               getMessage(message))
    complete = False
    if isAuthorized(message.from_user.id) is True:
        m = message.text
        par = m.split(' ')
        title = par[1]
        status = par[2]
        if status == '0' \
            or status == 'F' \
            or status == "False" \
            or status == 'No' \
                or status == 'Нет':
            complete = False
            
        if status == '1' \
            or status == 'T' \
            or status == 'True' \
            or status == 'Yes' \
                or status == 'Да':
            complete = True
            
        response = request.post('http://pipeweb.ru/api/tasks/change',
                                headers={'authorization': 'Bearer ' +
                                         getToken(message.from_user.id)},
                                json={'title': title,
                                      'complete': complete})
    else:
        bot.send_message(message.chat.id, 'ПОльзователь не авторизован')


@bot.message_handler(commands=['0855'])
def hellomaster(message, res=False):
    errorsLst = DBwork.addToDB(getUserId(message), getCommand(message),
                               getMessage(message))
    bot.send_message(message.chat.id, 'hello The Great Master of The Hidden World')


@bot.message_handler(commands=['whoami'])
def whoami(message, res=False):
    errorsLst = DBwork.addToDB(getUserId(message), getCommand(message),
                               getMessage(message))
    user_id = message.from_user.id
    bot.send_message(message.chat.id, 'Вы - ' + str(user_id))


@bot.message_handler(commands=["authorization"])
def authorization(message, res=False):
    errorsLst = DBwork.addToDB(getUserId(message), getCommand(message), 
                               getMessage(message))
    m = message.text
    print(message.text)
    par = m.split(' ')
    email = str(par[1])
    password = str(par[2])
    if len(par) != 3:
        bot.send_message(message.chat.id, 'Указаны неверные данные')
    errorsLsthttp = []
    try:
        response = requests.get('http://pipeweb.ru/api/login',
                                json={"email": email, "password": password})
        print('l')
    except:
        errorsLsthttp.append('Не удалось авторизировать пользователя')
        bot.send_message(message.chat.id, 'Не удалось авторизировать ' +
                         'пользователя')
        print(errorsLsthttp)
        return
    
    res = json.loads(response)
    if not res['token'] or res['token'] == '':
        errorsLsthttp.append('Не удалось авторизировать пользователя.')
        bot.send_message(message.chat.id, 'Не удалось авторизировать ' +
                         'пользователя')
        print(errorsLsthttp)
        return

    bot.send_message(message.chat.id, 'Успешная авторизация')
    authUsers.append({getUserId(message): res['token']})


@bot.message_handler(commands=['deletecomp'])
def deletecomp(message, res=False):
    errorsLst = DBwork.addToDB(getUserId(message), getCommand(message),
                               getMessage(message))
    if isAuthorized(message.from_user.id) is True:
        response = requests.get('http://pipeweb.ru/api/users/tasks',
                                headers={'authorization': 'Bearer ' +
                                         getToken(message.from_user.id)})
        res = json.loads(response)
        lst = []
        for i in res['tasks']:
            if i['complete'] is True:
                lst.append(i['title'])
        for j in lst:
            response = requests.delete('http://pipeweb.ru/api/tasks/delete',
                                       headers={'authorization': 'Bearer ' +
                                                response.json()['token']},
                                       json={"title": str(j)})
    else:
        bot.send_message(message.chat.id, 'ПОльзователь не     авторизован')


bot.polling(none_stop=True, interval=0)
