SELECT 
  A.CRN AS CRN_1,
  A.Subject AS Subject_1,
  A.CourseNumber AS Course_1,
  A.Building_Room,
  A.BeginTime AS Start_1,
  A.EndTime AS End_1,
  
  B.CRN AS CRN_2,
  B.Subject AS Subject_2,
  B.CourseNumber AS Course_2,
  B.BeginTime AS Start_2,
  B.EndTime AS End_2

FROM ClassMeetings A
JOIN ClassMeetings B 
  ON A.Building_Room = B.Building_Room
  AND A.CRN < B.CRN
  AND A.BeginTime < B.EndTime
  AND A.EndTime > B.BeginTime;
