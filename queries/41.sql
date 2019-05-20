SELECT match_id, killer_name as player_name, COUNT(*) as kill_count 
FROM match_frag
GROUP BY match_id, player_name
ORDER BY kill_count DESC;