SELECT 
    F.match_id, 
    F.victim_name as player_name,
    F.killer_name as wrost_enemy_name,
    F.kill_count
FROM
    (
    SELECT 
        match_id,
        killer_name,
        victim_name,
        row_number() OVER 
            (PARTITION by victim_name 
            ORDER BY count(killer_name) DESC) ,
        count(victim_name) as kill_count
    FROM match_frag
    WHERE weapon_code is NOT NULL
    GROUP BY match_id, killer_name, victim_name
    ) F
WHERE row_number = 1
ORDER BY match_id
;