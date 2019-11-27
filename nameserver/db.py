import pickledb
import os

class Files():
    def __init__(self, name):
        self.db_name = 'f'
        self.name = name
        self.db = pickledb.load(name, os.path.isfile("./"+name))
        self.db.lcreate(self.db_name)
        self.db.dump()

    def is_file_exist(self, name):
        res = self.db.lgetall(self.db_name)
        return name in res

    def add(self, name):
        self.db.ladd(self.db_name, name)
        self.db.dump()

    def del_file(self, name):
        files = self.db.lgetall(self.db_name)
        self.db.lpop(self.db_name, files.index(name))
        self.db.dump()

    def items_in_folder(self, name):
        files = self.db.lgetall(self.db_name)
        items = []
        for i in range(len(files)):
            if files[i].startswith(name):
                items.append(files[i])
        return items

    def get_all_files(self):
        return self.db.lgetall(self.db_name)

