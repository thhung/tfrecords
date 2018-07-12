from create_caltech_tfrecords import TFRecordCreator

import argparse
print("Start_mess")
parser = argparse.ArgumentParser(description = "Convert the Caltech-like dataset to TFRecords")
parser.add_argument("images_path", help=" where you store the image of dataset")
parser.add_argument("annot_path", help=" where you store the annotation of dataset")
parser.add_argument("-o","--output", help="where to store the TFRecords", default="./")
parser.add_argument("-dsn","--dataset_name", help="name of dataset you would like to put", default="train")
parser.add_argument("--json", help = "load the precomputed json to dict")

args = parser.parse_args()

print("Done parse")

record_creator = TFRecordCreator(args.annot_path, args.images_path)
if args.json is not None:
    record_creator.create_record_from_saved_dict(args.json, dataset_name=args.dataset_name,output_path= args.output)
else:
    record_creator.create_records_caltech_format(dataset_name=args.dataset_name,output_path= args.output,save_dict=True)
print("the TFRecords  has been created!!!")
