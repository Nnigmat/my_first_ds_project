import pickledb
import os
from datetime import datetime

class Files():
    def __init__(self, name):
        '''
        name - filename of db
        db_name - name of subdb
        '''
        self.db_name = 'db'
        self.name = name
        self.is_exist = os.path.isfile("./"+name)
        self._init_db(self.name)
        
    def _init_db(self, name):
        self.db = pickledb.load(name, self.is_exist, False)
        if not self.is_exist:
            self.db.lcreate(self.db_name)
        self.db.dump()


    def exists(self, name):
        '''
        Check presents of a file in db
        Name - full path (e.g. /home/dir/file.txt or /home/dir/)
        ''' 
        res = self.db.lgetall(self.db_name)
        res = [item['name'] for item in res]
        return name in res

    def add(self, name):
        '''
        Add file to the db.
        Name - full path
        '''
        if type(name) == str:
            self.db.ladd(self.db_name, {'name': name, 'size': -1, 'cr_date': datetime.now().strftime('%d/%m/%Y, %H:%M')})
        else:
            self.db.ladd(self.db_name, name)
        self.db.dump()


    def add_info(self, name, dct):
        files = self.db.lgetall(self.db_name)
        for f in files:
            if f['name'] == name:
                f.update(dct)
        self.db.dump()


    def get_info(self, name):
        '''
        Return info about one file
        Name - path
        '''
        files = self.db.lgetall(self.db_name)
        for f in files:
            if f['name'] == name:
                return f
        return {}


    def get_infos(self, fnames):
        '''
        Return info about multiple files
        Fnames - array of names, paths
        '''
        res = []
        for f in fnames:
            res.append(self.get_info(f))
        return res

    def del_file(self, name):
        '''
        Delete file from db
        Name - full path
        '''
        files = self.db.lgetall(self.db_name)
        files = [item['name'] for item in files]
        to_delete = []
        if name.endswith('/'):
            for item in files:
                if item.startswith(name):
                    to_delete.append(item)
            for del_it in to_delete:
                self.db.lpop(self.db_name, files.index(del_it))
                files.pop(files.index(del_it))
        else:
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
            if not path['name'].startswith(name):
                continue

            # Get filename in folder
            tmp = path['name'][len(name):].split('/')[0]
            if path['name'] != name and path['name'].endswith('/'):
                if not tmp in folders:
                    folders.add(tmp)
            else:
                if not tmp in files and len(path['name'][len(name):].split('/'))==1:
                    files.add(tmp)

        return (sorted(folders), sorted(files))

    def drop_table(self):
        '''
        Drop table
        '''
        self.db.deldb()
        os.remove(self.name)
        self.is_exist = False
        self._init_db(self.name)

    def get_all(self):
        '''
        Return all files
        '''
        return self.db.lgetall(self.db_name)

    
    def move_file(self, source, target):
        if not (self.exists(target) and self.exists(source)):
            pass



    def copy_file(self, source, target):
        if not (self.exists(target) and self.exists(source)):
            pass


if __name__ == '__main__':
    f = Files('f')
    f.add({'name':'/home/', 'size':1, 'cr_date':1})
    f.add({'name':'/home/file1.txt', 'size':1, 'cr_date':1})
    
