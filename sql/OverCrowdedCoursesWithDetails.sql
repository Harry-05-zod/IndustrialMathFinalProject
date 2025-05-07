WITH OverCapacity AS (
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
        COUNT(*) > cr.RoomCapacity
)

SELECT 
    sr.CRN,
    sr.CourseTitle,
    sr.Subject,
    sr.CourseNumber,
    sr.Section,
    sr.Course_Campus,
    sr.College_of_the_Student,
    oc.Registered_Students,
    oc.RoomCapacity
FROM 
    OverCapacity oc
JOIN 
    StudentRegistrations sr ON sr.CRN = oc.CRN
JOIN 
    ClassMeetings cr ON sr.CRN = cr.CRN;
