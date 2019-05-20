SELECT match_id, COUNT(*) as kill_suicide_count 
FROM match_frag
GROUP BY match_id
ORDER BY kill_suicide_count DESC;