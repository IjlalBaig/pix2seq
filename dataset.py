from utils import read_json

from pathlib import Path
from PIL import Image
from torch.utils.data import Dataset


class CocoDetectionDataset(Dataset):
    def __init__(self, filepath, transform=None):
        super(CocoDetectionDataset, self).__init__()
        self.file_path = filepath
        self.transform = transform
        self.image_detections = self.load_image_detections()

    def load_image_detections(self):
        coco_data = read_json(self.file_path)
        image_data = self._parse_coco_image_data(coco_data)
        categories = self._parse_coco_categories(coco_data)
        for annotation in coco_data["annotations"]:
            image_id = annotation["image_id"]
            bbox = annotation["bbox"]
            category = categories[annotation["category_id"]]
            detection = dict(bbox=bbox, category=category)
            image_data[image_id]["detections"] = image_data[image_id].get("detections", [])
            image_data[image_id]["detections"] += [detection]
        image_detections = [im_data for _, im_data in image_data.items()]
        return image_detections

    @staticmethod
    def _parse_coco_categories(coco_data):
        categories = dict()
        for category in coco_data.get("categories", []):
            _id = category["id"]
            name = category["name"]
            categories[_id] = name
        return categories

    def _parse_coco_image_data(self, coco_data):
        image_data = dict()
        for data in coco_data.get("images", []):
            _id = data["id"]
            file_name = data["file_name"]
            image_dir_name = Path(self.file_path).stem.split("_")[-1]
            image_file_path = Path(self.file_path).parents[1].joinpath("images", image_dir_name, file_name).as_posix()
            image_data[_id] = dict(path=image_file_path)
        return image_data

    def __len__(self):
        return self.image_detections.__len__()

    def __getitem__(self, idx):
        im_data = self.image_detections[idx]

        image = Image.open(im_data["path"])
        bboxes = [d["bbox"] for d in im_data["detections"]]
        categories = [d["category"] for d in im_data["detections"]]
        sample = dict(image=image, bboxes=bboxes, categories=categories)
        if self.transform is not None:
            sample = self.transform(sample)
        return sample
