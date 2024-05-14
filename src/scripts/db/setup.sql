drop database if exists `cset160final`;

create database if not exists `cset160final`;
use `cset160final`;

create table `users`
(
	`id` int unsigned auto_increment,
	`first_name` varchar(64) not null,
	`last_name` varchar(64) not null,
	`email_address` varchar(64) unique not null,
	`password` blob not null,
	`account_type` enum ("teacher", "student") not null,

	primary key (`id`)
);

create table `assignments`
(
	`id` int unsigned auto_increment,
	`user_id` int unsigned not null,
	`title` varchar(255) not null,
	`points` int unsigned not null,

	primary key (`id`),
	foreign key (`user_id`) references `users` (`id`) on delete restrict on update restrict
);

create table `assignment_questions`
(
	`id` int unsigned auto_increment,
	`assignment_id` int unsigned not null,
	`question` text not null,

	primary key (`id`),
	foreign key (`assignment_id`) references `assignments` (`id`) on delete cascade on update restrict
);

create table `assignment_attempts`
(
	`id` int unsigned auto_increment,
	`user_id` int unsigned not null,
	`assignment_id` int unsigned not null,
	`submission_date` datetime not null,
	`graded` boolean not null,

	primary key (`id`),
	foreign key (`user_id`) references `users` (`id`) on delete restrict on update restrict,
	foreign key (`assignment_id`) references `assignments` (`id`) on delete cascade on update restrict
);

create table `assignment_attempt_responses`
(
	`id` int unsigned auto_increment,
	`attempt_id` int unsigned not null,
	`question_id` int unsigned not null,
	`response` text not null,

	primary key (`id`),
	foreign key (`attempt_id`) references `assignment_attempts` (`id`) on delete cascade on update restrict,
	foreign key (`question_id`) references `assignment_questions` (`id`) on delete cascade on update restrict
);
