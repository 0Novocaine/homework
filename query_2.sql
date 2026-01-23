SELECT
	s.name as student_name,
	sub.name AS subject_name,
	ROUND(AVG(m.score), 1) AS avg_score
FROM students AS s
JOIN marks AS m ON s.id = m.student_id
JOIN subjects AS sub ON sub.id = m.subject_id
WHERE sub.name = "Computer Science"
GROUP by s.id
ORDER by avg_score DESC
Limit 1