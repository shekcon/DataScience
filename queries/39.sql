SELECT match_id, COUNT(*) as suicide_count
FROM match_frag
WHERE victim_name is NULL
GROUP BY match_id
ORDER BY suicide_count ASC;