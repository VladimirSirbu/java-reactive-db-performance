DROP TABLE IF EXISTS student;

CREATE TABLE IF NOT EXISTS student (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    email_address VARCHAR(255),
    phone VARCHAR(20)
);

INSERT INTO student (first_name, last_name, email_address, phone) VALUES ('John', 'Doe', 'john.doe@example.com', '1234567890');
INSERT INTO student (first_name, last_name, email_address, phone) VALUES ('Jane', 'Smith', 'jane.smith@example.com', '9876543210');
INSERT INTO student (first_name, last_name, email_address, phone) VALUES ('Michael', 'Johnson', 'michael.johnson@example.com', '5555555555');
INSERT INTO student (first_name, last_name, email_address, phone) VALUES ('Emily', 'Brown', 'emily.brown@example.com', '1112223333');
INSERT INTO student (first_name, last_name, email_address, phone) VALUES ('David', 'Martinez', 'david.martinez@example.com', '4444444444');
INSERT INTO student (first_name, last_name, email_address, phone) VALUES ('Sarah', 'Wilson', 'sarah.wilson@example.com', '6666666666');
INSERT INTO student (first_name, last_name, email_address, phone) VALUES ('Jessica', 'Lee', 'jessica.lee@example.com', '7777777777');
INSERT INTO student (first_name, last_name, email_address, phone) VALUES ('Matthew', 'Taylor', 'matthew.taylor@example.com', '8888888888');
INSERT INTO student (first_name, last_name, email_address, phone) VALUES ('Daniel', 'Anderson', 'daniel.anderson@example.com', '9999999999');
INSERT INTO student (first_name, last_name, email_address, phone) VALUES ('Amanda', 'Thomas', 'amanda.thomas@example.com', '1212121212');
