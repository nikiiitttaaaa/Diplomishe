# импорты
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from datetime import datetime
from config import community_token, access_token, db_url_object
from core import VkTools
from data_store import DataBase


class BotInterface():
    def __init__(self,comunity_token, acces_token):
        self.interface = vk_api.VkApi(token=comunity_token)
        self.api = VkTools(acces_token)
        self.longpoll = VkLongPoll(self.interface)
        self.database = DataBase(db_url_object)
        self.params = None
        self.worksheets = []
        self.offset = 0

    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                                {'user_id': user_id,
                                'message': message,
                                'attachment': attachment,
                                'random_id': get_random_id()
                                }
                                )

    def get_data_about_user(self, event):

        if self.params['name'] is None:
            self.message_send(event.user_id, 'Введите имя и фамилию:')
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    return event.text

        elif self.params['sex'] is None:
            self.message_send(event.user_id, 'Введите пол (1-м, 2-ж):')
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    return int(event.text)

        elif self.params['city'] is None:
            self.message_send(event.user_id, 'Введите город, в котором проживаете:')
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    return event.text

        elif self.params['year'] is None:
            self.message_send(event.user_id, 'Введите дату рождения в формате (дд.мм.гггг):')
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    return datetime.now().year - int(event.text.split('.')[2])

    def get_data_from_db(self, worksheet):
        data = self.database.select_from_db()
        flag = False
        for i in data:
            if i[1] == worksheet['id']:
                flag = True
                break
            else:
                flag = False
        return flag

    def event_handler(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()

                if command == 'привет':
                    self.params = self.api.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'Приветствую, {self.params["name"]}!')
                    # Проверка на недостающие данные
                    for i in self.params:
                        if self.params[i] is None:
                            self.params[i] = self.get_data_about_user(event)

                elif command == 'поиск':
                    self.message_send(
                        event.user_id, 'Начинаем поиск')
                    while True:
                        if self.worksheets:
                            worksheet = self.worksheets.pop()

                            data_flag = self.get_data_from_db(worksheet)
                            if data_flag is False:

                                self.database.insert_in_db(event.user_id, worksheet['id'])
                                break
                        else:
                            self.worksheets = self.api.search_worksheet(
                                self.params, self.offset)

                    photos = self.api.get_photos(worksheet['id'])
                    self.offset += 10

                    photo_string = ''
                    for photo in photos:
                        photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'

                    self.message_send(
                        event.user_id,
                        f'имя: {worksheet["name"]} ссылка: vk.com/id{worksheet["id"]}',
                        attachment=photo_string
                    )
                elif command == 'пока':
                    self.message_send(event.user_id, 'До новых встреч!')
                else:
                    self.message_send(event.user_id, 'Неизвестная команда')


if __name__ == '__main__':
    bot = BotInterface(community_token, access_token)
    bot.event_handler()

            

