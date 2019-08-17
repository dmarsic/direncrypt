import os
from direncrypt.util import printit

class FileOps(object):

    @staticmethod
    def delete_file(root_dir, file_name):
        """Try to delete file from filesystem.
        
        returns true if successful, false otherwise
        """
        try:
            os.unlink(os.path.expanduser(os.path.join(root_dir, file_name)))
        except OSError as ose:
            printit("Failed to delete file {} : {}",file_name, str(ose))
            return False
        return True
    
    @staticmethod
    def create_symlink(root_dir, link_name, target):
        """Try to create a symlink pointing to target
                
        returns true if successful, false otherwise
        """
        try:
            os.symlink(target, os.path.expanduser(os.path.join(root_dir, link_name)))
        except Exception as e:
            printit('Failed to create symlink {} : {}', link_name, str(e))
            return False
        return True
    
    @staticmethod
    def create_directory(root_dir, dir_name):
        """Try to create a directory
                
        returns true if successful, false otherwise
        """
        try:
            os.mkdir(os.path.expanduser(os.path.join(root_dir, dir_name)))
        except OSError as ose:
            printit('Failed to create directory {} : {}', dir_name, str(ose))
            return False
        return True