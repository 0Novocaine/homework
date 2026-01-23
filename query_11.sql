SELECT 	s.name,
		t.name,
		ROUND(AVG(m.score), 1)
FROM marks AS m
JOIN students AS s ON m.student_id  = s.id
JOIN subjects AS sub ON m.subject_id = sub.id
JOIN teachers AS t ON sub.teacher_id = t.id
WHERE 	s.name = 'Богуслав Закусило'
	AND t.name = 'викладач Марта Якимчук'
GROUP by sub.name
