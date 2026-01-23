SELECT s.name, sub.name, m.score, MAX(m.date)
FROM marks AS m
JOIN students AS s ON s.id = m.student_id 
JOIN subjects AS sub ON sub.id = m.subject_id 
JOIN groups AS g ON g.id = s.group_id 
WHERE g.name = 'Group A' AND sub.name = 'Biology'
GROUP by s.name
