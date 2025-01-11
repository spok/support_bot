import json
import os.path


class Db:
    def __init__(self):
        self.chats: dict = {}
        self.workspaces: list = []
        self.courses: list = []
        self.admins: dict = {783188960: {"name": "Власов Слава"}}
        self.file_name: str = "db.json"
        if os.path.isfile(self.file_name):
            self.load_db()

    def add_chats(self, id: int, name: str, workspace: str, course: str):
        """Добавление чата"""
        pass
        self.save_db()

    def add_workspaces(self, name: str):
        """Добавление воркспейса"""
        if name not in self.workspaces:
            self.workspaces.append(name)
        self.save_db()

    def del_workspace(self, name: str):
        """Удаление воркспейса"""
        try:
            self.workspaces.remove(name)
        except:
            print("Удяляемый воркспейс отсутсвует в базе данных")
        self.save_db()

    def check_workspace(self, name: str) -> bool:
        """Проверка воркспейса на наличие в базе данных"""
        for elem in self.workspaces:
            if name == elem:
                return True
        return False

    def add_course(self, name: str):
        """Добавление курса"""
        if name not in self.courses:
            self.courses.append(name)
        self.save_db()

    def del_course(self, name: str):
        """Удаление курса"""
        try:
            self.courses.remove(name)
        except:
            print("Удяляемый курс отсутсвует в базе данных")
        self.save_db()

    def check_course(self, name: str) -> bool:
        """Проверка курса на наличие в базе данных"""
        for elem in self.courses:
            if name == elem:
                return True
        return False

    def add_admin(self, id: int, name: str):
        """Добавление администратора бота"""
        self.admins[id] = {}
        self.admins[id]["name"] = name
        self.save_db()

    def get_admins_id(self) -> set:
        """Возвращает кортеж из идентификаторов админов"""
        return set(self.admins.keys())

    def get_admins_name(self) -> set:
        """Возвращает кортеж из названий админов"""
        admins_name: set = set()
        for key in self.admins:
            admins_name.add(self.admins[key]["name"])
        return admins_name

    def del_admin(self, name: str):
        """Удаляет администратора по его имени"""
        del_id: int = 0
        for key in self.admins:
            if self.admins[key]["name"] == name:
                del_id = key
        if del_id in self.admins and len(self.admins) > 1:
            del self.admins[del_id]
            self.save_db()

    def get_workspaces(self) -> set:
        """Возвращает кортеж из названий воркспейсов"""
        return set(self.workspaces)

    def save_db(self):
        """Сохранение изменений в базе"""
        # Создаем словарь с данными
        save_dict: dict = {}
        save_dict["chats"] = self.chats
        save_dict["workspaces"] = self.workspaces
        save_dict["courses"] = self.courses
        save_dict["admins"] = self.admins
        # Сохраняем словарь в файл
        with open(self.file_name, "w") as f:
            json.dump(save_dict, f, ensure_ascii=False)

    def load_db(self):
        """Загрузка базы из файла"""
        save_dict: dict = {}
        # Чтение данных из файла
        try:
            with open(self.file_name, "r") as f:
                save_dict = json.load(f)
            # Загрузка данных из словаря
            self.chats = save_dict["chats"]
            self.workspaces = save_dict["workspaces"]
            self.courses = save_dict["courses"]
            # Преобразование идентификаторов администраторов
            for id in save_dict["admins"]:
                new_id = int(id)
                self.admins[new_id] = {"name": save_dict["admins"][id]["name"]}
        except:
            print("Ошибка при загрузке файла с базой данных")




bot_db = Db()