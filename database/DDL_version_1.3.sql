-- MySQL Script generated by MySQL Workbench
-- Sat Nov  9 14:42:33 2024
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema default_schema
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema project_brewery
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `project_brewery` ;

-- -----------------------------------------------------
-- Schema project_brewery
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `project_brewery` DEFAULT CHARACTER SET utf8 ;
USE `project_brewery` ;

-- -----------------------------------------------------
-- Table `project_brewery`.`Batch`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `project_brewery`.`Batch` ;

CREATE TABLE IF NOT EXISTS `project_brewery`.`Batch` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) CHARACTER SET 'cp1250' NULL DEFAULT NULL,
  `productionDate` VARCHAR(45) NULL DEFAULT NULL,
  `Recipe_id` INT NOT NULL,
  `initialQuantity` INT NULL DEFAULT 0 COMMENT 'depends on the batcg size',
  `availableQuantity` INT NULL DEFAULT 0 COMMENT 'remaining quantity after issue to customer',
  `dateOfExpiry` DATETIME NULL DEFAULT NULL,
  `User_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_Batch_User1_idx` (`User_id` ASC) VISIBLE,
  CONSTRAINT `fk_Batch_User1`
    FOREIGN KEY (`User_id`)
    REFERENCES `project_brewery`.`User` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `project_brewery`.`GRN`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `project_brewery`.`GRN` ;

CREATE TABLE IF NOT EXISTS `project_brewery`.`GRN` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `issuedDate` VARCHAR(45) CHARACTER SET 'cp1250' NULL DEFAULT NULL,
  `quantity` INT NULL DEFAULT 0,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `project_brewery`.`GRN_has_Ingredient`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `project_brewery`.`GRN_has_Ingredient` ;

CREATE TABLE IF NOT EXISTS `project_brewery`.`GRN_has_Ingredient` (
  `GRN_id` INT NOT NULL,
  `Ingredient_id` INT NOT NULL,
  PRIMARY KEY (`GRN_id`, `Ingredient_id`),
  INDEX `fk_GRN_has_Ingredient_Ingredient1_idx` (`Ingredient_id` ASC) VISIBLE,
  INDEX `fk_GRN_has_Ingredient_GRN1_idx` (`GRN_id` ASC) VISIBLE,
  CONSTRAINT `fk_GRN_has_Ingredient_GRN1`
    FOREIGN KEY (`GRN_id`)
    REFERENCES `project_brewery`.`GRN` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_GRN_has_Ingredient_Ingredient1`
    FOREIGN KEY (`Ingredient_id`)
    REFERENCES `project_brewery`.`Ingredient` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `project_brewery`.`Ingredient`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `project_brewery`.`Ingredient` ;

CREATE TABLE IF NOT EXISTS `project_brewery`.`Ingredient` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) CHARACTER SET 'cp1250' NULL DEFAULT NULL,
  `currentQuantity` INT NULL DEFAULT 0,
  `description` VARCHAR(255) NULL,
  `image` BLOB NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `project_brewery`.`Location`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `project_brewery`.`Location` ;

CREATE TABLE IF NOT EXISTS `project_brewery`.`Location` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) CHARACTER SET 'cp1250' NULL DEFAULT NULL,
  `address` VARCHAR(250) NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `project_brewery`.`Location_has_User`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `project_brewery`.`Location_has_User` ;

CREATE TABLE IF NOT EXISTS `project_brewery`.`Location_has_User` (
  `Location_id` INT NOT NULL,
  `User_id` INT NOT NULL,
  PRIMARY KEY (`Location_id`, `User_id`),
  INDEX `fk_Location_has_User_User1_idx` (`User_id` ASC) VISIBLE,
  INDEX `fk_Location_has_User_Location1_idx` (`Location_id` ASC) VISIBLE,
  CONSTRAINT `fk_Location_has_User_Location1`
    FOREIGN KEY (`Location_id`)
    REFERENCES `project_brewery`.`Location` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Location_has_User_User1`
    FOREIGN KEY (`User_id`)
    REFERENCES `project_brewery`.`User` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `project_brewery`.`Product`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `project_brewery`.`Product` ;

CREATE TABLE IF NOT EXISTS `project_brewery`.`Product` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NULL DEFAULT NULL,
  `currentQuantity` INT NULL DEFAULT 0,
  `description` VARCHAR(250) NULL DEFAULT NULL,
  `ProductType_id` INT NOT NULL,
  PRIMARY KEY (`id`, `ProductType_id`),
  INDEX `fk_Product_ProductType_idx` (`ProductType_id` ASC) VISIBLE,
  CONSTRAINT `fk_Product_ProductType`
    FOREIGN KEY (`ProductType_id`)
    REFERENCES `project_brewery`.`ProductType` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `project_brewery`.`ProductType`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `project_brewery`.`ProductType` ;

CREATE TABLE IF NOT EXISTS `project_brewery`.`ProductType` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) CHARACTER SET 'cp1250' NULL DEFAULT NULL,
  `code` VARCHAR(10) NULL DEFAULT NULL,
  `batchSize` INT NULL DEFAULT 0,
  `expireDuration` INT NULL DEFAULT 0,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `project_brewery`.`Recipe`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `project_brewery`.`Recipe` ;

