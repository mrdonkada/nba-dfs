create or replace view v_implied_pts as 
select 'dk' as site,
season,
pos,
sal,
ct,
fpts,
fpts/ct as imp_pts
from (
        select
        case when day >= '2015-10-25' then '2016' else '2015' end as season,
        pos,delete from implied_points;
insert into implied_points (site, season, pos, sal, ct, fpts, imp_pts)
select 'dk' as site,
season,
pos,
sal,
ct,
fpts,
fpts/ct as imp_pts
from (
        select
        case when day >= '2015-10-25' then '2016' else '2015' end as season,
        pos,
        dksal as sal,
        count(id) as ct,
        sum(dkp) as fpts
        from rotoguru_gamelog where dksal > 0 group by season, pos, sal) t

union

select 'fd' as site,
season,
pos,
sal,
ct,
fpts,
fpts/ct as imp_pts
from (
        select
        case when day >= '2015-10-25' then '2016' else '2015' end as season,
        pos,
        dksal as sal,
        count(id) as ct,
        sum(fdp) as fpts
        from rotoguru_gamelog where fdsal > 0 group by season, pos, sal) a
        dksal as sal,
        count(id) as ct,
        sum(dkp) as fpts
        from rotoguru_gamelog where dksal > 0 group by season, pos, sal) t

union

select 'fd' as site,
season,
pos,
sal,
ct,
fpts,
fpts/ct as imp_pts
from (
        select
        case when day >= '2015-10-25' then '2016' else '2015' end as season,
        pos,
        dksal as sal,
        count(id) as ct,
        sum(fdp) as fpts
        from rotoguru_gamelog where fdsal > 0 group by season, pos, sal) a