SELECT
    *
FROM
    (SELECT  match_id, killer_name, victim_name, count(victim_name)
    FROM match_frag
    WHERE weapon_code is NOT NULL
    GROUP BY match_id, killer_name, victim_name
    ORDER BY killer_name ASC, count(victim_name) DESC) as W
;