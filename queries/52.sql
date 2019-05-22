DROP FUNCTION get_killer_class;
CREATE FUNCTION get_killer_class(weapon text)
RETURNS text AS $$
BEGIN
    RETURN
    CASE
        WHEN weapon IN ('Machete', 'Falcon', 'MP5') THEN 'Hitman'
        WHEN weapon IN ('SniperRifle') THEN 'Sniper'
        WHEN weapon IN ('AG36', 'OICW', 'P90', 'M4', 'Shotgun', 'M249') THEN 'Commando'
        WHEN weapon IN ('Rocket', 'VehicleRocket', 'HandGrenade', 'StickExplosive', 'Boat', 'Vehicle', 'VehicleMountedRocketMG', 'VehicleMountedAutoMG', 'MG', 'VehicleMountedMG', 'OICWGrenade', 'AG36Grenade') THEN 'Psychopath'
    END;
END; $$ 
LANGUAGE PLPGSQL;

SELECT 
    C.match_id, 
    C.killer_name as player_name,
    C.weapon_code,
    C.kill_count,
    get_killer_class(C.weapon_code) as killer_class
FROM
    (SELECT 
        match_id, 
        killer_name,
        weapon_code,
        count(weapon_code) as kill_count,
        row_number() OVER (PARTITION by killer_name ORDER BY count(weapon_code) DESC)
    FROM match_frag
    WHERE weapon_code is NOT NULL
    GROUP BY match_id, killer_name, weapon_code) C
WHERE row_number = 1
;
