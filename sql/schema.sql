-- ============================================
-- Chronic Disease Data Warehouse Schema
-- ============================================

-- 1. Diseases Master Table
CREATE TABLE diseases (
    disease_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50)
);

-- 2. Patients Table
CREATE TABLE patients (
    patient_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT CHECK (age >= 0),
    gender VARCHAR(10) CHECK (gender IN ('Male', 'Female', 'Other')),
    disease_id INT REFERENCES diseases(disease_id)
);

-- 3. Visits Table
CREATE TABLE visits (
    visit_id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id),
    visit_date DATE NOT NULL,
    hospital VARCHAR(100),
    outcome VARCHAR(50) CHECK (outcome IN ('Recovered', 'Ongoing', 'Readmitted', 'Deceased'))
);

-- 4. Medications Table
CREATE TABLE medications (
    medication_id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id),
    med_name VARCHAR(100) NOT NULL,
    adherence DECIMAL(5,2) CHECK (adherence >= 0 AND adherence <= 100),
    start_date DATE,
    end_date DATE
);

-- ============================================
-- Indexes for Performance
-- ============================================
CREATE INDEX idx_patients_disease ON patients(disease_id);
CREATE INDEX idx_visits_patient ON visits(patient_id);
CREATE INDEX idx_medications_patient ON medications(patient_id);

-- ============================================
-- Sample Data (Optional for Testing)
-- ============================================
INSERT INTO diseases (name, type) VALUES
('Diabetes', 'Chronic'),
('Hypertension', 'Chronic'),
('Asthma', 'Respiratory'),
('Heart Disease', 'Cardiovascular');

INSERT INTO patients (name, age, gender, disease_id) VALUES
('Amit Sharma', 45, 'Male', 1),
('Neha Singh', 50, 'Female', 2),
('Raj Verma', 32, 'Male', 3),
('Priya Patel', 60, 'Female', 4);

INSERT INTO visits (patient_id, visit_date, hospital, outcome) VALUES
(1, '2025-01-12', 'AIIMS Delhi', 'Ongoing'),
(2, '2025-02-05', 'Fortis Hospital', 'Recovered'),
(3, '2025-02-10', 'Apollo Bhopal', 'Readmitted'),
(4, '2025-03-15', 'AIIMS Bhopal', 'Deceased');

INSERT INTO medications (patient_id, med_name, adherence, start_date, end_date) VALUES
(1, 'Metformin', 90.0, '2025-01-12', '2025-06-12'),
(2, 'Amlodipine', 85.0, '2025-02-05', '2025-07-05'),
(3, 'Inhaler', 70.0, '2025-02-10', '2025-08-10'),
(4, 'Aspirin', 60.0, '2025-03-15', '2025-09-15');
