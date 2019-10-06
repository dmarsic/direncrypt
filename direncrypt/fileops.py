import os


class FileOps(object):

    @staticmethod
    def delete_file(root_dir, file_name):
        """Try to delete file from filesystem.

        Returns true if successful, false otherwise.
        """
        try:
            os.unlink(os.path.expanduser(os.path.join(root_dir, file_name)))
        except OSError as ose:
            print("Failed to delete file {} : {}".format(file_name, str(ose)))
            return False
        return True

    @staticmethod
    def create_symlink(root_dir, link_name, target):
        """Try to create a symlink pointing to target.

        Returns true if successful, false otherwise.
        """
        try:
            os.symlink(target, os.path.expanduser(os.path.join(root_dir, link_name)))
        except OSError as ose:
            print('Failed to create symlink {} : {}'.format(link_name, str(ose)))
            return False
        return True

    @staticmethod
    def create_directory(root_dir, dir_name):
        """Try to create a directory.

        Returns true if successful, false otherwise.
        """
        try:
            os.mkdir(os.path.expanduser(os.path.join(root_dir, dir_name)))
        except OSError as ose:
            print('Failed to create directory {} : {}'.format(dir_name, str(ose)))
            return False
        return True
