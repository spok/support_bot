import sqlite3
import re
from copy import deepcopy


class Db:
    def __init__(self):
        self.db_name = 'data.db'
        self.chats: dict = {}
        self.workspaces: list[str] = []
        self.courses: list[str] = []
        self.groups: list[str] = []
        self.admins: dict = {783188960: {"name": "Власов Слава"}}
        self.create_table()
        self.load_db()

    def create_table(self):
        """Создание таблиц в базе данных"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            # создание таблицы с чатами
            create_table_query = """CREATE TABLE IF NOT EXISTS chats
                                  (ID                INTEGER PRIMARY KEY NOT NULL,
                                  name             TEXT    NOT NULL,
                                  workspace               TEXT    NOT NULL,
                                  group               TEXT    NOT NULL,
                                  course        TEXT NOT NULL);"""
            cursor.execute(create_table_query)
            conn.commit()
            # создание таблицы с воркспейсами
            create_table_query = """CREATE TABLE IF NOT EXISTS workspaces
                                  (ID                INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                  name             TEXT    NOT NULL);"""
            cursor.execute(create_table_query)
            conn.commit()
            # создание таблицы с группами
            create_table_query = """CREATE TABLE IF NOT EXISTS groups
                                  (ID                INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                  name             TEXT    NOT NULL);"""
            cursor.execute(create_table_query)
            conn.commit()
            # создание таблицы с курсами
            create_table_query = """CREATE TABLE IF NOT EXISTS courses
                                  (ID                INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                  name             TEXT    NOT NULL);"""
            cursor.execute(create_table_query)
            conn.commit()
            # создание таблицы с администраторами
            create_table_query = """CREATE TABLE IF NOT EXISTS admins
                                  (ID                INTEGER PRIMARY KEY NOT NULL,
                                  name             TEXT    NOT NULL);"""
            cursor.execute(create_table_query)
            conn.commit()
        except Exception as error:
            print("Ошибка при работе с базой данной", error)
        finally:
            conn.close()
            print("Соединение с базой закрыто")
        # Добавление администратора по умолчанию
        conn = None
        for admin in self.admins:
            try:
                conn = sqlite3.connect(self.db_name)
                cursor = conn.cursor()
                insert_query = """INSERT INTO admins (ID, name) VALUES (?, ?)"""
                cursor.execute(insert_query, (admin, self.admins[admin]["name"]))
                conn.commit()
            except Exception as error:
                print("Ошибка при добавлении в таблицу нового администратора", error)
            finally:
                conn.close()

    def load_db(self):
        """Загрузка данных из базы данных"""
        conn = None
        try:
            # Подключение к базе данных
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            # Загрузка чатов
            query_chats = """SELECT * FROM chats;"""
            cursor.execute(query_chats)
            record = cursor.fetchall()
            for elem in record:
                self.chats[elem[0]] = {
                    "name": elem[1],
                    "workspace": elem[2],
                    "group": elem[3],
                    "course": elem[4]
                }

            # Загрузка воркспейсов
            query_chats = """SELECT * FROM workspaces;"""
            cursor.execute(query_chats)
            record = cursor.fetchall()
            for elem in record:
                self.workspaces.append(elem[1])

            # Загрузка групп
            query_chats = """SELECT * FROM groups;"""
            cursor.execute(query_chats)
            record = cursor.fetchall()
            for elem in record:
                self.groups.append(elem[1])

            # Загрузка курсов
            query_chats = """SELECT * FROM courses;"""
            cursor.execute(query_chats)
            record = cursor.fetchall()
            for elem in record:
                self.courses.append(elem[1])

            # Загрузка администраторов
            query_chats = """SELECT * FROM admins;"""
            cursor.execute(query_chats)
            record = cursor.fetchall()
            for elem in record:
                self.admins[elem[0]] = {
                    "name": elem[1]
                }
        except Exception as error:
            print("Ошибка при загрузки из базы данных", error)
        finally:
            conn.close()

    def add_chats(self, id: int, name: str, workspace: str, course: str, group: str):
        """Добавление нового чата"""
        # Добавление в переменную с чатами
        if id not in self.chats:
            self.chats[id] = {
                "name": name,
                "workspace": workspace,
                "course": course,
                "group": group
            }
            # Добавление в базу данных
            conn = None
            try:
                conn = sqlite3.connect(self.db_name)
                cursor = conn.cursor()
                insert_query = """INSERT INTO chats(ID, name, group, workspace, course) VALUES (?, ?, ?, ?, ?)"""
                cursor.execute(insert_query, (id, name, group, workspace, course))
                conn.commit()
            except Exception as error:
                print("Ошибка при добавлении в таблицу нового чата", error)
            finally:
                conn.close()

    def get_chats(self) -> set:
        """Возвращает кортеж из списка названий чатов"""
        all_chats: set = set()
        for key in self.chats:
            all_chats.add(self.chats[key]["name"])
        return all_chats

    def get_filter_chats(self, workspace: str, course: str, group: str) -> dict:
        """Возвращает список чатов отфильтрованных по параметрам"""
        filter_chats = deepcopy(self.chats)
        del_id: set[int] = set()       # Кортеж идентификаторов чатов для удаления
        # Заполняем кортеж с идентификаторов чатов, которые не соответствуют фильтрам
        for chat_id in filter_chats:
            # Проверка на соответсвие чата фильтру вокрспейса, группы и курса
            if workspace not in 'any':
                if filter_chats[chat_id]["workspace"] not in workspace:
                    del_id.add(chat_id)
            if group not in 'any':
                if filter_chats[chat_id]["group"] not in group:
                    del_id.add(chat_id)
            if course not in 'any':
                if filter_chats[chat_id]["course"] not in course:
                    del_id.add(chat_id)
        # Удаляем в копии чаты, которые не соответсвуют фильтрам
        for chat in del_id:
            del filter_chats[chat]
        return filter_chats

    def get_chats_id(self) -> set:
        """Возвращает кортеж из идентификаторов чата"""
        all_chats_id: set = set()
        for key in self.chats:
            all_chats_id.add(key)
        return all_chats_id

    def get_chat_name(self, chat_id: int) -> str:
        """Возвращает название чата по его идентификатору"""
        return self.chats[chat_id]["name"]

    def del_chat(self, chat_id: int):
        """Удаляет чат по имени"""
        # Удаление чата из переменной
        if chat_id in self.chats:
            del self.chats[chat_id]
        # Удаление чата из таблицы БД
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            insert_query = """DELETE FROM chats WHERE ID = ?"""
            cursor.execute(insert_query, (chat_id,))
            conn.commit()
        except Exception as error:
            print("Ошибка при удалении чата", error)
        finally:
            conn.close()

    # ========== Работа с группами ==========
    # =======================================

    def add_group(self, name: str):
        """Добавление новой группы"""
        if name not in self.groups:
            # Добавление в переменную с группами
            self.groups.append(name)
            # Добавление в таблицу БД
            conn = None
            try:
                conn = sqlite3.connect(self.db_name)
                cursor = conn.cursor()
                insert_query = """INSERT INTO groups (name) VALUES (?)"""
                cursor.execute(insert_query, (name, ))
                conn.commit()
            except Exception as error:
                print("Ошибка при добавлении в таблицу новоой группы", error)
            finally:
                conn.close()

    def check_group(self, name: str) -> bool:
        """Проверка группы на наличие в базе данных"""
        return name in self.groups


    def del_group(self, name: str) -> str:
        """Удаление группы"""
        group_index: int = int(name[5:])
        group_name: str = self.groups[group_index]
        try:
            del self.groups[group_index]
        except:
            print("Удяляемая группв отсутсвует в базе данных")
        # Удаление группы из таблицы БД
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            insert_query = """DELETE FROM groups WHERE name = ?"""
            cursor.execute(insert_query, (group_name,))
            conn.commit()
        except Exception as error:
            print("Ошибка при удалении группы", error)
        finally:
            conn.close()
        return group_name


    # ========== Работа с воркспейсами ==========
    # ===========================================

    def add_workspaces(self, name: str):
        """Добавление воркспейса"""
        if name not in self.workspaces:
            # Добавление в переменную воркспейсов
            self.workspaces.append(name)
            # Добавление в таблицу БД
            conn = None
            try:
                conn = sqlite3.connect(self.db_name)
                cursor = conn.cursor()
                insert_query = """INSERT INTO workspaces (name) VALUES (?)"""
                cursor.execute(insert_query, (name, ))
                conn.commit()
            except Exception as error:
                print("Ошибка при добавлении в таблицу нового воркспейса", error)
            finally:
                conn.close()

    def del_workspace(self, name: str):
        """Удаление воркспейса"""
        self.workspaces.remove(name)
        # Удаление воркспейса из таблицы БД
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            insert_query = """DELETE FROM workspaces WHERE name = ?"""
            cursor.execute(insert_query, (name,))
            conn.commit()
        except Exception as error:
            print("Ошибка при удалении воркспейса", error)
        finally:
            conn.close()

    def check_workspace(self, name: str) -> bool:
        """Проверка воркспейса на наличие в базе данных"""
        for elem in self.workspaces:
            if name == elem:
                return True
        return False

    def get_workspaces(self) -> set[str]:
        """Возвращает кортеж из списка названий воркспейсов"""
        print(set(self.workspaces))
        return set(self.workspaces)

    def add_course(self, name: str):
        """Добавление курса"""
        if name not in self.courses:
            self.courses.append(name)
            # Добавление в таблицу БД
            conn = None
            try:
                conn = sqlite3.connect(self.db_name)
                cursor = conn.cursor()
                insert_query = """INSERT INTO courses (name) VALUES (?)"""
                cursor.execute(insert_query, (name, ))
                conn.commit()
            except Exception as error:
                print("Ошибка при добавлении в таблицу нового курса", error)
            finally:
                conn.close()

    def del_course(self, name: str) -> str:
        """Удаление курса"""
        course_index: int = int(name[6:])
        course_name: str = self.courses[course_index]
        try:
            del self.courses[course_index]
        except:
            print("Удяляемый курс отсутсвует в базе данных")
        # Удаление курса из таблицы БД
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            insert_query = """DELETE FROM courses WHERE name = ?"""
            cursor.execute(insert_query, (course_name,))
            conn.commit()
        except Exception as error:
            print("Ошибка при удалении курса", error)
        finally:
            conn.close()
        return course_name

    def check_course(self, name: str) -> bool:
        """Проверка курса на наличие в базе данных"""
        return name in self.courses

    def get_course(self) -> set:
        """Возвращает кортеж из списка курсов"""
        return set(self.courses)

    def get_course_name(self, course_index: str) -> str:
        """Возвращает название курса по его calback_data"""
        return self.courses[int(course_index[6:])]

    def add_admin(self, id: int, name: str):
        """Добавление администратора бота"""
        if id not in self.admins:
            self.admins[id] = {}
            self.admins[id]["name"] = name
            # Добавление в таблицу БД
            conn = None
            try:
                conn = sqlite3.connect(self.db_name)
                cursor = conn.cursor()
                insert_query = """INSERT INTO admins (ID, name) VALUES (?, ?)"""
                cursor.execute(insert_query, (id, name))
                conn.commit()
            except Exception as error:
                print("Ошибка при добавлении в таблицу нового администратора", error)
            finally:
                conn.close()

    def get_admins_id(self) -> set:
        """Возвращает кортеж из идентификаторов админов"""
        return set(self.admins.keys())

    def get_admins_name(self) -> set:
        """Возвращает кортеж из названий админов"""
        admins_name: set = set()
        for key in self.admins:
            admins_name.add(self.admins[key]["name"])
        return admins_name

    def del_admin(self, name: str) -> str:
        """Удаляет администратора по его имени"""
        del_id: int = int(name)
        del_name = self.admins[del_id]["name"]
        if del_id in self.admins and len(self.admins) > 1:
            del self.admins[del_id]
            # Удаление курса из таблицы БД
            conn = None
            try:
                conn = sqlite3.connect(self.db_name)
                cursor = conn.cursor()
                insert_query = """DELETE FROM admins WHERE ID = ?"""
                cursor.execute(insert_query, (del_id,))
                conn.commit()
            except Exception as error:
                print("Ошибка при удалении администратора чата", error)
            finally:
                conn.close()
        return del_name

def escape_markdown(text: str) -> str:
  escape_chars = r"\_*[]()~`>#+-=|{}.!"
  return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)

bot_db = Db()
