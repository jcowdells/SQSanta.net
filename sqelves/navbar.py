class Navbar:
    def __init__(self, **links):
        self.__links = links

    def get_title(self, index):
        return list(self.__links.keys())[index].replace("_", " ")

    def get_link(self, index):
        return list(self.__links.values())[index]

    def get_num_links(self):
        return len(self.__links)
