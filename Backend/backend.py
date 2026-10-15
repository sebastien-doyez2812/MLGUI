import os, cv2
from pathlib import Path
import numpy as np

class Backend:
    def __init__(self):
        self.dataset_path = None
        self.idx_img = 0
        self.img_list = []


    def setDatasetPath(self, path: str):
        self.dataset_path = path
        self.idx_img = 0
        self.img_list = []
        for root, dirs, files in os.walk(self.dataset_path):
            if root.endswith("imgs"):
                for file in files:
                    self.img_list.append(os.path.join(root, file))

    def getDatasetPath(self):
        return self.dataset_path

    def load_mask(self, num_bits=8):
        try:
            if len(self.img_list) == 0:
                print("[-] error backend.load_mask: no dataset")

            img_path = Path(str(self.img_list[self.idx_img]))
            dataset_root = img_path.parent.parent
            label_root = os.path.join(dataset_root, "labels")

            label_path = os.path.join(label_root, img_path.stem + ".png")
            orig_img = cv2.imread(str(img_path))
            if orig_img is None:
                return {}

            height, width, _ = orig_img.shape
            if not os.path.exists(label_path):
                return {i: np.zeros((height, width), dtype=np.uint8) for i in range(num_bits)}
            
            encoded_mask = cv2.imread(str(label_path), cv2.IMREAD_GRAYSCALE)
            if encoded_mask is None:
                return {i: np.zeros((height, width), dtype=np.uint8) for i in range(num_bits)}

            masks_dict = {}
            for i in range(num_bits):
                bit_mask = ((encoded_mask & (2 ** i)) > 0).astype(np.uint8) * 255
                masks_dict[i] = bit_mask

            print("[+] load_mask loaded in backend")
            return masks_dict
        except Exception as e:
            print(f"[-] error in Backend: {e}")
    
    def save_mask(self, mask):
        if mask is None or len(self.img_list) == 0:
            print(f"[-] save_mask Error: no mask or path of img given.")
            return False

        img_path = Path(str(self.img_list[self.idx_img]))
        dataset_root = img_path.parent.parent
        labels_dir = dataset_root / "labels"
        labels_dir.mkdir(parents=True, exist_ok=True)
        label_filename = img_path.stem + ".png"
        label_path = labels_dir / label_filename


        items = mask.items()

        first_img = None
        for _, img in items:
            first_img = img
            break
        if first_img is None:
            print("[-] save_mask error: empty mask")
            return False
        
        width, height = first_img.size
        mask_numpy = np.zeros((height, width), dtype=np.uint8)

        for idx, curr_mask in items:
            curr_np = np.array(curr_mask.convert("L")) > 0
            mask_numpy |= curr_np.astype(np.uint8) * (2 ** idx)

        cv2.imwrite(str(label_path), mask_numpy)
        print(f"[+] Mask saved successfully at: {label_path}")
        return True

    def get_current_index(self):
        return self.idx_img

    def get_current_img_path(self):
        if len(self.img_list) == 0:
            return None
        else:
            return self.img_list[self.idx_img]

    def next_image(self):
        self.idx_img += 1

    def previous_image(self):
        self.idx_img -= 1

    def enter_index_image(self, index):
        self.idx_img = index

    def get_len_dataset(self):
        return len(self.img_list)