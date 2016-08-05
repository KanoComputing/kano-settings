from pyfakefs.fake_filesystem_unittest import Patcher


def create_fs():
    patcher = Patcher()
    patcher.setUp()

    return patcher


FAKE_FS = create_fs()
