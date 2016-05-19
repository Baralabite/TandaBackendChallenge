
class FileHandler(dict):
    """
    Function to aid in the storing of data.
    Would normally use SQL, but was in a hurry.

    Class essentially extends dict, and adds loading/saving functions
    """
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.load()

    def load(self, filename="tanda.dic"):
        """
        Loads
        :param filename:
        :return:
        """
        file_ = open(filename, "r")
        data = file_.read()
        if data == "":
            data = "{}"
        loadedDict = eval(data)
        self.clear()
        for key in loadedDict:
            self[key] = loadedDict[key]

    def save(self, filename="tanda.dic"):
        """
        Saves itself to a file
        :param filename: Name of file to save to
        :return:
        """
        file_ = open(filename, "w")
        file_.write(str(self))
        file_.close()
