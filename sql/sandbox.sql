UPDATE Table2
SET ref_id2 = table1.ref_id1
FROM table1
WHERE table1.id = table2.id
AND table1.a_ref1 = table2.b_ref1;
