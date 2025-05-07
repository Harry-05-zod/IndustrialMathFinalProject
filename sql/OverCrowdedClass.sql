SELECT 
    sr.CRN,
    COUNT(*) AS Registered_Students,
    cr.RoomCapacity
FROM 
    StudentRegistrations sr
JOIN 
    ClassMeetings cr ON sr.CRN = cr.CRN
GROUP BY 
    sr.CRN, cr.RoomCapacity
HAVING 
    COUNT(*) > cr.RoomCapacity;
