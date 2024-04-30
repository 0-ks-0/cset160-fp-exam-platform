set FOREIGN_KEY_CHECKS = 0;

drop table if exists `users`;
drop table if exists `teachers`;
drop table if exists `students`;

drop table if exists `assignments`;
drop table if exists `assignment_questions`;
drop table if exists `assignment_question_options`;

drop table if exists `assignment_attempts`;
drop table if exists `assignment_attempt_responses`;

set FOREIGN_KEY_CHECKS = 1;
