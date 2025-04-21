-- FastAPIX 数据库初始化和表结构定义
-- 基于实际项目模型生成的SQL脚本

-- 创建数据库
CREATE DATABASE IF NOT EXISTS fastapix_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户并授权
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY 'ZH$$ewA38pjgyn';
GRANT ALL PRIVILEGES ON fastapix_db.* TO 'root'@'%';
FLUSH PRIVILEGES;

-- 使用数据库
USE fastapix_db;

-- 使用UTF8MB4字符集
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- 用户表 - 对应 apps/users/models.py 中的User类
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username` varchar(50) NOT NULL COMMENT '用户名',
  `email` varchar(100) NOT NULL COMMENT '邮箱',
  `hashed_password` varchar(100) NOT NULL COMMENT '密码哈希',
  `full_name` varchar(100) DEFAULT NULL COMMENT '全名',
  `is_active` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否激活',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_username` (`username`),
  UNIQUE KEY `ix_users_email` (`email`),
  KEY `ix_users_id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 注意：访问令牌不存储在数据库中，而是根据配置存储在Redis或内存中
-- 这样可以提高性能，并允许更好的令牌管理和失效处理

-- 可以在这里添加其他表结构...

SET FOREIGN_KEY_CHECKS = 1; 