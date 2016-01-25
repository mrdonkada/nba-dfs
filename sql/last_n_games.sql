select player_id, playernm_full, sum(pts) as total_pts, count(*) as games, sum(pts)/count(*) as avgpts from (
select a.*, @id_rank := IF(@cur_player = player_id, @id_rank + 1, 1) as id_rank, @cur_player := player_id from (
select * from nba_gamelog order by player_id, day desc) a) b where id_rank <= 5 group by 1,2;