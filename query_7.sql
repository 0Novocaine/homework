SELECT 	s.name AS student,
		g.name AS group_name,
		m.score AS score,
		sub.name AS subject
FROM marks AS m
JOIN students AS s ON m.student_id  = s.id
JOIN subjects AS sub on m.subject_id = sub.id
JOIN groups AS g ON g.id = s.group_id

WHERE 	g.name = "Group A"
	AND sub.name = "Geography"