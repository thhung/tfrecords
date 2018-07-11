###################################################################
## INRIA - STARS 2018
## Author: Hung NGUYEN
###################################################################

"""
    This script contains code to convert the Caltech - like dataset to the TFRecords with multiple variations could be
    set and be handled.
"""
#####import numpy as np
import os
from time import sleep
import cv2
from create_tfrecords import create

## path of folder contains the images of dataset
images_path = ""

## path of folder contains the annotations which should match wi
annotations_path = ""

## image extension
img_extension = ".jpg"

def get_size_img(full_path_image):
    exist = os.path.exists(full_path_image)
    if not exist:
        print("%r doesn't exist" % full_path_image)
    img = cv2.imread(full_path_image)
    if img is not None:
        return img.shape
    return None, None, None

DEBUG = False

class TFRecordCreator:
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

        if DEBUG: print("Init sucessful!!")



    def create_record_for_single_image(self, filename):
        with open(self._annotations_path + "/" + filename) as file:
            content = file.readlines()
            annotations = []
            for line in content[1:]:
                if line.startswith("person"):
                    single_annotation = line.split()
                    annotations.append(single_annotation[1:5])
        if len(annotations) > 0:
            image_record = {}

            ## get rid of .txt
            if not filename[:-4].endswith(img_extension):
                filename = filename[:-4] + img_extension
            else:
                filename = filename[:-4]

            image_record["filename"] = self._images_path + filename

            height, width, channels = get_size_img(image_record["filename"])

            if height is None:
                return None, 0

            image_record["height"] = height
            image_record["width"] = width
            image_record["channels"] = channels
            image_record["format"] = img_extension

            class_dict = {
                            "label" : 1,
                            "text" : "person",
                            "conf" : 1.
                         }

            image_record["class"] = class_dict

            temp_obj_dict = {}
            temp_obj_dict["count"] = len(annotations)
            temp_obj_dict["area"] = []
            temp_obj_dict["id"] = []
            temp_x_min = []
            temp_x_max = []
            temp_y_min = []
            temp_y_max = []

            for anno in annotations:
                x,y,w,h = [int(float(_)) for _ in anno]
                normal_x_min = x/width
                normal_y_min = y/height
                normal_x_max = (x + w)/width
                nornal_y_max = (y + h)/height

                temp_x_min.append(normal_x_min)
                temp_x_max.append(normal_x_max)
                temp_y_min.append(normal_y_min)
                temp_y_max.append(nornal_y_max)

                temp_obj_dict["area"].append((normal_x_max - normal_x_min) * (nornal_y_max - normal_y_min) )

            temp_obj_dict["bbox"] = {}
            temp_obj_dict["bbox"]["xmin"] = temp_x_min
            temp_obj_dict["bbox"]["xmax"] = temp_x_max
            temp_obj_dict["bbox"]["ymin"] = temp_y_min
            temp_obj_dict["bbox"]["ymax"] = temp_y_max
            nb_object = int(len(annotations))
            temp_obj_dict["bbox"]["score"] = [1.0] * nb_object
            temp_obj_dict["bbox"]["label"] = [1] * nb_object
            temp_obj_dict["bbox"]["conf"] = [1.0] * nb_object
            temp_obj_dict["bbox"]["text"] = ["person"] * nb_object
            temp_obj_dict["id"] = range(nb_object)

            image_record["object"] = temp_obj_dict

            return image_record, nb_object

        ## No object annotation in current image.
        return None, 0

    def create_records_caltech_format(self,dataset_name = "train" , output_path = ".", num_shards = 10, num_threads=5, store_images = True):

        dataset = []
        directory = os.fsencode(self._annotations_path)

        nb_images = 0
        files = os.listdir(directory)
        nb_files = len(files)
        for file in files:
            filename = os.fsdecode(file)
            if filename.endswith(".txt"):
                record, nb_object = self.create_record_for_single_image(filename)
                if nb_object > 0: dataset.append(record)
            nb_images += 1
            #if nb_images > 9: break
            sleep(0.1)
            # Update Progress Bar
            TFRecordCreator.printProgressBar(nb_images + 1, nb_files, prefix='Progress:', suffix='Complete', length=50)
            if DEBUG: print("Done, ", nb_images)

        failed_images = create(
            dataset=dataset,
            dataset_name=dataset_name,
            output_directory= output_path,
            num_shards=num_shards,
            num_threads=num_threads,
            store_images=store_images
        )

        ## in case of failed:
        print("%d images failed." % (len(failed_images),))
        for image_data in failed_images:
            print("Image %s: %s" % (image_data['id'], image_data['error_msg']))

    @staticmethod
    # Print iterations progress
    def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
        """
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
        # Print New Line on Complete
        if iteration == total:
            print()
