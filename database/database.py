import sqlite3


class Db:
    def __init__(self):
        self.db_name = 'data.db'
        self.chats: dict = {}
        self.workspaces: list = []
        self.courses: list = []
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
                                  course        TEXT NOT NULL);"""
            cursor.execute(create_table_query)
            conn.commit()
            # создание таблицы с воркспейсами
            create_table_query = """CREATE TABLE IF NOT EXISTS workspaces
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
                    "course": elem[3]
                }

            # Загрузка воркспейсов
            query_chats = """SELECT * FROM workspaces;"""
            cursor.execute(query_chats)
            record = cursor.fetchall()
            for elem in record:
                self.workspaces.append(elem[1])

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

    def add_chats(self, id: int, name: str, workspace: str, course: str):
        """Добавление нового чата"""
        # Добавление в переменную с чатами
        if id not in self.chats:
            self.chats[id] = {
                "name": name,
                "workspace": workspace,
                "course": course
            }
            # Добавление в базу данных
            conn = None
            try:
                conn = sqlite3.connect(self.db_name)
                cursor = conn.cursor()
                insert_query = """INSERT INTO chats(ID, name, workspace, course) VALUES (?, ?, ?, ?)"""
                cursor.execute(insert_query, (id, name, workspace, course))
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

    def del_chat(self, name: str):
        """Удаляет чат по имени"""
        # Удаление чата из переменной
        del_key: int = 0
        for key in self.chats:
            if self.chats[key]["name"] == name:
                del_key = key
        del self.chats[del_key]
        # Удаление чата из таблицы БД
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            insert_query = """DELETE FROM chats WHERE name = ?"""
            cursor.execute(insert_query, (name,))
            conn.commit()
        except Exception as error:
            print("Ошибка при удалении чата", error)
        finally:
            conn.close()

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

    def del_course(self, name: str):
        """Удаление курса"""
        try:
            self.courses.remove(name)
        except:
            print("Удяляемый курс отсутсвует в базе данных")
        # Удаление курса из таблицы БД
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            insert_query = """DELETE FROM courses WHERE name = ?"""
            cursor.execute(insert_query, (name,))
            conn.commit()
        except Exception as error:
            print("Ошибка при удалении курса", error)
        finally:
            conn.close()

    def check_course(self, name: str) -> bool:
        """Проверка курса на наличие в базе данных"""
        for elem in self.courses:
            if name == elem:
                return True
        return False

    def get_course(self) -> set:
        """Возвращает кортеж из списка курсов"""
        return set(self.courses)

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

    def del_admin(self, name: str):
        """Удаляет администратора по его имени"""
        del_id: int = 0
        for key in self.admins:
            if self.admins[key]["name"] == name:
                del_id = key
        if del_id in self.admins and len(self.admins) > 1:
            del self.admins[del_id]
            # Удаление курса из таблицы БД
            conn = None
            try:
                conn = sqlite3.connect(self.db_name)
                cursor = conn.cursor()
                insert_query = """DELETE FROM admins WHERE ID = ?"""
                cursor.execute(insert_query, (id,))
                conn.commit()
            except Exception as error:
                print("Ошибка при удалении администратора чата", error)
            finally:
                conn.close()


bot_db = Db()
