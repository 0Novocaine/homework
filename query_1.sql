SELECT s.name, ROUND(AVG(m.score), 1) AS avg_score
FROM students AS s
LEFT JOIN marks AS m ON s.id = m.student_id
GROUP BY s.name
ORDER by avg_score
LIMIT 5
