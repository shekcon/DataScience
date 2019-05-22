SELECT  match_id, killer_name, count(DISTINCT weapon_code) as weapon_count
FROM match_frag
WHERE weapon_code is NOT NULL
GROUP BY match_id, killer_name
ORDER BY weapon_count DESC;