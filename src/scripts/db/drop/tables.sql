create table `users`
(
	`id` int unsigned auto_increment,
	`first_name` varchar(64) not null,
	`last_name` varchar(64) not null,
	`email_address` varchar(64) unique not null,
	`password` blob not null,

	primary key (`id`)
);

create table `teachers`
(
	`id` int unsigned auto_increment,
	`user_id` int unsigned not null,

	primary key (`id`),
	foreign key (`user_id`) references `users` (`id`) on delete cascade on update restrict
);

create table `students`
(
	`id` int unsigned auto_increment,
	`user_id` int unsigned not null,

	primary key (`id`),
	foreign key (`user_id`) references `users` (`id`) on delete cascade on update restrict
);

create table `assignments`
(
	`id` int unsigned auto_increment,
	`teacher_id` int unsigned not null,
	`title` varchar(255) not null,
	`due_date` datetime,

	primary key (`id`),
	foreign key (`teacher_id`) references `teachers` (`id`) on delete cascade on update restrict
);

create table `assignment_questions`
(
	`id` int unsigned auto_increment,
	`assignment_id` int unsigned not null,
	`text` text not null,
	`type` enum ('OPEN_ENDED', 'MULTIPLE_CHOICE') not null,
	`points` int unsigned not null,

	primary key (`id`),
	foreign key (`assignment_id`) references `assignments` (`id`) on delete cascade on update restrict
);

create table `assignment_question_options`
(
	`id` int unsigned auto_increment,
	`question_id` int unsigned not null,
	`text` text not null,
	`is_correct` boolean,

	primary key (`id`),
	foreign key (`question_id`) references `assignment_questions` (`id`) on delete cascade on update restrict
);

create table `assignment_attempts`
(
	`id` int unsigned auto_increment,
	`student_id` int unsigned not null,
	`assignment_id` int unsigned not null,
	`submission_date` datetime not null,
	`graded` boolean not null,

	primary key (`id`),
	foreign key (`student_id`) references `students` (`id`) on delete cascade on update restrict,
	foreign key (`assignment_id`) references `assignments` (`id`) on delete cascade on update restrict
);

create table `assignment_attempt_responses`
(
	`id` int unsigned auto_increment,
	`attempt_id` int unsigned not null,
	`question_id` int unsigned not null,
	`option_id` int unsigned not null,
	`graded` boolean not null,

	primary key (`id`),
	foreign key (`attempt_id`) references `assignment_attempts` (`id`) on delete cascade on update restrict,
	foreign key (`question_id`) references `assignment_questions` (`id`) on delete cascade on update restrict,
	foreign key (`option_id`) references `assignment_question_options` (`id`) on delete cascade on update restrict
);
