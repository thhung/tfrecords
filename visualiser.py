import os

import cv2

IMG_EXTENSION = ".jpg"

ANNOTATION_EXT = ".txt"

class Visualiser:
    def __init__(self, annotations_path, images_path):
        assert os.path.isdir(
            images_path), "%r is not a valid folder path, please check if this folder exists" % images_path
        assert os.path.isdir(annotations_path), \
            "%r is not a valid folder path, please check if this folder exists" % annotations_path

        self._annotations_path = annotations_path
        if not self._annotations_path.endswith("/"):
            self._annotations_path = self._annotations_path + "/"

        self._images_path = images_path
        if not self._images_path.endswith("/"):
            self._images_path = self._images_path + "/"

    @staticmethod
    def create_visual_image(image, bbxs, color = (255,0,0), thickness = 5,xywh = True):
        for bb in bbxs:
            x_min, y_min, x_max, y_max = bb
            if xywh:
                ## x_max is width
                x_max = x_min + x_max
                ## y_max is height
                y_max = y_min + y_max
            cv2.rectangle(image, (x_min, y_min), (x_max, y_max), color, thickness= thickness)
        return image

    @staticmethod
    def visualise(image, bxs, win_name = "From Visualizer",wait_key = 0,color = (255,0,0), thickness = 5,xywh = True):
        visualised_image = Visualiser.create_visual_image(image, bxs, color, thickness,xywh)
        cv2.imshow(visualised_image, win_name)
        cv2.waitKey(wait_key)

    @staticmethod
    def get_bbox_from_file(file_name):
        with open(file_name) as file:
            content = file.readlines()
            annotations = []
            for line in content[1:]:
                if line.startswith("person"):
                    single_annotation = line.split()
                    annotations.append((int(x) for x in single_annotation[1:5]))
        return annotations

    def visualise_file(self, file_name, visual = True, save = False, output="./"):
        if file_name.endswith(".txt") or file_name.endswith(".jpg"):
            file_name = file_name[:-4]
        full_image_path = self._images_path + file_name + IMG_EXTENSION
        exist = os.path.exists(full_image_path)

        assert exist, "Image file doesn't exist at %r" % full_image_path

        full_annotation_path = self._annotations_path + file_name + ANNOTATION_EXT

        exist = os.path.exists(full_annotation_path)

        if not exist:
            full_annotation_path = self._annotations_path + file_name + IMG_EXTENSION + ANNOTATION_EXT
            exist = os.path.exists(full_annotation_path)

        assert exist, "No annotation file found with both pattern file_name.jpg.txt or file_name.txt"

        image = cv2.imread(full_image_path)
        bbxs = Visualiser.get_bbox_from_file(full_annotation_path)

        if visual:
            Visualiser.visualise(image, bbxs, win_name=file_name)

        if save:
            v_image = Visualiser.create_visual_image(image, bbxs)
            if not output.endswith("/"):
                output = output + "/"
            cv2.imwrite(output + "visualised_"+ file_name,v_image)


