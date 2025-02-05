CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;
DROP TABLE IF EXISTS Pictures CASCADE;
DROP TABLE IF EXISTS Users CASCADE;
DROP TABLE IF EXISTS Tag;

CREATE TABLE Users (
    user_id int4  AUTO_INCREMENT,
    email varchar(255) NOT NULL UNIQUE,
    password varchar(255) NOT NULL,
    
	first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    birth_date DATE NOT NULL,
    town VARCHAR(255),
    gender ENUM('M','F','N'),
	CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE Album (
	album_id VARCHAR(255) PRIMARY KEY,
    album_name VARCHAR(255),
    created_date DATE,
    album_owner VARCHAR(255),
    FOREIGN KEY (album_owner) REFERENCES Users(userid)
    );

CREATE TABLE Pictures
(
  picture_id int4  AUTO_INCREMENT,
  user_id int4,
  imgdata longblob ,
  caption VARCHAR(255),
  album VARCHAR(255),
  
  INDEX upid_idx (user_id),
  CONSTRAINT pictures_pk PRIMARY KEY (picture_id),
  FOREIGN KEY (album) REFERENCES Album(album_id)
);

create table Tag (
	Word_Description VARCHAR(30) PRIMARY KEY
);

create table Friend (
	user_id VARCHAR(255) NOT NULL,
    friend_id VARCHAR(255) NOT NULL,
    PRIMARY KEY(User_ID, Friend_ID),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (friend_id) REFERENCES Users(user_id)
);

INSERT INTO Users (email, password) VALUES ('test@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test1@bu.edu', 'test');
