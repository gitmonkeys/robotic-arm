Generate TF records
python generate_tfrecord.py --csv_input=images/test_labels.csv --image_dir=images/test --output_path=test.record
python generate_tfrecord.py --csv_input=images/train_labels.csv --image_dir=images/train --output_path=train.record

Start training
python model_main_tf2.py --pipeline_config_path==ssd_efficientdet_d0_512x512_coco17_tpu-8.config  --model_dir==training --alsologtostderr

https://developer.nvidia.com/cuda-toolkit-archive
https://developer.nvidia.com/cudnn
