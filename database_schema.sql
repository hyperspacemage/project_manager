-- Create database
CREATE DATABASE IF NOT EXISTS co_project_db;
USE co_project_db;

-- 1. user Table (Authentication & Security)
CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL, -- Stored as a secure hash
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. role Table (Dynamic Roles for flexibility)
CREATE TABLE role (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE, -- 'Owner', 'Editor', 'Viewer'
    description TEXT
);

-- 3. project Table
CREATE TABLE project (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. project_member Table (Relates Users, Projects, and Roles)
CREATE TABLE project_member (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    project_id INT NOT NULL,
    role_id INT NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES project(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES role(id) ON DELETE RESTRICT,
    UNIQUE(user_id, project_id) -- A user can only have one role per project
);

-- 5. priority Table (Normalization)
CREATE TABLE priority (
    id INT AUTO_INCREMENT PRIMARY KEY,
    level VARCHAR(20) NOT NULL UNIQUE -- 'Urgent', 'High', 'Normal', 'Low'
);

-- 6. task Table (Core CRUD Entity)
CREATE TABLE task (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    priority_id INT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'To Do',
    due_date DATETIME NULL,
    created_by INT NOT NULL,
    assigned_to INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES project(id) ON DELETE CASCADE,
    FOREIGN KEY (priority_id) REFERENCES priority(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES user(id) ON DELETE SET NULL
);

-- 7. comment Table
CREATE TABLE comment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT NOT NULL,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES task(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

-- 8. attachment Table
CREATE TABLE attachment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT NOT NULL,
    user_id INT NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES task(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

-- 9. invitation Table (For sharing links to users or non-users)
CREATE TABLE invitation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    inviter_id INT NOT NULL,
    token VARCHAR(100) NOT NULL UNIQUE, -- Secure URL token
    expires_at DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES project(id) ON DELETE CASCADE,
    FOREIGN KEY (inviter_id) REFERENCES user(id) ON DELETE CASCADE
);

-- Inject Default Roles
INSERT INTO role (name, description) VALUES 
('Owner', 'Full access and control over the project.'),
('Editor', 'Can view, create, and edit tasks.'),
('Viewer', 'Read-only access to the project and tasks.');

-- Inject Default Priorities
INSERT INTO priority (level) VALUES 
('Low'), ('Medium'), ('High'), ('Urgent');