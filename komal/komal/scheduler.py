import sqlite3
from collections import defaultdict

def get_graph_data(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM Exams")
    all_exams = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT exam_id, COUNT(student_id) FROM Enrollments GROUP BY exam_id")
    enrollment_counts = {row[0]: row[1] for row in cursor.fetchall()}
    
    cursor.execute("SELECT student_id, exam_id FROM Enrollments")
    student_exams = defaultdict(list)
    for sid, eid in cursor.fetchall():
        student_exams[sid].append(eid)
        
    cursor.execute("SELECT id, capacity FROM Rooms ORDER BY capacity DESC")
    rooms = [{"id": row[0], "capacity": row[1]} for row in cursor.fetchall()]
    
    conn.close()
    
    # Build Conflict Graph
    graph = {exam: set() for exam in all_exams}
    for exams in student_exams.values():
        for i in range(len(exams)):
            for j in range(i + 1, len(exams)):
                graph[exams[i]].add(exams[j])
                graph[exams[j]].add(exams[i])
                
    return graph, enrollment_counts, rooms, all_exams

def run_allocation(db_name="exam_system.db"):
    graph, enrollment_counts, rooms, all_exams = get_graph_data(db_name)
    
    steps = []
    
    # 1. GRAPH COLORING (Greedy Welsh-Powell)
    # Sort exams by highest degree (most conflicts) first
    sorted_exams = sorted(all_exams, key=lambda e: len(graph[e]), reverse=True)
    
    steps.append({"type": "info", "msg": f"Exams sorted by conflict degree: {sorted_exams}"})
    
    time_slots = {} # exam_id -> slot_number
    
    for exam in sorted_exams:
        neighbor_colors = {time_slots[neighbor] for neighbor in graph[exam] if neighbor in time_slots}
        
        # Find first available color (slot)
        slot = 1
        while slot in neighbor_colors:
            slot += 1
            
        time_slots[exam] = slot
        steps.append({
            "type": "coloring",
            "exam": exam,
            "conflicts": list(graph[exam]),
            "unavailable_slots": list(neighbor_colors),
            "assigned_slot": slot
        })
        
    # 2. ROOM ALLOCATION (Greedy by capacity)
    # Group exams by time slot
    slots_to_exams = defaultdict(list)
    for exam, slot in time_slots.items():
        slots_to_exams[slot].append(exam)
        
    final_schedule = []
    for slot, exams_in_slot in slots_to_exams.items():
        # Sort exams in this slot by enrollment size descending
        exams_in_slot = sorted(exams_in_slot, key=lambda e: enrollment_counts.get(e, 0), reverse=True)
        
        available_rooms = rooms.copy()
        for exam in exams_in_slot:
            students = enrollment_counts.get(exam, 0)
            assigned_room = None
            
            for room in available_rooms:
                if room['capacity'] >= students:
                    assigned_room = room['id']
                    available_rooms.remove(room)
                    break
                    
            if assigned_room:
                final_schedule.append({
                    "slot": f"Time Slot {slot}",
                    "exam": exam,
                    "students": students,
                    "room": assigned_room
                })
                steps.append({"type": "room", "msg": f"Exam {exam} ({students} students) in Slot {slot} assigned to {assigned_room}."})
            else:
                steps.append({"type": "error", "msg": f"Failed to find a room for Exam {exam} ({students} students) in Slot {slot}."})

    # Sort final schedule by slot
    final_schedule = sorted(final_schedule, key=lambda x: x["slot"])
    return steps, final_schedule