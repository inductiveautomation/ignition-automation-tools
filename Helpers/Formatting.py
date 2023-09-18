import os
from pathlib import Path


class FilePathFormatting:
    """
    The functions contained within this class are intended to operate on string file paths and make them
    platform-agnostic, so that they can be used regardless of Operating System.
    """

    @staticmethod
    def system_safe_file_path(exec_dir: str, file_path: str) -> str:
        """
        Attempts to take a standard string file path and make it work across any operating system.

        :param exec_dir: The execution directory to be used in constructing the file path.
        :param file_path: The path of the file.

        :returns: A platform-agnostic path to a file.
        """
        return str(Path(os.path.join(exec_dir, file_path)).resolve())

    @staticmethod
    def create_incremented_file_path(file_path: str) -> str:
        """
        Given a desired file path, create a unique file name by incrementing on the supplied path.

        Example:
            file_path = "something/myPicture.jpeg"
            If a file with that name already exists on the operating system, you will receive a new file path:
            "something/myPicture_1.jpeg". Had the file not already existed, you would receive the same file path you
            had supplied.

        :param file_path: A File path to look for on the operating system.

        :returns: A unique and unused file path built from the supplied file_path.
        """
        add = 1
        final_file_path = file_path
        while os.path.isfile(final_file_path):
            split = file_path.split('.')
            part_1 = split[0] + "_" + str(add)
            final_file_path = '.'.join([part_1, split[1]])
            add += 1
        return final_file_path
