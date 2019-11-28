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
        res = [item['name'] for item in res]
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
        os.remove(self.name)

    def get_all(self):
        '''
        Return all files
        '''
        return self.db.lgetall(self.db_name)


if __name__ == '__main__':
    f = Files('f')
    f.add({'name':'/home/', 'size':1, 'cr_date':1})
    f.add({'name':'/home/file1.txt', 'size':1, 'cr_date':1})
    
