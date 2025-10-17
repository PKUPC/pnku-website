SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS=0;

INSERT INTO `trigger` VALUES (1, 0, 0, '活动即将开始');
INSERT INTO `trigger` VALUES (2, 500, 1758452400, '序章开放');
INSERT INTO `trigger` VALUES (3, 1000, 1758456000, '活动开始');
INSERT INTO `trigger` VALUES (4, 9000, 1767182400, '活动结束');

INSERT INTO `announcement` VALUES (1, 1758369600, -1, 'GENERAL', '公告示例', '这是一个公告示例。');

INSERT INTO `game_policy` VALUES (1, 0, '{\"currency_increase_policy\": [{\"type\": \"HINT_POINT\", \"increase_policy\": [{\"begin_time_min\": \"2025-08-30 20:00\", \"increase_per_min\": 10}, {\"begin_time_min\": \"2025-09-27 11:00\", \"increase_per_min\": 100}]}], \"puzzle_passed_display\": [1, 2, 4, 8, 16, 32, 64, 96, 128], \"board_setting\": {\"begin_time\": \"2025-09-21 20:00:00\", \"end_time\": \"2025-12-31 20:00:00\", \"top_star_n\": 20}}');

INSERT INTO `user` VALUES (1, 1756728000000, 1756728000000, 'manual:admin', '{\"type\": \"manual\"}', 1, 'staff', NULL, '{\"nickname\": \"admin\", \"email\": \"manual@example.com\"}');

SET FOREIGN_KEY_CHECKS=1;
