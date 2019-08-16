import os
from direncrypt.util import printit

class FileOps(object):

    @staticmethod
    def delete_file(directory, filename):
        """Try to delete file from filesystem."""
        printit("Deleting file on filesystem: {}", filename)
        try:
            os.unlink(os.path.expanduser(os.path.join(directory, filename)))
        except OSError as e:
            printit("Failed to delete {}: {}",filename, str(e))
            return False
        return True
    
    @staticmethod
    def create_symlink(target, linkpath):
        """Try to create a symlink pointing to target"""
        try:
            os.symlink(target, linkpath)
        except Exception as e:
            printit('Failed to create symlink : {} ---> {}', linkpath, target)
            return False
        return True