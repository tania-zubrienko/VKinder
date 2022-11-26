from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import requests
import DBase
import datetime


class User:
    with open("token2.txt", "r") as f:
        token = f.readline().strip()

    def get_info(self, user_id):
        URL = "https://api.vk.com/method/users.get"
        params = {
            'access_token': self.token,
            'user_ids': user_id,
            'fields': 'first_name,bdate,sex,city,relation',
            'v': '5.131'
        }
        res = requests.get(URL, params=params)
        if res:
            return res.json()
        else:
            print("Ошибка в получении данных пользователя")

    def __init__(self, user_id):
        userinfo = self.get_info(user_id)
        if 'response' in userinfo:
            response = userinfo['response'][0]
            try:
                self.sex = response['sex']
                self.id = response['id']
                self.name = response['first_name']
                self.birthday = int(response['bdate'][-4::])
                self.relation = response['relation']
                self.city = response['city']['id']
                self.userlist = DBase.consult_db()
            except:
                print("Не достаточно данных в профиле")
        else:
            print("Ошибка в получении информации о пользователе.")


class Chat:
    def get_search_criteria(self, user):
        params = {
            'access_token': user.token,
            'city': user.get_info['response'][0]['city']['id'],
            'relation': '6',
            'count': '5',
            'online': '1',
            'offset': 0,
            'age_from': self.get_age(user.id, "Укажи минимальный возраст твоей идеальной половинки"),
            'age_to': self.get_age(user.id, "И каков твой максимальный порог?"),
            'sex': self.get_sex(user.id, "Кто тебя интересует: мужчины или женщины?"),
            'has_photo': '1',
            'can_access_closed': False,
            'v': '5.131'
        }
        return params

    def set_search_criteria(self):
        def opposite_sex():
            if main_user.sex == 1:
                return "2"
            elif main_user.sex == 2:
                return "1"
            else:
                return "0"

        params = {
            'access_token': main_user.token,
            'city': main_user.city,
            'relation': '6',
            'count': '5',
            'online': '1',
            'offset': 0,
            'age_from': int(datetime.datetime.now().year) - main_user.birthday - 5,
            'age_to': int(datetime.datetime.now().year) - main_user.birthday + 5,
            'sex': opposite_sex(),
            'has_photo': '1',
            'can_access_closed': False,
            'v': '5.131'
        }
        return params

    def get_age(self, id, message):
        self.write_msg(id, message)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                try:
                    request = int(event.text)
                except:
                    self.write_msg(id, "Введи возраст цифрами")
                else:
                    return request

    def get_sex(self, id, message):
        self.write_msg(id, message)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    request = event.text.lower()
                    if request == 'мужчины' or request == 'парни':
                        self.write_msg(event.user_id, "Cекунду, ищу совпадения :)")
                        return 2
                    elif request == 'женщины' or request == 'девушки':
                        Chat.write_msg(event.user_id, "Cекунду, ищу совпадения :)")
                        return 1
                    else:
                        self.write_msg(event.user_id, "Прости, мне кажется, я не понял твоего ответа...")
                        self.get_sex(id, "Так все же парни или девушки?")
                        continue

    def write_msg(self, user_id, message):
        params = {
            'user_id': user_id,
            'message': message,
            'random_id': randrange(10 ** 7)
        }
        vk.method('messages.send', params)

    def send_basic_msg(self):
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    self.write_msg(event.user_id,
                                   "Привет!Я - бот, который поможет подобрать для тебя вторую половинку! "
                                   "\nЕсли захочешь прервать мою работу, отправь 'СТОП'")
                    return event.user_id


class Searcher:
    def get_userlist(self, params):
        response = requests.get("https://api.vk.com/method/users.search", params=params).json()
        if response:
            result = []
            for profile in response['response']['items']:
                if profile['id'] not in main_user.userlist:
                    result.append(profile)
            return result
        else:
            print("список анкет не получен")
            return False

    def get_profile(self, profiles):
        profile_list = []
        for element in profiles:
            try:
                profile = {
                    "name": element['first_name'],
                    'surname': element['last_name'],
                    'photos': self.get_photos(element['id']),
                    'user': element['id']
                }
                profile_list.append(profile)
            except:
                continue
        return profile_list

    def get_photos(self, user):
        URL = "https://api.vk.com/method/photos.getAll"
        params = {
            'access_token': main_user.token,
            'owner_id': user,
            'extended': "1",
            'v': "5.131"
        }
        result = requests.get(URL, params)
        if result:
            result = result.json()['response']['items']
            ph_list = sorted(result, key=lambda row: row['likes']['count'])
            bestphotos = ph_list[-1:-4:-1]
            bestphotos = sorted(bestphotos, key=lambda row: row['sizes'][0]['height'])
            ids = [url['id'] for url in bestphotos]
            return ids
        else:
            print("Ошибка в получении фото")
            return False

    def read_list(self, profile_list, criterias):
        while len(profile_list) != 0:
            for profile in profile_list:
                self.send_profile(profile_list.pop())
                chat.write_msg(main_user.id, "Да / Нет")
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW:
                        if event.to_me:
                            request = event.text.lower()
                            if request == "нет":
                                DBase.add_toDB("dislike", profile['user'])
                                break
                            elif request == "да":
                                chat.write_msg(main_user.id,
                                               f"Лови ссылку на профиль! \nwww.vk.com/id{profile['user']}")
                                DBase.add_toDB("like", profile['user'])
                                break
                            elif request == "стоп":
                                chat.write_msg(main_user.id, "Было здорово! Заходи еще!")
                                return
                            else:
                                chat.write_msg(main_user.id, 'Прости, я не понял ответа... Да или Нет?')
        else:
            criterias['offset'] += 5
            new = self.get_userlist(criterias)
            self.read_list(self.get_profile(new), criterias)

    def send_profile(self, prof):
        profile = f"Имя: {prof['name']}\nФамилия: {prof['surname']}"
        chat.write_msg(main_user.id, profile)
        photo_list = prof["photos"]
        for pic in photo_list:
            vk.method('messages.send', {'user_id': main_user.id, 'attachment': f"photo{prof['user']}_{pic}",
                                        'random_id': randrange(10 ** 7), })


# открываем сессию и слушаем сервер
with open("token.txt", "r") as f:
    token = f.readline().strip()
vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)

# создаем 2 объекта для бота
chat = Chat()
bot_logic = Searcher()

# если пользователь начал диалог, то создаем объект класса User
user = chat.send_basic_msg()
main_user = User(user)

# передаем набор критериев, по которым осуществляем первый поиск
criteria = chat.set_search_criteria()

# передаем параметры поиска для получения списка анкет
user_profiles = bot_logic.get_userlist(criteria)

# получаем список анкет для показа, обработав возможные совпадения в базе
profiles = bot_logic.get_profile(user_profiles)

# читаем список, показывая анкеты и записывая их в базу
bot_logic.read_list(profiles, criteria)
