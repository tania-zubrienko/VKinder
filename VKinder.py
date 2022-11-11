from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardButton, VkKeyboardColor
import requests
from pprint import pprint

token = "vk1.a.UdjJgt1pq1ObEcx7YW2Q94iFv-GXIvB7BIiSFAwfmsU2spmBZ0MajZ8QOdM9JZSNtLhdiU0VxII6wyz2TUfOWK58kbYsNhOizm_MGPe4975OZvoCVj6Jq0cSm9K8u7D0n3ZBj_oKWjgtEsV4doJNahRu93xQ5hvRx_9tqEFWWwDe220wfKNy5Ck_8DXxkEQO83C8DmEnTC3SsubclAUduQ"
vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)


class User:
    token = "vk1.a.t2tmoTAN7tSZHcyGXl48BtPj0-LCAYSGVz-uf94_BJNt7KudFPxj2v2AB7dNnqIlyaMnl7kZktU2pfKOs29GjFZ-HWesz7AMzrKcji6ed3W8cqgXuBnY_6PmTiKyVjsHUteLb-nB-f5kZf-vZlqDuph37pkrGg6vFCWUtkU4kBIZRQRW8jqTv3N8jUof84uPN6IX08sldYXzOftLtGpeqA"
    @property
    def get_info(self):
        URL = "https://api.vk.com/method/users.get"
        params = {
            'access_token': self.token,
            'fields': 'first_name,bdate,sex,city,relation',
            'v': '5.131'
        }
        res = requests.get(URL, params=params).json()
        return res

    def __init__(self):
        response = self.get_info['response'][0]
        self.sex = response['sex']
        self.id = response['id']
        self.name = response['first_name']
        self.birthday = response['bdate']
        self.relation = response['relation']
        self.city = response['city']['title']


    def __str__(self):
        return f'Имя пользователя: {self.name}, Дата рождения: {self.birthday}, Город: {self.city}, Семейное положение: {self.relation}'



    def get_userlist(self):
        URL = "https://api.vk.com/method/users.search"
        params = {
            'access_token': self.token,
            'city': self.get_info['response'][0]['city']['id'],
            'relation': '6',
            'age_from': get_age(self.id, "Укажи минимальный возраст твоей идеальной половинки"),      # через общение с ботом просим ввести желаемый возраст
            'age_to': get_age(self.id, "И каков твой максимальный порог? :)"),
            'sex': get_sex(self.id, "Кто тебя интересует: мужчины или женщины?"),
            #'sex': button("Кто тебя интересует: мужчины или женщины?", 'мужчины'),
            'has_photo': '1',
            'can_access_closed': False,
            'v': '5.131'
        }
        print("getuserlist done")
        return requests.get(URL, params=params).json()
class Bot:
    pass
# Шаблон для отправки сообщений
def write_msg(user_id, message, keyboard=None):
    params ={
        'user_id': user_id,
        'message': message,
        'random_id': randrange(10 ** 7)
    }
    if keyboard != None:
        params['keyboard']: keyboard.get_keyboard()
    else:
        params=params
    vk.method('messages.send', params)

def send_profile(prof):
    profile = (f"Имя: {prof['name']}\nФамилия: {prof['surname']}")
    vk.method('messages.send', {'user_id': main_user.id, 'message': profile,  'random_id': randrange(10 ** 7),})
    photo_list = prof["photos"]
    print(photo_list)
    for pic in photo_list:
        vk.method('messages.send', {'user_id': main_user.id, 'attachment': f"photo{prof['user']}_{pic}", 'random_id': randrange(10 ** 7), })


# шаблон для приветствия/прощания
def send_basic_msg(user):
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text.lower()

                if request == "привет":
                    write_msg(event.user_id, f"Хай, {main_user.name}. Я - бот, который поможет подобрать для тебя вторую половинку! "
                                             f"\nДля начала я задам тебе пару вопросов :)")

                elif request == "пока":
                    write_msg(event.user_id, "Пока((")
                else:
                    write_msg(event.user_id, "Не поняла вашего ответа...")
            break

def get_age(id, message):
    write_msg(id, message)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            request = event.text
            try:
                request = int(event.text)
            except:
                write_msg(id, "Введи возраст цифрами")
            else:
                return request

def get_sex(id, message):
    write_msg(id, message)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text.lower()
                if request == 'мужчины' or request == 'парни':
                    return 2
                elif request == 'женщины' or request == 'девушки':
                    return 1
                else:
                    write_msg(event.user_id, "Прости, мне кажется, я не поняла твоего ответа...")
                    get_sex(id, "Так все же парни или девушки?")
                    continue

def button(message, lable):
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            text = event.text

            if text == message:
                keyboard = VkKeyboard(one_time=True)
                keyboard.add_button(label=lable, color=VkKeyboardColor.POSITIVE)
                write_msg(main_user.id, "", keyboard)



def get_photos(user_id):
    URL = "https://api.vk.com/method/photos.getAll"
    params = {
        'access_token': main_user.token,
        'owner_id': user_id,
        'extended': "1",
        'v': "5.131"
        }
    result = requests.get(URL, params).json()
    result = result['response']['items']
    ph_list = sorted(result, key=lambda row: row['likes']['count'])
    bestphotos = ph_list[-1:-4:-1]
    bestphotos = sorted(bestphotos, key=lambda row:row['sizes'][0]['height'])
    # urls = [url['sizes'][-1]['url'] for url in bestphotos]
    urls = [url['id'] for url in bestphotos]

    return urls

def get_profile(profiles):

    for element in profiles['response']['items']:
        try:
            profile = {
                "name": element['first_name'],
                'surname': element['last_name'],
                'photos': get_photos(element['id']),
                'user': element['id']
            }
            print(profile)
            send_profile(profile)
            vk.method('messages.send', {'user_id': main_user.id, 'message': "да/нет?",
                                        'random_id': randrange(10 ** 7), })
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW:
                    if event.to_me:
                        request = event.text.lower()
                        if request == "нет":
                            break
                        else:
                            break

        except:
            continue
        print("----------")



main_user = User()
#pprint(main_user.get_info)
send_basic_msg(main_user)
pprint(get_profile(main_user.get_userlist()))