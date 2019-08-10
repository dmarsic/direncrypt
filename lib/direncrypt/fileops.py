import os

class FileOps(object):

    @staticmethod
    def delete_file(directory, filename):
        """Try to delete file from filesystem."""
        print("Deleting file on filesystem: {}".format(filename))
        try:
            os.unlink(os.path.expanduser(os.path.join(directory, filename)))
        except OSError as e:
            print("Failed to delete {}: {}".format(filename, str(e)))
            return False
        return True
