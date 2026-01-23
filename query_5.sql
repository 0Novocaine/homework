SELECT t.name AS teacher_name, sub.name AS subject_name
FROM teachers AS t
LEFT JOIN subjects AS sub on t.id = sub.teacher_id
WHERE t.name = "викладач Марта Якимчук"