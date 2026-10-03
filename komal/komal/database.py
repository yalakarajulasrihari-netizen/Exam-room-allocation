import sqlite3

DB_NAME = "exam_system.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create tables
    cursor.executescript("""
        DROP TABLE IF EXISTS Exams;
        DROP TABLE IF EXISTS Rooms;
        DROP TABLE IF EXISTS Enrollments;
        
        CREATE TABLE Exams (id TEXT PRIMARY KEY, name TEXT);
        CREATE TABLE Rooms (id TEXT PRIMARY KEY, capacity INTEGER);
        CREATE TABLE Enrollments (student_id TEXT, exam_id TEXT);
    """)

    # Seed Exams
    exams = [('CS101', 'Intro to CS'), ('MTH201', 'Calculus II'), 
             ('PHY101', 'Physics I'), ('ENG101', 'English Lit'), 
             ('HIS101', 'World History')]
    cursor.executemany("INSERT INTO Exams VALUES (?, ?)", exams)

    # Seed Rooms
    rooms = [('Room A', 30), ('Room B', 50), ('Room C', 20)]
    cursor.executemany("INSERT INTO Rooms VALUES (?, ?)", rooms)

    # Seed Enrollments (Creating intentional conflicts)
    # Student 1 takes CS101, MTH201 (Conflict between CS101 and MTH201)
    # Student 2 takes CS101, PHY101 (Conflict between CS101 and PHY101)
    # Student 3 takes MTH201, PHY101 (Conflict between MTH201 and PHY101)
    enrollments = [
        ('S1', 'CS101'), ('S1', 'MTH201'),
        ('S2', 'CS101'), ('S2', 'PHY101'),
        ('S3', 'MTH201'), ('S3', 'PHY101'),
        ('S4', 'ENG101'), ('S4', 'HIS101'),
        ('S5', 'CS101'), ('S5', 'ENG101')
    ]
    cursor.executemany("INSERT INTO Enrollments VALUES (?, ?)", enrollments)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized and seeded.")