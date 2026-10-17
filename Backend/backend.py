import os, cv2
from pathlib import Path
import numpy as np
import albumentations as A
from PIL import Image
import shutil

class Backend:
    def __init__(self):
        self.dataset_path = None
        self.idx_img = 0
        self.img_list = []
        self.output_augmentation_folder = None
        
        self.nb_classes = 8 # TODO

        self.augmented_dataset_path = None
        self.img_dataset_viewer = []
        self.idx_img_dataset_viewer = 0

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

    def get_aug_folder_path(self):
        return self.augmented_dataset_path
    
    def setAugmentedDataset(self, augDatasetpath):
        self.idx_img_dataset_viewer = 0
        self.augmented_dataset_path = augDatasetpath
        
        valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')
        
        for root, dirs, files in os.walk(self.augmented_dataset_path):
            for file in files:
                if file.lower().endswith(valid_extensions):
                    self.img_dataset_viewer.append(os.path.join(root, file))

    def get_current_aug_img(self):
        print(self.idx_img_dataset_viewer)
        img_path = self.img_dataset_viewer[self.idx_img_dataset_viewer]
        if os.path.exists(img_path):
            return img_path
        else:
            print(f"[-] Error in backend.get_current_aug_img: {img_path} does not exist")
            return None
    
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
            if self.idx_img >= len(self.img_list) or self.idx_img < 0:
                self.idx_img = 0
            return self.img_list[self.idx_img]

    def next_image(self):
        self.idx_img += 1

    def previous_image(self):
        self.idx_img -= 1

    def enter_index_image(self, index):
        self.idx_img = index

    def get_len_dataset(self):
        return len(self.img_list)

    def exportDataset(self, settings, output_folder, progress = None):
        print(settings)
        self.output_augmentation_folder = output_folder

        nb_copy = settings["copies"]
        transform = []

        for key, value in settings.items():
            if value == False:
                continue
            print(key)
            if key == "hflip":
                transform.append(A.HorizontalFlip(p=0.5))
            elif key == "vflip":
                transform.append(A.VerticalFlip(p=0.5))
            elif key == "rotation":
                transform.append(
                                A.ShiftScaleRotate(
                                    shift_limit=0.05, 
                                    scale_limit=(0.1, 0.3),  
                                    rotate_limit=90,          
                                    border_mode=cv2.BORDER_REFLECT_101, 
                                    mask_value=0,            
                                    p=0.8
                                )
                            )
            elif key == "elastic":
                transform.append(A.ElasticTransform(
                                        alpha=120, 
                                        sigma=120 * 0.05, 
                                        alpha_affine=120 * 0.03,
                                        border_mode=cv2.BORDER_REFLECT_101,
                                        mask_value=0,
                                        p=0.5
                                    )
                                )
            elif key == "grid":
                transform.append(A.GridDistortion(
                            num_steps=5, 
                            distort_limit=0.3,
                            border_mode=cv2.BORDER_REFLECT_101,
                            mask_value=0,
                            p=0.5
                        )
                    )
        aug_pipeline = A.Compose(transform)
        self.augmentData(aug_pipeline, nb_copy, progress)

    def augmentData(self, aug_pipeline, nb_copy, progress):
        if self.output_augmentation_folder is None:
            print("[-] Error in Backend.augmentData: output_augmentation_folder is None")
            return 

        total = len(self.img_list)
        img_path = self.img_list[0]
        first_img_Path = Path(img_path)
        config_src = os.path.join(first_img_Path.parent.parent, "config.json")
        config_dest = os.path.join(self.output_augmentation_folder, "config.json")

        shutil.copy(config_src, config_dest)
        for idx, path in enumerate(self.img_list):
            currentPath = Path(path)
            labelPath = os.path.join(currentPath.parent.parent, "labels", currentPath.stem + '.png')
            
            if not os.path.exists(labelPath):
                continue
            
            image_np = np.array(Image.open(currentPath).convert("RGB"))
            mask_np = np.array(Image.open(labelPath)) 

            os.makedirs(os.path.join(self.output_augmentation_folder, "imgs"), exist_ok=True)
            os.makedirs(os.path.join(self.output_augmentation_folder, "labels"), exist_ok=True)

            for i in range(nb_copy):
                augmented = aug_pipeline(image=image_np, mask=mask_np)
                aug_image = augmented["image"]
                aug_mask = augmented["mask"]
                new_filename_img = f"{currentPath.stem}_aug{i+1}{currentPath.suffix}"
                new_filename_mask = f"{currentPath.stem}_aug{i+1}.png"

                aug_img_path = os.path.join(self.output_augmentation_folder, "imgs", new_filename_img)
                aug_mask_path = os.path.join(self.output_augmentation_folder, "labels", new_filename_mask)

                Image.fromarray(aug_image).save(aug_img_path)
                Image.fromarray(aug_mask.astype(np.uint8)).save(aug_mask_path)

            if progress:
                progress.setValue(idx + 1)
                progress.setLabelText(f"Processing : {currentPath.name} ({idx + 1}/{total})")

        if progress:
            progress.setValue(total)

    def next_aug_img_in_dataset(self):
        self.idx_img_dataset_viewer+=1
    def prev_aug_img_in_dataset(self):
        self.idx_img_dataset_viewer -=1
    def calculated_stats_on_image(self):
        pixel_counts = [0.0 for i in range (self.nb_classes)]
        
        current_img_path = Path(self.img_dataset_viewer[self.idx_img_dataset_viewer])
        current_label_path = os.path.join(current_img_path.parent.parent, "labels", current_img_path.stem + ".png")
        if not os.path.exists(current_label_path):
            print(f"[-] Error in backend.calculated_stats_on_image: {current_label_path} doesn't exist!")
            return pixel_counts

        mask_np = cv2.imread(current_label_path, cv2.IMREAD_UNCHANGED)
        if mask_np is None:
            return pixel_counts

        for i in range(self.nb_classes):
            class_pixels = int(np.sum((mask_np & (1 << i)) > 0))
            pixel_counts[i] =(class_pixels)

        print(pixel_counts)
        return pixel_counts

        

    def calculated_statistics(self):
        # This function will return the proportion of each class
        if self.augmented_dataset_path is None:
            return None
        pixel_counts = [0.0 for i in range (self.nb_classes)]
        total_pixels_dataset = 0.0
        
        labels_path = os.path.join(self.augmented_dataset_path, "labels")
        for root, dirs, files in os.walk(labels_path):
            for file in files:
                current_label_path = os.path.join(root, file)
                mask_np = cv2.imread(current_label_path, cv2.IMREAD_UNCHANGED)
                if mask_np is None:
                    continue
                total_pixels_dataset += (mask_np.shape[0] * mask_np.shape[1])

                for i in range(self.nb_classes):
                    class_pixels = int(np.sum((mask_np & (1 << i)) > 0))
                    pixel_counts[i] +=(class_pixels)
        if total_pixels_dataset > 0:
            proportions = [round(val / total_pixels_dataset * 100.0, 2) for val in pixel_counts]
        else:
            proportions = pixel_counts

        return proportions
        
