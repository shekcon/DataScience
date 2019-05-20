SELECT COUNT(*) as kill_count FROM match_frag as MF
WHERE MF.victim_name is NOT NULL;