SELECT DISTINCT
	sub.name AS course,
    s.name AS student,
    t.name AS teacher
FROM subjects AS sub
JOIN teachers AS t ON t.id = sub.teacher_id
JOIN marks AS m ON m.subject_id = sub.id
JOIN students AS s ON m.student_id = s.id
WHERE 	s.name = 'Демиденко Михайло Едуардович'
	AND t.name = 'викладач Карпа Орися Германівна'

