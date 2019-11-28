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
            self.db.ladd(self.db_name, {'name':name, 'size':-1, 'cr_date':-1})
        else:
            self.db.ladd(self.db_name, name)
        self.db.dump()
    
    def add_info(self, name, dct):
        files = self.db.lgetall(self.db_name)
        for i in range(len(files)):
            if files[i]['name'] == name:
                for key in list(dct.keys()):
                    files[i][key] = dct[key]
    
    def get_info(self, name):
        files = self.db.lgetall(self.db_name)
        for i in range(len(files)):
            if files[i]['name'] == name:
                return files[i]
        return {}

    def del_file(self, name):
        '''
        Delete file from db
        Name - full path
        '''
        files = self.db.lgetall(self.db_name)
        files = [item['name'] for item in files]
        self.db.lpop(self.db_name, files.index(name))
        self.db.dump()

    def items_in_folder(self, name):
        '''
        Get all items in folder
        Name - full path to folder (means ends with '/')
        '''
        paths = self.db.lgetall(self.db_name)
        files = []
        folders = []
        files_set, folders_set = set(), set() 
        for path in paths:
            if not path['name'].startswith(name):
                continue

            # Get filename in folder
            tmp = path['name'][len(name):].split('/')[0]
            if len(tmp) != 1 and path['name'] != name:
                if not tmp in folders_set:
                    folders_set.add(tmp)
                    folders.append({'name':tmp, 'size':path['size'],'cr_date':path['cr_date']})
            else:
                if not tmp in files_set:
                    files_set.add(tmp)
                    files.append({'name':tmp, 'size':path['size'],'cr_date':path['cr_date']})

        return (folders, files)

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


if __name__ == '__main__':
    f = Files('f')
    f.add({'name':'/home/', 'size':1, 'cr_date':1})
    f.add({'name':'/home/file1.txt', 'size':1, 'cr_date':1})
    
