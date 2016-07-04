
from moviemanager.objects import get_data_from_files, Fileobj
from moviemanager.settings import VIDEO_DIR, FILE_SIZE_LIMIT
from moviemanager.test import Test


def main():
    # Test().test()
    import os
    for root, dirs, files in os.walk(VIDEO_DIR, topdown=True):
        allfiles = []
        for name in files:
            filepath = os.path.join(root, name)
            if not Fileobj.is_hidden(filepath) and Fileobj.is_video(filepath) and Fileobj.has_size(filepath,FILE_SIZE_LIMIT):
                allfiles.append(filepath)
        get_data_from_files(allfiles)




if __name__ == '__main__':
    main()