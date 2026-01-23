SELECT
    g.name AS group_name,
    ROUND(AVG(m.score), 2) AS avg_score
FROM marks m
JOIN students s ON s.id = m.student_id
JOIN groups g ON g.id = s.group_id
JOIN subjects sub ON sub.id = m.subject_id
WHERE sub.name = "Biology"
GROUP BY g.id, g.name
ORDER BY avg_score DESC;