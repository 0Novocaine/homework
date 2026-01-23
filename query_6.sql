SELECT s.name AS student, g.name AS class
FROM students AS s
JOIN groups AS g ON g.id = s.group_id
WHERE g.name = "Group A"