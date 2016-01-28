-- Shows average pts and variance to implied average over 5 games
select
c.nba_id,
c.rotoguru_id,
c.playernm_full,
count(*) as games,
sum(c.fdp) as fdp,
sum(c.fdp)/count(*) as avg_fdp,
sum(c.meet)/count(*) as pct_val,
(sum(c.fdp) - sum(c.implied))/count(*) as plus_minus_pg
from (
select b.day, b.nba_id, map.rotoguru_id, b.playernm_full, b.fdp, rg.fdsal, imp.implied, case when b.fdp >= imp.implied then 1 else 0 end as meet from (
select
day,
nba_id,
bbmon_id,
playernm_full,
fdp,
@id_rank := IF(@cur_player = nba_id, @id_rank + 1, 1) as id_rank,
@cur_player := nba_id

from
(
select nba.day, 
nba.player_id as nba_id, 
map.bbmon_id as bbmon_id, 
nba.playernm_full, 
nba.fdp

from nba_gamelog nba 

left join player_map map on nba.player_id = map.nba_id 

left join (select distinct player_id from bbmon_proj where day = '2016-01-26') bbmon on bbmon.player_id = map.bbmon_id

order by 2,1 desc) a) b

left join player_map map on b.nba_id = map.nba_id

left join rotoguru_gamelog rg on b.day = rg.day and map.rotoguru_id = rg.player_id

left join (select sal, sum(fpts)/sum(ct) as implied from v_implied_points where site = 'fd' group by 1) imp on rg.fdsal = imp.sal

where b.id_rank <= 5  and rg.fdsal is not Null and rg.fdsal <> 0 order by 4, 1 desc) c group by 1,2,3 order by 5 desc;