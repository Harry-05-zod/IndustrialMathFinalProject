SELECT 
    COUNT(*) AS NumberOfOverlappingClassPairs
FROM 
    (
    SELECT 
        A.CRN AS CRN_1,
        B.CRN AS CRN_2
    FROM 
        ClassMeetings A
    JOIN 
        ClassMeetings B 
        ON A.Building_Room = B.Building_Room
        AND A.CRN < B.CRN
        AND A.BeginTime < B.EndTime
        AND A.EndTime > B.BeginTime
    ) AS Overlaps;
