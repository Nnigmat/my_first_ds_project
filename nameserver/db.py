import pickledb
import os

class Files():
    def __init__(self, name):
        '''
        name - filename of db
        db_name - name of subdb
        '''
        self.db_name = 'db'
        self.name = name
        self.is_exist = os.path.isfile("./"+name)
        self.db = pickledb.load(name, self.is_exist, False)
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
        Name - full path to folder (means ends with '/')
        '''
        paths = self.db.lgetall(self.db_name)
        files = set()
        folders = set() 
        for path in paths:
            if not path.startswith(name):
                continue

            # Get filename in folder
            tmp = path[len(name):].split('/')[0]
            if path.endswith('/') and path != name:
                folders.add(tmp)
            else:
                files.add(tmp)

        return (folders, files) 

    def get_all(self):
        '''
        Return all files
        '''
        return self.db.lgetall(self.db_name)


if __name__ == '__main__':
    f = Files('db')
    f.add('/home/')
    f.add('/home/file1.txt')
    f.add('/a.txt')
