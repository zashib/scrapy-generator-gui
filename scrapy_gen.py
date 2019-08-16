# -*- coding: utf-8 -*-
import os
import shutil
from assist import Text
from assist import Dir
from assist import File
import filecmp

class ScrapyGen:
    def __init__(self, src_dir='scrapy_generator', dest_dir='test', items=['1','2'], items_path=['path 1','path 2'], default_src='default settings', settings_list=[], start_url='https://scrapy.generator'):
        self.src_dir = src_dir
        self.dest_dir = dest_dir
        self.default_src = default_src
        self.items = items
        self.options = {'images(default)': ['images', 'image_urls'],
                        'images(named)': ['images', 'image_urls']}
        self.items_path = items_path
        self.start_url = start_url
        settings_list.insert(0, self.default_src)
        self.settings_list = settings_list
        self.domain = self.domain_name()
        self.gen()

    def gen(self):
        '''Generate project'''
        for src in self.settings_list:
            if src in self.options:
                self.items += self.options[src]
            self.source_path = os.path.join(self.src_dir, src)
            settings_path = os.path.join(self.src_dir, 'settings', '%s.py'%src)
            settin = os.path.join(self.dest_dir, self.src_dir, 'settings.py')
            if os.path.exists(self.source_path):
                self.copy_dir(src)
            if os.path.exists(settings_path):
                dst = Text.read(settin)
                src = Text.read(settings_path)
                Text.write(settin, '\n'.join([dst, src]))

        self.rename_dirs()
        self.change_content()
        self.edit_spider()
        #Edit items.py
        self.items_add()
        #Edit <spider_name>.py file
        self.items_add(indent=8, filename='%s.py'%self.dest_dir)

        filename = 'settings.py'
        filepath = Text.get_file(self.dest_dir, filename)
        text = Text.read(filepath)
        pattern = 'items_generator'
        repl = str(self.items)
        text = Text.replace(pattern, repl, text)
        Text.write(filepath, text)

    def copy_dir(self, src):
        '''Copying project'''
        if src == 'default settings':
            Dir.copy(self.source_path, self.dest_dir)
        else:
            settings = os.path.join(self.src_dir, src)
            list_ignore = []
            common_files = filecmp.dircmp(settings, self.dest_dir).common_files
            common_files = set(File.get_files(self.dest_dir, path=False)).intersection(set(File.get_files(settings, path=False)))

            for com_file in common_files:
                if File.compare(File.get_file(self.dest_dir, com_file), File.get_file(os.path.join(self.src_dir, self.default_src), com_file)) == False:
                    list_ignore.append(com_file)
                    dst = Text.read(File.get_file(self.dest_dir, com_file))
                    src = Text.read(File.get_file(self.source_path, com_file))
                    Text.write(File.get_file(self.dest_dir, com_file), '\n'.join([dst, src]))

            Dir.copy(self.source_path, self.dest_dir, ignore=shutil.ignore_patterns(*list_ignore), dirs_exist_ok=True)


    def domain_name(self):
        '''Return domain name based on start_url'''
        if '/' in self.start_url:
            if '://' in self.start_url:
                domain = self.start_url.split('://')[1]
                if '/' in domain:
                    return domain.split('/')[0]
        else: return self.start_url

    def edit_spider(self):
        '''Edit spider'''
        args = [['https://scrapy-generator', '%s'%self.start_url],
                ["scrapy.generator", '%s'%self.domain]]
        self.mass_replace(args, filename='%s.py'%self.dest_dir)

    def rename_dirs(self):
        '''Rename directoties'''
        for dir in Dir.get_dirs(self.dest_dir, topdown=False):
            if os.path.split(dir)[1] == self.src_dir:
                Dir.rename(dir, os.path.join(os.path.split(dir)[0], self.dest_dir))

    def get_classname(self):
        '''Get class name from project name'''
        if '_' in self.dest_dir:
            names = self.dest_dir.split('_')
            classname = ''
            for name in names:
                classname += name.capitalize()
            return classname
        return self.dest_dir.capitalize()

    def change_content(self):
        '''Rename files and replace content'''
        for file in Dir.get_files(self.dest_dir):
            data = Text.read(file)
            data = Text.replace(self.src_dir, self.dest_dir, data)
            class_name = self.get_classname()
            data = Text.replace(self.src_dir[0].upper() + self.src_dir[1:], class_name, data)
            # Rename spider
            if os.path.split(file)[1] == self.src_dir + '.py':
                new_dst = os.path.dirname(file) + '/' + self.dest_dir + '.py'
                File.rename(file, new_dst)
                Text.write(new_dst, data)
            else:
                Text.write(file, data)

    def items_add(self, indent=4, filename='items.py'):
        '''Add items to file'''
        indent = ' ' * indent
        pattern = indent + 'pass'
        repl = ''
        if filename == 'items.py':
            for item in self.items:
                repl += '%s%s = scrapy.Field()\n'%(indent, item)
        elif filename == '%s.py'%self.dest_dir:
            items = list(zip(self.items, self.items_path))
            for item, path in items:
                repl += "%sitem['%s'] = %s\n"%(indent, item, path)

        filepath = Text.get_file(self.dest_dir, filename)
        text = Text.read(filepath)
        text = Text.replace(pattern, repl, text)
        Text.write(filepath, text)

    def mass_replace(self, args, filename='settings.py'):
        '''Mass text replace (get file path and list of [pattern, repl])'''
        filepath = Text.get_file(self.dest_dir, filename)
        text = Text.read(filepath)
        for pattern, repl in args:
            text = Text.replace(pattern, repl, text)
        Text.write(filepath, text)

if __name__ == '__main__':
    ScrapyGen()
