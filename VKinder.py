import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange

token = "vk1.a.UdjJgt1pq1ObEcx7YW2Q94iFv-GXIvB7BIiSFAwfmsU2spmBZ0MajZ8QOdM9JZSNtLhdiU0VxII6wyz2TUfOWK58kbYsNhOizm_MGPe4975OZvoCVj6Jq0cSm9K8u7D0n3ZBj_oKWjgtEsV4doJNahRu93xQ5hvRx_9tqEFWWwDe220wfKNy5Ck_8DXxkEQO83C8DmEnTC3SsubclAUduQ"

vk = vk_api.VkApi(token=token)
session = vk.get_api()
longpoll = VkLongPoll(vk)


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7),})


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text

            if request == "привет":
                write_msg(event.user_id, f"Хай, {event.user_id}")
            elif request == "пока":
                write_msg(event.user_id, "Пока((")
            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")

