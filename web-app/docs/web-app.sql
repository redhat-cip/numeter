--
-- Current Database: `numeter`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `numeter` /*!40100 DEFAULT CHARACTER SET latin1 */;

USE `numeter`;

drop table IF EXISTS users;
CREATE TABLE users (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    password VARCHAR(50),
    isadmin INT NOT NULL DEFAULT  '0',
    graph INT NOT NULL DEFAULT  '1',
    created DATETIME DEFAULT NULL,
    modified DATETIME DEFAULT NULL
);
INSERT INTO  `numeter`.`users` (`id` ,`username` ,`password` ,`isadmin`, `graph` ,`created` ,`modified`)VALUES (1 ,  'admin',  'f99550a09dda1afdc4e8e5dd22e9bcae75db7b1d',  '1', 0, NULL , NULL);

drop table IF EXISTS groups;
CREATE TABLE groups (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    created DATETIME DEFAULT NULL,
    modified DATETIME DEFAULT NULL
);
INSERT INTO  `numeter`.`groups` (`id` ,`name`, `created`, `modified`) VALUES (1 ,  'admin', NULL, NULL);

drop table IF EXISTS group_user_memberships;
CREATE TABLE group_user_memberships (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(10) unsigned NOT NULL,
  `group_id` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;
INSERT INTO  `numeter`.`group_user_memberships` (`id` ,`user_id` ,`group_id`) VALUES (NULL ,  '1',  '1');

drop table IF EXISTS hosts;
CREATE TABLE hosts (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    addr VARCHAR(50),
    hostID VARCHAR(50),
    storageID VARCHAR(50),
    created DATETIME DEFAULT NULL,
    modified DATETIME DEFAULT NULL
);

drop table IF EXISTS group_host_memberships;
CREATE TABLE group_host_memberships (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `host_id` int(10) unsigned NOT NULL,
  `group_id` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;


