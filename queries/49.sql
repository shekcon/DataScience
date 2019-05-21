SELECT
    W.match_id as match_id,
    W.killer_name as killer_name, 
    count(W.weapon_count) as weapon_count
FROM
    (SELECT  match_id,killer_name, weapon_code as weapon_count
    FROM match_frag
    WHERE weapon_code is NOT NULL
    GROUP BY match_id, killer_name, weapon_code
    ORDER BY killer_name ASC) as W
GROUP BY killer_name, match_id
ORDER BY count(W.weapon_count) DESC;