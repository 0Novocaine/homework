SELECT DISTINCT
    s.name AS student,
    sub.name AS course
FROM students s
JOIN marks m ON m.student_id = s.id
JOIN subjects sub ON sub.id = m.subject_id
WHERE s.name = 'Демиденко Михайло Едуардович';