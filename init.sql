CREATE DATABASE IF NOT EXISTS wiki;
CREATE DATABASE IF NOT EXISTS celery;

USE wiki;

CREATE TABLE IF NOT EXISTS `continent` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `population` int DEFAULT NULL,
  `area` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `country` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `population` int DEFAULT NULL,
  `area` int DEFAULT NULL,
  `hospitals_count` int DEFAULT NULL,
  `national_parks_count` int DEFAULT NULL,
  `continent_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `continent_id` (`continent_id`),
  CONSTRAINT `country_ibfk_1` FOREIGN KEY (`continent_id`) REFERENCES `continent` (`id`)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `city` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `population` int DEFAULT NULL,
  `area` int DEFAULT NULL,
  `road_count` int DEFAULT NULL,
  `tree_count` int DEFAULT NULL,
  `country_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `country_id` (`country_id`),
  CONSTRAINT `city_ibfk_1` FOREIGN KEY (`country_id`) REFERENCES `country` (`id`)
) ENGINE=InnoDB;

DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER IF NOT EXISTS `city_BEFORE_INSERT` BEFORE INSERT ON `city` FOR EACH ROW BEGIN
	DECLARE country_pop INT;
	DECLARE country_ar INT;
    DECLARE total_pop INT;
    DECLARE total_ar INT;
    
    SELECT population INTO country_pop FROM country WHERE country.id=NEW.country_id;
    IF country_pop < NEW.population THEN
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='City Population cannot be more than Country population';
	END IF;
    
    SELECT area INTO country_ar FROM country WHERE country.id=NEW.country_id;
    IF country_ar < NEW.area THEN
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='City Area cannot be more than Country Area';
	END IF;
    
    SELECT sum(population)+NEW.population INTO total_pop FROM city WHERE city.country_id=NEW.country_id;
	IF total_pop > country_pop THEN
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Sum of population of cities for the country exceeds country population';
	END IF;
    
    SELECT sum(area)+NEW.area INTO total_ar FROM city WHERE city.country_id=NEW.country_id;
	IF total_ar > country_ar THEN
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Sum of area of cities for the country exceeds country area';
	END IF;
END */;;
DELIMITER ;

DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER IF NOT EXISTS `city_BEFORE_UPDATE` BEFORE UPDATE ON `city` FOR EACH ROW BEGIN
	DECLARE country_pop INT;
	DECLARE country_ar INT;
    DECLARE total_pop INT;
    DECLARE total_ar INT;
    
    SELECT population INTO country_pop FROM country WHERE country.id=NEW.country_id;
    IF country_pop < NEW.population THEN
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='City Population cannot be more than Country population';
	END IF;
    
    SELECT area INTO country_ar FROM country WHERE country.id=NEW.country_id;
    IF country_ar < NEW.area THEN
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='City Area cannot be more than Country Area';
	END IF;
    
    SELECT sum(population)+NEW.population INTO total_pop FROM city WHERE city.country_id=NEW.country_id;
	IF total_pop > country_pop THEN
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Sum of population of cities for the country exceeds country population';
	END IF;
    
    SELECT sum(area)+NEW.area INTO total_ar FROM city WHERE city.country_id=NEW.country_id;
	IF total_ar > country_ar THEN
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Sum of area of cities for the country exceeds country area';
	END IF;
END */;;
DELIMITER ;

DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER IF NOT EXISTS `country_BEFORE_INSERT` BEFORE INSERT ON `country` FOR EACH ROW BEGIN
	DECLARE continent_pop INT;
	DECLARE continent_ar INT;
    DECLARE total_pop INT;
    DECLARE total_ar INT;
    
    SELECT population INTO continent_pop FROM continent WHERE continent.id=NEW.continent_id;
    IF continent_pop < NEW.population THEN
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Country Population cannot be more than continent population';
	END IF;
    
    SELECT area INTO continent_ar FROM continent WHERE continent.id=NEW.continent_id;
    IF continent_ar < NEW.area THEN
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Country Area cannot be more than Continent Area';
	END IF;
    
    SELECT sum(population)+NEW.population INTO total_pop FROM country WHERE country.continent_id=NEW.continent_id;
	IF total_pop > continent_pop THEN
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Sum of population of countries for the continent exceeds continent population';
	END IF;
    
    SELECT sum(area)+NEW.area INTO total_ar FROM country WHERE country.continent_id=NEW.continent_id;
	IF total_ar > continent_ar THEN
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Sum of area of countries for the continent exceeds continent area';
	END IF;
END */;;
DELIMITER ;

DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER IF NOT EXISTS `country_BEFORE_UPDATE` BEFORE UPDATE ON `country` FOR EACH ROW BEGIN
	DECLARE continent_pop INT;
	DECLARE continent_ar INT;
    DECLARE total_pop INT;
    DECLARE total_ar INT;
    
    SELECT population INTO continent_pop FROM continent WHERE continent.id=NEW.continent_id;
    IF continent_pop < NEW.population THEN
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Country Population cannot be more than continent population';
	END IF;
    
    SELECT area INTO continent_ar FROM continent WHERE continent.id=NEW.continent_id;
    IF continent_ar < NEW.area THEN
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Country Area cannot be more than Continent Area';
	END IF;
    
    SELECT sum(population)+NEW.population INTO total_pop FROM country WHERE country.continent_id=NEW.continent_id;
	IF total_pop > continent_pop THEN
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Sum of population of countries for the continent exceeds continent population';
	END IF;
    
    SELECT sum(area)+NEW.area INTO total_ar FROM country WHERE country.continent_id=NEW.continent_id;
	IF total_ar > continent_ar THEN
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Sum of area of countries for the continent exceeds continent area';
	END IF;
END */;;
DELIMITER ;