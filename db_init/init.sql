-- Drop tables if they already exist to avoid conflicts
DROP TABLE IF EXISTS Votes;
DROP TABLE IF EXISTS Candidates;
DROP TABLE IF EXISTS Elections;
DROP TABLE IF EXISTS Users;

-- Create Users Table
CREATE TABLE IF NOT EXISTS Users (
    username VARCHAR(50) PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    last_login DATETIME
);

-- Insert Users data
INSERT INTO Users (username, email, password, last_login) VALUES
('harrypotter', 'harry@example.com', 'password1', NULL),
('hermionegranger', 'hermione@example.com', 'password2', NULL),
('ronweasley', 'ron@example.com', 'password3', NULL),
('dracomalfoy', 'draco@example.com', 'password4', NULL),
('ginnyweasley', 'ginny@example.com', 'password5', NULL),
('lunalovegood', 'luna@example.com', 'password6', NULL),
('nevillelongbottom', 'neville@example.com', 'password7', NULL),
('albusdumbledore', 'dumbledore@example.com', 'password8', NULL),
('severussnape', 'snape@example.com', 'password9', NULL),
('rubeushagrid', 'hagrid@example.com', 'password10', NULL);

-- Create Elections Table
CREATE TABLE IF NOT EXISTS Elections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    creator_username VARCHAR(50),
    FOREIGN KEY (creator_username) REFERENCES Users(username)
);

-- Insert Elections data
INSERT INTO Elections (name, description, start_time, end_time, creator_username) VALUES
('Best Wizard', 'Vote for the best wizard in the wizarding world.', '2024-11-10 10:00:00', '2024-11-17 10:00:00', 'harrypotter'),
('Best Witch', 'Vote for the best witch in the wizarding world.', '2024-11-18 10:00:00', '2024-11-25 10:00:00', 'hermionegranger'),
('Best Quidditch Player', 'Vote for the best Quidditch player of the year.', '2024-11-26 10:00:00', '2024-12-03 10:00:00', 'ginnyweasley'),
('Most Influential Wizard', 'Vote for the most influential wizard in the community.', '2024-12-04 10:00:00', '2024-12-11 10:00:00', 'albusdumbledore'),
('Best Magical Creature', 'Vote for the best magical creature.', '2024-12-12 10:00:00', '2024-12-19 10:00:00', 'rubeushagrid');

-- Create Candidates Table
CREATE TABLE IF NOT EXISTS Candidates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    birth_date DATE,
    occupation VARCHAR(100),
    program TEXT,
    election_id INT,
    FOREIGN KEY (election_id) REFERENCES Elections(id)
);

-- Insert Candidates data
INSERT INTO Candidates (name, birth_date, occupation, program, election_id) VALUES
('Harry Potter', '1980-07-31', 'Wizard', 'Defeater of Voldemort', 1),
('Hermione Granger', '1979-09-19', 'Witch', 'Master of All Subjects', 2),
('Ron Weasley', '1980-03-01', 'Wizard', 'Best Friend of Harry', 1),
('Draco Malfoy', '1980-06-05', 'Wizard', 'Member of Slytherin House', 1),
('Ginny Weasley', '1981-08-11', 'Witch', 'Quidditch Star', 3),
('Luna Lovegood', '1981-02-13', 'Witch', 'Inventor and Explorer', 4),
('Neville Longbottom', '1980-07-30', 'Wizard', 'Herbology Expert', 5),
('Albus Dumbledore', '1881-07-02', 'Wizard', 'Former Headmaster', 4),
('Severus Snape', '1960-01-09', 'Wizard', 'Potions Master', 5),
('Rubeus Hagrid', '1928-12-06', 'Half-Giant', 'Keeper of Keys and Grounds', 4);

-- Create Votes Table
CREATE TABLE IF NOT EXISTS Votes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    election_id INT,
    candidate_id INT,
    vote_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (username, election_id),  -- Ensures a user can only vote once per election
    FOREIGN KEY (username) REFERENCES Users(username),
    FOREIGN KEY (election_id) REFERENCES Elections(id),
    FOREIGN KEY (candidate_id) REFERENCES Candidates(id)
);

-- Insert Votes data
INSERT INTO Votes (username, election_id, candidate_id, vote_time) VALUES
('harrypotter', 1, 1, '2024-11-10 10:00:01'),
('hermionegranger', 2, 2, '2024-11-19 10:01:01'),
('ronweasley', 1, 1, '2024-11-10 10:02:01'),
('dracomalfoy', 1, 4, '2024-11-11 10:03:01'),
('ginnyweasley', 3, 5, '2024-11-26 10:04:01'),
('lunalovegood', 4, 6, '2024-12-04 10:05:01'),
('nevillelongbottom', 5, 7, '2024-12-11 10:06:01'),
('albusdumbledore', 4, 8, '2024-12-10 10:07:01'),
('severussnape', 5, 9, '2024-12-09 10:08:01'),
('rubeushagrid', 4, 10, '2024-12-05 10:09:01');
