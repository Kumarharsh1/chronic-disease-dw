CREATE TABLE Patients (
    patient_id INT PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    gender VARCHAR(10),
    disease VARCHAR(50)
);

CREATE TABLE Visits (
    visit_id INT PRIMARY KEY,
    patient_id INT,
    visit_date DATE,
    diagnosis VARCHAR(100),
    treatment VARCHAR(100),
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id)
);
