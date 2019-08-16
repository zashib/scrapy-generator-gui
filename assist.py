import re
import os
import glob
import shutil
import distutils.dir_util
import filecmp

class Error(OSError):
    pass

class Action():
    @classmethod
    def read(cls, file_name, mode='r', buffering=-1, encoding='utf-8', errors=None, newline=None, closefd=True, opener=None):
        '''File read'''
        with open(file_name, mode, encoding=encoding) as f:
            return f.read()

    @classmethod
    def write(cls, file_name, data, mode='w', buffering=-1, encoding='utf-8', errors=None, newline=None, closefd=True, opener=None):
        '''File write'''
        with open(file_name, mode, encoding=encoding) as f:
            f.write(data)

    @classmethod
    def replace(cls, pattern, repl, string, count=0, flags=0):
        '''Text replacement(for Text only)'''
        pattern = r'%s'%pattern
        return re.sub(pattern, repl, string, count=count, flags=flags)

    @classmethod
    def get_files(cls, top, path=True, topdown=True, onerror=None, followlinks=False):
        '''Get list of all files in directory(with path or without)'''
        files_list = []
        for root, dirs, files in os.walk(top, topdown=topdown, onerror=onerror, followlinks=followlinks):
            for file in files:
                if path == True:
                    files_list.append(os.path.join(root, file))
                else:
                    files_list.append(file)
        return files_list

    @classmethod
    def get_file(cls, pathname, filename,  recursive=True):
        '''Get first file path from directory (using glob library)'''
        for file in glob.glob(os.path.join(pathname, '**'), recursive=recursive):
            if os.path.split(file)[1] == filename and os.path.isfile(file):
                return file
    @classmethod
    def get_dir(cls, pathname, dirname,  recursive=True):
        '''Get first directory path from directory (using glob library)'''
        for path in glob.glob(os.path.join(pathname, '**'), recursive=recursive):
            if os.path.split(path)[1] == dirname and os.path.isdir(path):
                return path
    @classmethod
    def get_dirs(cls, top, topdown=True, onerror=None, followlinks=False):
        '''Get list of all directories in directory(with path)'''
        dirs_list = []
        for root, dirs, files in os.walk(top, topdown=topdown, onerror=onerror, followlinks=followlinks):
            for dir in dirs:
                dirs_list.append(os.path.join(root, dir))
        return dirs_list

    @classmethod
    def copy(cls, src, dst, follow_symlinks=True):
        '''Copying file.
        If the dst directory doesn't exist, we will attempt to create it using makedirs.'''
        if not os.path.isdir(os.path.dirname(dst)):
            os.makedirs(os.path.dirname(dst))
        shutil.copy(src, dst, follow_symlinks=follow_symlinks)

    @classmethod
    def remove(cls, path):
        '''Remove file'''
        import stat
        if not os.access(path, os.W_OK):
            # Is the error an access error ? Change the mode of path.
            os.chmod(path, stat.S_IWUSR)
        else:
            raise
        os.remove(path)

    @classmethod
    def rename(cls, src, dst):
        """ Rename file"""
        os.rename(src, dst)

    @classmethod
    def compare(cls, f1, f2, shallow=True):
        """ File comparison"""
        return filecmp.cmp(f1, f2, shallow=shallow)

class Text(Action):
    pass

class Directoty(Action):
    @classmethod
    def copy(cls, src, dst, symlinks=False, ignore=None, copy_function=shutil.copy2, ignore_dangling_symlinks=False, dirs_exist_ok=True):
        '''Copying directory with all files(creates new directoty)
        Can overwrite directory'''
        names = os.listdir(src)
        if ignore is not None:
            ignored_names = ignore(src, names)
        else:
            ignored_names = set()

        os.makedirs(dst, exist_ok=dirs_exist_ok)
        errors = []
        for name in names:
            if name in ignored_names:
                continue
            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)
            try:
                if os.path.islink(srcname):
                    linkto = os.readlink(srcname)
                    if symlinks:
                        # We can't just leave it to `copy_function` because legacy
                        # code with a custom `copy_function` may rely on copytree
                        # doing the right thing.
                        os.symlink(linkto, dstname)
                        shutil.copystat(srcname, dstname, follow_symlinks=not symlinks)
                    else:
                        # ignore dangling symlink if the flag is on
                        if not os.path.exists(linkto) and ignore_dangling_symlinks:
                            continue
                        # otherwise let the copy occurs. copy2 will raise an error
                        if os.path.isdir(srcname):
                            cls.copy(srcname, dstname, symlinks, ignore,
                                     copy_function)
                        else:
                            copy_function(srcname, dstname)
                elif os.path.isdir(srcname):
                    cls.copy(srcname, dstname, symlinks, ignore, copy_function)
                else:
                    # Will raise a SpecialFileError for unsupported file types
                    copy_function(srcname, dstname)
            # catch the Error from the recursive copytree so that we can
            # continue with other files
            except Error as err:
                errors.extend(err.args[0])
            except OSError as why:
                errors.append((srcname, dstname, str(why)))
        try:
            shutil.copystat(src, dst)
        except OSError as why:
            # Copying file access times may fail on Windows
            if getattr(why, 'winerror', None) is None:
                errors.append((src, dst, str(why)))
        if errors:
            raise Error(errors)
        return dst

    @classmethod
    def remove(cls, path, ignore_errors=False, onerror=None):
        '''Remove directory'''
        def onerror(func, path, exc_info):
            """
            Error handler for ``shutil.rmtree``.

            If the error is due to an access error (read only file)
            it attempts to add write permission and then retries.

            If the error is for another reason it re-raises the error.

            Usage : ``shutil.rmtree(path, onerror=onerror)``
            """
            import stat
            if not os.access(path, os.W_OK):
                # Is the error an access error ?
                os.chmod(path, stat.S_IWUSR)
                func(path)
            else:
                raise
        shutil.rmtree(path, ignore_errors=ignore_errors, onerror=onerror)

    @classmethod
    def compare(cls, dir1, dir2):
        """ Directories comparison"""
        """
        Compare two directories recursively. Files in each directory are
        assumed to be equal if their names and contents are equal.
        @return: True if the directory trees are the same and
            there were no errors while accessing the directories or files,
            False otherwise.
        """
        dirs_cmp = filecmp.dircmp(dir1, dir2)
        if len(dirs_cmp.left_only)>0 or len(dirs_cmp.right_only)>0 or \
            len(dirs_cmp.funny_files)>0:
            return False
        (_, mismatch, errors) =  filecmp.cmpfiles(
            dir1, dir2, dirs_cmp.common_files, shallow=False)
        if len(mismatch)>0 or len(errors)>0:
            return False
        for common_dir in dirs_cmp.common_dirs:
            new_dir1 = os.path.join(dir1, common_dir)
            new_dir2 = os.path.join(dir2, common_dir)
            if not cls.compare(new_dir1, new_dir2):
                return False
        return True

    @classmethod
    def rename(cls, src, dest):
        """ Rename directory"""
        os.rename(src, dest)

class File(Action):
    pass

Txt = Text
Dir = Directoty
