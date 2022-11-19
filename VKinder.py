from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import requests
import DBase


class User:
    with open("token2.txt", "r") as f:
        token = f.readline().strip()
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
        self.userlist = DBase.consult_db()
    def get_search_criteria(self):
        params = {
            'access_token': self.token,
            'city': self.get_info['response'][0]['city']['id'],
            'relation': '6',
            'count': '5',
            'online': '1',
            'offset': 0,
            'age_from': self.get_age(self.id, "Укажи минимальный возраст твоей идеальной половинки"),
            # через общение с ботом просим ввести желаемый возраст
            'age_to': self.get_age(self.id, "И каков твой максимальный порог?"),
            'sex': self.get_sex(self.id, "Кто тебя интересует: мужчины или женщины?"),
            'has_photo': '1',
            'can_access_closed': False,
            'v': '5.131'
        }
        return params
    def get_age(self, id, message):
        bot.write_msg(self.id, message)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                request = event.text
                try:
                    request = int(event.text)
                except:
                    bot.write_msg(id, "Введи возраст цифрами")
                else:
                    return request
    def get_sex(self, id, message):
        bot.write_msg(id, message)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    request = event.text.lower()
                    if request == 'мужчины' or request == 'парни':
                        bot.write_msg(main_user.id, "Cекунду, ищу совпадения :)")
                        return 2
                    elif request == 'женщины' or request == 'девушки':
                        bot.write_msg(main_user.id, "Cекунду, ищу совпадения :)")
                        return 1
                    else:
                        bot.write_msg(main_user.id, "Прости, мне кажется, я не понял твоего ответа...")
                        self.get_sex(id, "Так все же парни или девушки?")
                        continue
    def get_userlist(self, params):
        response = requests.get("https://api.vk.com/method/users.search", params=params).json()
        result = []
        for profile in response['response']['items']:
            if profile['id'] not in self.userlist:
                result.append(profile)
        return result

class Bot:
    def write_msg(self, user_id, message):
        params = {
            'user_id': user_id,
            'message': message,
            'random_id': randrange(10 ** 7)
        }
        vk.method('messages.send', params)
    def send_basic_msg(self, user):
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    request = event.text.lower()

                    if request == "старт":
                        self.write_msg(user, f"Хай, {main_user.name}."
                                  f"\nДля начала я задам тебе пару вопросов :)")
                        return True

                    elif request == "пока":
                        self.write_msg(user, "Пока((")
                        return False
                    else:
                        self.write_msg(user, "Привет!Я - бот, который поможет подобрать для тебя вторую половинку! "
                                             "\nЕсли хочешь начать чат, отправь 'СТАРТ'"
                                             "\nЕсли захочешь прервать мою работу, отправь 'СТОП'")
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
        result = requests.get(URL, params).json()
        result = result['response']['items']
        ph_list = sorted(result, key=lambda row: row['likes']['count'])
        bestphotos = ph_list[-1:-4:-1]
        bestphotos = sorted(bestphotos, key=lambda row: row['sizes'][0]['height'])
        # urls = [url['sizes'][-1]['url'] for url in bestphotos]
        ids = [url['id'] for url in bestphotos]
        return ids
    def read_list(self, profile_list, criterias):
        while len(profile_list) !=0:
            for profile in profile_list:
                self.send_profile(profile_list.pop())
                self.write_msg(main_user.id, "Да / Нет")
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW:
                        if event.to_me:
                            request = event.text.lower()
                            if request == "нет":
                                DBase.add_toDB("dislike", profile['user'])
                                break
                            elif request == "да":
                                self.write_msg(main_user.id, f"Лови ссылку на профиль! \nwww.vk.com/id{profile['user']}")
                                DBase.add_toDB("like", profile['user'])
                                break
                            elif request == "стоп":
                                self.write_msg(main_user.id, "Было здорово! Заходи еще!")
                                return
                            else:
                                self.write_msg(main_user.id, 'Прости, я не понял ответа... Да или Нет?')


        else:
            criterias['offset'] += 5
            new = main_user.get_userlist(criterias)
            self.read_list(self.get_profile(new), criterias)
    def send_profile(self, prof):
        profile = (f"Имя: {prof['name']}\nФамилия: {prof['surname']}")
        bot.write_msg(main_user.id, profile)
        photo_list = prof["photos"]
        for pic in photo_list:
            vk.method('messages.send', {'user_id': main_user.id, 'attachment': f"photo{prof['user']}_{pic}",
                                        'random_id': randrange(10 ** 7), })


# открываем сессию и слушаем сервер
with open("token.txt", "r") as f:
    token = f.readline().strip()
#token = "vk1.a.UdjJgt1pq1ObEcx7YW2Q94iFv-GXIvB7BIiSFAwfmsU2spmBZ0MajZ8QOdM9JZSNtLhdiU0VxII6wyz2TUfOWK58kbYsNhOizm_MGPe4975OZvoCVj6Jq0cSm9K8u7D0n3ZBj_oKWjgtEsV4doJNahRu93xQ5hvRx_9tqEFWWwDe220wfKNy5Ck_8DXxkEQO83C8DmEnTC3SsubclAUduQ"
vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)

# создаем 2 объекта для пользователя и для бота
main_user = User()
bot = Bot()
print(main_user.userlist)
# если пользователь начал диалог, то передаем набор критериев, по которым осуществляем первый поиск
if bot.send_basic_msg(main_user.id):
    criterias = main_user.get_search_criteria()
    user_profiles = main_user.get_userlist(criterias)
    profiles = bot.get_profile(user_profiles)
    bot.read_list(profiles, criterias)

