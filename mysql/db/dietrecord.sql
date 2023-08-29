-- MySQL Script generated by MySQL Workbench
-- Wed Feb 22 22:39:19 2023
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema dietrecorddb
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema dietrecorddb
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `dietrecorddb` DEFAULT CHARACTER SET utf8 ;
USE `dietrecorddb` ;

-- -----------------------------------------------------
-- Table `dietrecorddb`.`MyGeometry`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `dietrecorddb`.`MeetingRecords` ;

CREATE TABLE IF NOT EXISTS `dietrecorddb`.`MeetingRecords` (
    id INT PRIMARY KEY AUTO_INCREMENT,
    issueID VARCHAR(255),
    imageKind VARCHAR(255),
    searchObject INT,
    session INT,
    nameOfHouse VARCHAR(255),
    nameOfMeeting VARCHAR(255),
    issue VARCHAR(255),
    date DATE,
    closing TEXT,
    meetingURL TEXT,
    pdfURL TEXT
)
ENGINE = InnoDB;


DROP TABLE IF EXISTS `dietrecorddb`.`SpeechRecords` ;

CREATE TABLE IF NOT EXISTS `dietrecorddb`.`SpeechRecords` (
    id INT PRIMARY KEY AUTO_INCREMENT,
    meeting_id INT,
    speechID VARCHAR(255),
    speechOrder INT,
    speaker VARCHAR(255),
    speakerYomi VARCHAR(255),
    speakerGroup VARCHAR(255),
    speakerPosition VARCHAR(255),
    speakerRole VARCHAR(255),
    speech TEXT,
    startPage INT,
    createTime DATETIME,
    updateTime DATETIME,
    speechURL TEXT,
    FOREIGN KEY (meeting_id) REFERENCES MeetingRecords(id)
)
ENGINE = InnoDB;



SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
