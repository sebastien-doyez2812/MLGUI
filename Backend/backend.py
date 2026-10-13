import os

class Backend:
    def __init__(self):
        self.dataset_path = None
        self.idx_img = 0

    def setDatasetPath(self, path: str):
        print("set")
        self.dataset_path = path
        self.idx_img = 0
        self.img_list = []
        for root, dirs, files in os.walk(self.dataset_path):
            if root.endswith("imgs"):
                for file in files:
                    self.img_list.append(os.path.join(root, file))

    def getDatasetPath(self):
        print("get")
        return self.dataset_path

    def get_current_img_path(self):
        return self.img_list[self.idx_img]

    def next_image(self):
        self.idx_img += 1

    def previous_image(self):
        self.idx_img -= 1

    def enter_index_image(self, index):
        self.idx_img = index