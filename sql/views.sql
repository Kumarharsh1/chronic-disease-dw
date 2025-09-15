-- ============================================
-- Chronic Disease Data Warehouse KPI Views (SQLite version)
-- ============================================

-- 1. Disease Prevalence (how many patients per disease)
DROP VIEW IF EXISTS disease_prevalence;
CREATE VIEW disease_prevalence AS
SELECT 
    d.name AS disease,
    COUNT(p.patient_id) AS total_patients
FROM diseases d
LEFT JOIN patients p ON d.name = p.disease
GROUP BY d.name;

-- 2. Readmission Rate (patients with 'Readmitted' visits)
DROP VIEW IF EXISTS readmission_rate;
CREATE VIEW readmission_rate AS
SELECT 
    d.name AS disease,
    COUNT(DISTINCT v.patient_id) AS readmitted_patients,
    COUNT(DISTINCT p.patient_id) AS total_patients,
    ROUND(
        (CAST(COUNT(DISTINCT v.patient_id) AS REAL) / NULLIF(COUNT(DISTINCT p.patient_id), 0)) * 100,
        2
    ) AS readmission_rate_percent
FROM diseases d
LEFT JOIN patients p ON d.name = p.disease
LEFT JOIN visits v ON p.patient_id = v.patient_id AND v.outcome = 'Readmitted'
GROUP BY d.name;

-- 3. Medication Adherence (average adherence per disease)
DROP VIEW IF EXISTS medication_adherence;
CREATE VIEW medication_adherence AS
SELECT 
    d.name AS disease,
    ROUND(AVG(m.adherence), 2) AS avg_adherence_percent
FROM diseases d
LEFT JOIN patients p ON d.name = p.disease
LEFT JOIN medications m ON p.patient_id = m.patient_id
GROUP BY d.name;

-- 4. Patient Outcomes Summary (Recovered, Ongoing, Deceased, etc.)
DROP VIEW IF EXISTS patient_outcomes_summary;
CREATE VIEW patient_outcomes_summary AS
SELECT 
    v.outcome,
    COUNT(DISTINCT v.patient_id) AS total_patients
FROM visits v
GROUP BY v.outcome;
