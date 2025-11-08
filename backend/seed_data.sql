-- Seed data for LabLink System
-- This script inserts initial users, components, and sample requests

-- Insert users (passwords are hashed with bcrypt)
-- Default password for all users: 'faculty123' for faculty, 'student123' for students
INSERT INTO users (username, email, password_hash, role) VALUES
('faculty', 'faculty@lablink.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYILSm6K7gO', 'faculty'),
('student', 'student@lablink.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYILSm6K7gO', 'student'),
('john_doe', 'john.doe@lablink.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYILSm6K7gO', 'student'),
('jane_smith', 'jane.smith@lablink.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYILSm6K7gO', 'student'),
('prof_wilson', 'wilson@lablink.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYILSm6K7gO', 'faculty');

-- Insert components
INSERT INTO components (name, type, quantity, description, location) VALUES
-- Arduino Boards
('Arduino Uno R3', 'Microcontroller', 15, 'ATmega328P based microcontroller board with 14 digital I/O pins', 'Rack A, Shelf 1'),
('Arduino Mega 2560', 'Microcontroller', 8, 'ATmega2560 based board with 54 digital I/O pins and 16 analog inputs', 'Rack A, Shelf 1'),
('Arduino Nano', 'Microcontroller', 20, 'Compact ATmega328P board, breadboard-friendly', 'Rack A, Shelf 2'),

-- Sensors
('DHT22 Temperature & Humidity Sensor', 'Sensor', 25, 'Digital temperature and humidity sensor with high accuracy', 'Rack B, Shelf 1'),
('HC-SR04 Ultrasonic Sensor', 'Sensor', 30, 'Ultrasonic distance sensor, range 2cm to 400cm', 'Rack B, Shelf 1'),
('PIR Motion Sensor', 'Sensor', 18, 'Passive infrared motion detection sensor', 'Rack B, Shelf 2'),
('MQ-2 Gas Sensor', 'Sensor', 12, 'Detects LPG, propane, methane, hydrogen, alcohol, smoke', 'Rack B, Shelf 2'),
('BMP280 Pressure Sensor', 'Sensor', 10, 'Barometric pressure and temperature sensor', 'Rack B, Shelf 3'),

-- Modules
('ESP8266 WiFi Module', 'Module', 22, 'WiFi module for IoT projects with TCP/IP stack', 'Rack C, Shelf 1'),
('HC-05 Bluetooth Module', 'Module', 16, 'Bluetooth serial communication module', 'Rack C, Shelf 1'),
('L298N Motor Driver', 'Module', 14, 'Dual H-bridge motor driver for DC motors', 'Rack C, Shelf 2'),
('16x2 LCD Display', 'Display', 12, '16 character x 2 line LCD display with I2C interface', 'Rack C, Shelf 3'),

-- Cables and Accessories
('Jumper Wires (Male-Male)', 'Cable', 50, 'Pack of 40 jumper wires, 20cm length', 'Rack D, Shelf 1'),
('Jumper Wires (Male-Female)', 'Cable', 45, 'Pack of 40 jumper wires, 20cm length', 'Rack D, Shelf 1'),
('Breadboard 830 Points', 'Accessory', 28, 'Solderless breadboard with 830 tie points', 'Rack D, Shelf 2'),
('USB Cable Type A to B', 'Cable', 20, 'USB cable for Arduino Uno/Mega programming', 'Rack D, Shelf 3');

-- Insert sample requests
-- Pending requests
INSERT INTO requests (student_id, component_id, quantity, status, requested_at) VALUES
(2, 1, 2, 'Pending', NOW() - INTERVAL '1 day'),
(3, 5, 3, 'Pending', NOW() - INTERVAL '2 days');

-- Approved requests
INSERT INTO requests (student_id, component_id, quantity, status, requested_at, processed_at, processed_by) VALUES
(2, 9, 1, 'Approved', NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days' + INTERVAL '2 hours', 1),
(3, 13, 2, 'Approved', NOW() - INTERVAL '4 days', NOW() - INTERVAL '4 days' + INTERVAL '2 hours', 1);

-- Rejected request
INSERT INTO requests (student_id, component_id, quantity, status, rejection_reason, requested_at, processed_at, processed_by) VALUES
(2, 2, 5, 'Rejected', 'Requested quantity exceeds project requirements', NOW() - INTERVAL '7 days', NOW() - INTERVAL '7 days' + INTERVAL '2 hours', 1);

-- Returned request
INSERT INTO requests (student_id, component_id, quantity, status, requested_at, processed_at, processed_by, returned_at) VALUES
(3, 3, 1, 'Returned', NOW() - INTERVAL '10 days', NOW() - INTERVAL '10 days' + INTERVAL '2 hours', 1, NOW() - INTERVAL '7 days');

-- Note: Default passwords (bcrypt hashed):
-- faculty123: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYILSm6K7gO
-- student123: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYILSm6K7gO
