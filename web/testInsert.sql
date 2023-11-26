USE AIartDetectionApp;
USE AIartDetectionApp;

INSERT INTO 
  imageMetadata(image_size, file_name, bucket_key)
  values(1024, 'test01.jpg',
         '6b0be043-1265-4c80-9719-fd8dbcda8fd4');
    
INSERT INTO 
  imagePredictions(image_id, precentage_ai, model_version)
  values(00001,
         .01235,
         '1-2-3');

