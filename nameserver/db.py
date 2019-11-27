import pickledb
import os

class Files():
    def __init__(self, name):
        '''
        name - filename of db
        db_name - name of subdb
        '''

        self.db_name = 'f'
        self.name = name
        self.is_exist = os.path.isfile("./"+name)
        self.db = pickledb.load(name, self.is_exist)
        if not self.is_exist:
            self.db.lcreate(self.db_name)
        self.db.dump()

    def is_file_exist(self, name):
        '''
        Check presents of a file in db
        Name - full path (e.g. /home/dir/file.txt or /home/dir/)
        '''
        res = self.db.lgetall(self.db_name)
        return name in res

    def add(self, name):
        '''
        Add file to the db.
        Name - full path
        '''
        self.db.ladd(self.db_name, name)
        self.db.dump()

    def del_file(self, name):
        '''
        Delete file from db
        Name - full path
        '''
        files = self.db.lgetall(self.db_name)
        self.db.lpop(self.db_name, files.index(name))
        self.db.dump()

    def items_in_folder(self, name):
        '''
        Get all items in folder
        Name - full path
        '''
        files = self.db.lgetall(self.db_name)
        items = []
        folders = []
        for i in range(len(files)):
            f = files[i][len(name):].split('/')
            if files[i].startswith(name):
                if files[i][-1] == '/':
                    if files[i] != name:
                        folders.append(f[0])
                else:
                    items.append(f[0])
        return (folders, items) 

    def get_all(self):
        '''
        Return all files
        '''
        return self.db.lgetall(self.db_name)
