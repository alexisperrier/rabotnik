select ch.channel_id, p.status
 from channel ch
     join pipeline p on p.channel_id = ch.channel_id
     left join border b on b.channel_id = ch.channel_id
     left join flow as fl on fl.channel_id = ch.channel_id
 where p.channel_id is not null
     and not p.channel_complete
     and p.status in ('active','energised','frenetic','sluggish','steady','asleep','cold','dormant','blank')
     and b.id is null
     and fl.id is null
 order by ch.id asc;
