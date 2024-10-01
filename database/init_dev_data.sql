SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS=0;

INSERT INTO `trigger` VALUES (1, 0, 0, '活动即将开始');
INSERT INTO `trigger` VALUES (2, 500, 1718323200, '序章开放');
INSERT INTO `trigger` VALUES (3, 1000, 1718326800, '活动开始');
INSERT INTO `trigger` VALUES (4, 9000, 1726315200, '活动结束');

INSERT INTO `announcement` VALUES (1, 1718330400, -1, 'GENERAL', '公告示例', '这是一个公告示例。');

INSERT INTO `game_policy` VALUES (1, 0, '{\"default_spap\": 2, \"ap_increase_setting\": [{\"begin_time_min\": \"2024-07-13 20:00\", \"increase_per_min\": 10}], \"puzzle_passed_display\": [1, 2, 4, 8, 16, 32, 64, 96, 128], \"board_setting\": {\"begin_time\": \"2024-07-13 20:00:00\", \"end_time\": \"2024-09-14 09:00:00\", \"top_star_n\": 20}}');

INSERT INTO `user` VALUES (1, 1672502400000, 1672502400000, 'manual:kinami', '{\"type\": \"manual\"}', 1, 'staff', NULL, '{\"nickname\": \"kinami\", \"email\": \"manual@example.com\"}');

SET FOREIGN_KEY_CHECKS=1;