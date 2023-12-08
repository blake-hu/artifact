-- CREATE DATABASE AIartDetectionApp;

USE AIartDetectionApp;

DROP TABLE IF EXISTS imageMetadata;
DROP TABLE IF EXISTS imagePredictions;

CREATE TABLE imageMetadata
(
    image_id       int not null AUTO_INCREMENT,
    time_uploaded    DATETIME,
    image_size        int not null,
    file_name     varchar(128) not null,
    bucket_key    varchar(128) not null,
    PRIMARY KEY (image_id),
    UNIQUE      (bucket_key)
);

ALTER TABLE imageMetadata AUTO_INCREMENT = 00001;  -- starting value

CREATE TABLE imagePredictions
(
    prediction_id      int not null AUTO_INCREMENT,
    image_id           int not null,
    precentage_ai      DECIMAL(7, 5) NOT NULL,
    model_version      varchar(128) not null,
    PRIMARY KEY (prediction_id),
    FOREIGN KEY (image_id) REFERENCES imageMetadata(image_id)
);

ALTER TABLE imagePredictions AUTO_INCREMENT = 10001;  -- starting value

DROP USER IF EXISTS 'final-project-read-write';

CREATE USER 'final-project-read-write' IDENTIFIED BY 'BASH-is-the-best';

GRANT ALL PRIVILEGES ON AIartDetectionApp.* 
      TO 'final-project-read-write';
      
FLUSH PRIVILEGES;