CREATE TABLE IF NOT EXISTS `project_brewery`.`Recipe` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) CHARACTER SET 'cp1250' NULL DEFAULT NULL,
  `description` VARCHAR(256) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `project_brewery`.`Recipe_has_Ingredient`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `project_brewery`.`Recipe_has_Ingredient` ;

CREATE TABLE IF NOT EXISTS `project_brewery`.`Recipe_has_Ingredient` (
  `Recipe_id` INT NOT NULL,
  `Ingredient_id` INT NOT NULL,
  `quantity` INT NULL DEFAULT 0,
  PRIMARY KEY (`Recipe_id`, `Ingredient_id`),
  INDEX `fk_Recipe_has_Ingredient_Ingredient1_idx` (`Ingredient_id` ASC) VISIBLE,
  INDEX `fk_Recipe_has_Ingredient_Recipe1_idx` (`Recipe_id` ASC) VISIBLE,
  CONSTRAINT `fk_Recipe_has_Ingredient_Recipe1`
    FOREIGN KEY (`Recipe_id`)
    REFERENCES `project_brewery`.`Recipe` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Recipe_has_Ingredient_Ingredient1`
    FOREIGN KEY (`Ingredient_id`)
    REFERENCES `project_brewery`.`Ingredient` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `project_brewery`.`Recipe_has_ProductType`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `project_brewery`.`Recipe_has_ProductType` ;

CREATE TABLE IF NOT EXISTS `project_brewery`.`Recipe_has_ProductType` (
  `Recipe_id` INT NOT NULL,
  `ProductType_id` INT NOT NULL,
  PRIMARY KEY (`Recipe_id`, `ProductType_id`),
  INDEX `fk_Recipe_has_ProductType_ProductType1_idx` (`ProductType_id` ASC) VISIBLE,
  INDEX `fk_Recipe_has_ProductType_Recipe1_idx` (`Recipe_id` ASC) VISIBLE,
  CONSTRAINT `fk_Recipe_has_ProductType_Recipe1`
    FOREIGN KEY (`Recipe_id`)
    REFERENCES `project_brewery`.`Recipe` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Recipe_has_ProductType_ProductType1`
    FOREIGN KEY (`ProductType_id`)
    REFERENCES `project_brewery`.`ProductType` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `project_brewery`.`User`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `project_brewery`.`User` ;

CREATE TABLE IF NOT EXISTS `project_brewery`.`User` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NULL DEFAULT NULL,
  `email` VARCHAR(45) NULL DEFAULT NULL,
  `contactNo` VARCHAR(45) NULL DEFAULT NULL,
  `UserType_id` INT NOT NULL,
  `createdOn` DATETIME NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_People_PeopleType1_idx` (`UserType_id` ASC) VISIBLE,
  CONSTRAINT `fk_People_PeopleType1`
    FOREIGN KEY (`UserType_id`)
    REFERENCES `project_brewery`.`UserType` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `project_brewery`.`UserType`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `project_brewery`.`UserType` ;

CREATE TABLE IF NOT EXISTS `project_brewery`.`UserType` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;