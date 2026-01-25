SELECT
    s.name,
    sub.name,
    m.score,
    m.date
FROM marks AS m
JOIN students AS s ON s.id = m.student_id
JOIN subjects AS sub ON sub.id = m.subject_id
JOIN groups AS g ON g.id = s.group_id
WHERE g.name = 'Group A'
  AND sub.name = 'Biology'
  AND m.date = (
        SELECT MAX(m2.date)
        FROM marks AS m2
        JOIN subjects AS sub2 ON sub2.id = m2.subject_id
        WHERE sub2.name = 'Biology'
  );