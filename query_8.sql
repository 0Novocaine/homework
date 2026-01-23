SELECT
    t.name AS teacher,
    sub.name AS subject,
    ROUND(AVG(m.score), 1)
FROM teachers t
JOIN subjects sub ON sub.teacher_id = t.id
JOIN marks m ON m.subject_id = sub.id
WHERE t.name = 'викладач Марта Якимчук'
GROUP BY t.id, sub.id;