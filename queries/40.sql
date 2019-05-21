SELECT killer_name as player_name, COUNT(*) as kill_count 
FROM match_frag
GROUP BY player_name
ORDER BY kill_count DESC, player_name ASC;