import os
import traceback
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, session, url_for
import re
from datetime import datetime
import secrets

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key = secrets.token_hex(16)

DATABASEURI = "postgresql://yz4795:970942@104.196.222.236/proj1part2"
engine = create_engine(DATABASEURI)
conn = engine.connect()

def get_affiliates():
  try:
    query = text("""
                 SELECT sid, did FROM affiliate
                 WHERE year = :year AND term = :term
                 ORDER BY did ASC, sid ASC
                 """)
    cursor = g.conn.execute(query)
    affiliate = {}
    results = cursor.mappings().all()
    for result in results:
      sid = result["sid"]
      did = result["did"]
      if sid not in affiliate:
        affiliate[sid] = {
          'did': did
        } 
    cursor.close()
    return affiliate  
  except Exception as e:
    print(f"Error from database (affiliates): {str(e)}") 
    return {}
  
def get_students():
  try:
    query = text("""
                SELECT sid, sname, semail, major, academic_level, gpa, enrolled_credits, min_allowed_enrollment, max_allowed_enrollment FROM Students
                ORDER BY sid ASC, academic_level ASC
                """)
    cursor = g.conn.execute(query)
    students = {}
    results = cursor.mappings().all()
    for result in results:
      sid = result["sid"]
      sname = result["sname"]
      semail = result["semail"]
      major = result["major"]
      academic_level = result["academic_level"]
      gpa = result["gpa"]
      enrolled_credits = result["enrolled_credits"]
      min_allowed_enrollment = result["min_allowed_enrollment"]
      max_allowed_enrollment = result["max_allowed_enrollment"]
      if sid not in students:
        students[sid] = {
          'sname': sname,
          'semail': semail,
          'major': major,
          'academic_level': academic_level,
          'gpa': gpa,
          'enrolled_credits': enrolled_credits,
          'min_allowed_enrollment': min_allowed_enrollment,
          'max_allowed_enrollment': max_allowed_enrollment,
        } 
    cursor.close()
    return students  
  except Exception as e:
    print(f"Error from database (students): {str(e)}") 
    return {}

def get_instructors_works_in():
  try:
    query = text("""
                SELECT id, name, email, did, address, since FROM instructors_works_in
                ORDER BY id ASC, did ASC 
                """)
    cursor = g.conn.execute(query)
    instructors_works_in = {}
    results = cursor.mappings().all()
    for result in results:
      id = result["id"]
      name = result["name"]
      email = result["email"]
      did = result["did"]
      address = result["address"]
      since = result["since"]
      if id not in instructors_works_in:
        instructors_works_in[id] = {
          'name': name,
          'email': email,
          'did': did,
          'address': address,
          'since': since
        } 
    cursor.close()
    return instructors_works_in  
  except Exception as e:
    print(f"Error from database (instructors_works_in): {str(e)}") 
    return {}

def get_departments_is_at():
  try:
    query_loc = text("""
                     SELECT did, address FROM is_at
                     ORDER BY did ASC
                     """)
    cursor = g.conn.execute(query_loc)
    departments_is_at = {}
    results_loc = cursor.mappings().all()
    for result in results_loc:
      did = result["did"]
      address = result["address"]
      if did not in departments_is_at:
        departments_is_at[did] = {
          'address': address
        }
    cursor.close()
    return departments_is_at  
  except Exception as e:
    print(f"Error from database (is_at): {str(e)}") 
    return {}
  
def get_departments():
  try:
    query = text("""
                 SELECT did, dname FROM departments
                 ORDER BY did ASC, dname ASC
                 """)
    cursor = g.conn.execute(query)
    departments = {}
    results = cursor.mappings().all()
    for result in results:
      did = result["did"]
      dname = result["dname"]
      if did not in departments:
        departments[did] = {
          'dname': dname
        } 
    cursor.close()
    return departments  
  except Exception as e:
    print(f"Error from database (departments): {str(e)}") 
    return {}

def get_classrooms():
  try:
    query_loc = text("""
                     SELECT address, bname FROM locations
                     ORDER BY bname ASC, address ASC
                     """)
    cursor = g.conn.execute(query_loc)
    buildings = {}
    results_loc = cursor.mappings().all()
    for result in results_loc:
      address = result["address"]
      bname = result["bname"]
      if address not in buildings:
        buildings[address] = {
          'bname': bname,
          'classrooms': {}
        }
    cursor.close()
    
    query_classroom = text("SELECT room_num, capacity, address FROM classrooms_locates_at")
    cursor = g.conn.execute(query_classroom)
    results_classroom = cursor.mappings().all()
    for result in results_classroom:
      address = result["address"]
      room_num = result["room_num"]
      capacity = result["capacity"]
      if address in buildings:
        buildings[address]['classrooms'][room_num] = {
          'capacity': capacity
        }
    cursor.close()
    return buildings  
  except Exception as e:
    print(f"Error from database (buildings&classrooms): {str(e)}") 
    return {}

def get_year_terms():
  try:
    query = text("SELECT year, term FROM Calendar ORDER BY year DESC, term DESC")
    cursor = g.conn.execute(query)
    
    year_terms = {}
    results = cursor.mappings().all()
    for result in results:
      year = result["year"]
      term = result["term"]
      if year not in year_terms:
        year_terms[year] = []
      year_terms[year].append(term) 
    cursor.close()
    return year_terms
  except Exception as e:
    print(f"Error from database (year_terms): {str(e)}") 
    return []
   

def get_calendar(year, term):
  params_dict = {
    'year': year,
    'term': term
  }
  try:
    query = text("""
                 SELECT add_waitlist_ddl, drop_ddl FROM Calendar
                 WHERE year = :year AND term = :term
                 """)
    cursor = g.conn.execute(query, params_dict)
    results = cursor.mappings().all()
    ddls = []
    for result in results:
      add_wl_ddl = result["add_waitlist_ddl"]
      drop_ddl = result["drop_ddl"]
      ddls.append({
        'add_waitlist_ddl': add_wl_ddl,
        'drop_ddl': drop_ddl
      })
    cursor.close()
    return ddls  
  except Exception as e:
    print(f"Error from database (calendar): {str(e)}") 
    return []
  
def get_holidays(year, term):
  params_dict = {
    'year': year,
    'term': term
  }
  try:
    query = text("""
                 SELECT hname, from_date, to_date FROM Holiday_falls_in
                 WHERE year = :year AND term = :term
                 ORDER BY from_date ASC, to_date ASC
                 """)
    cursor = g.conn.execute(query, params_dict)
    
    holidays = {}
    results = cursor.mappings().all()
    for result in results:
      hname = result["hname"]
      from_date = result["from_date"]
      to_date = result["to_date"]
      if hname not in holidays:
        holidays[hname] = {
          'from_date': from_date,
          'end_date': to_date
        }
    cursor.close()
    return holidays  
  except Exception as e:
    print(f"Error from database (holidays): {str(e)}") 
    return {}

def get_timeslot_allocates(year, term):
  params_dict = {
    'year': year,
    'term': term
  }
  try:
    query = text("""
                 SELECT tid, days_in_a_week, start_time, end_time FROM Timeslot_allocates
                 WHERE year = :year AND term = :term
                 ORDER BY days_in_a_week ASC, tid ASC, start_time ASC, end_time ASC
                 """)
    cursor = g.conn.execute(query, params_dict)
    timeslot_allocates = {}
    results = cursor.mappings().all()
    for result in results:
      tid = result["tid"]
      days_in_a_week = result["days_in_a_week"]
      start_time = result["start_time"]
      end_time = result["end_time"]
      if (tid, days_in_a_week) not in timeslot_allocates:
        timeslot_allocates[(tid, days_in_a_week)] = {
          'start_time': start_time,
          'end_time': end_time
        } 
    cursor.close()
    return timeslot_allocates  
  except Exception as e:
    print(f"Error from database (timeslot_allocates): {str(e)}") 
    return {}

def get_courses(year, term):
  params_dict = {
    'year': year,
    'term': term
  }
  
  try:
    query = text("""
                SELECT cid, cname, credits, major, academic_level FROM Courses
                WHERE year = :year AND term = :term
                ORDER BY cid ASC, cname ASC
                """)
    cursor = g.conn.execute(query, params_dict)
    courses = {}
    results = cursor.mappings().all()
    for result in results:
      cid = result["cid"]
      cname = result["cname"]
      credits = result["credits"]
      major = result["major"]
      academic_level = result["academic_level"]
      if cid not in courses:
        courses[cid] = {
          'cname': cname,
          'credits': credits,
          'major': major,
          'academic_level': academic_level
        } 
    cursor.close()

    query = text("""
                 SELECT cid_course, cid_prerequisite FROM Prerequisites
                 WHERE year = :year AND term = :term
                 """)
    cursor = g.conn.execute(query, params_dict)
    results = cursor.mappings().all()
    for result in results:
      cid_course = result["cid_course"]
      cid_prerequisite = result["cid_prerequisite"]
      if cid_course in courses:
        courses[cid_course]['prerequisites'] = cid_prerequisite
    cursor.close()

    query = text("""
                 SELECT cid, did FROM offers
                 WHERE year = :year AND term = :term
                 """)
    cursor = g.conn.execute(query, params_dict)
    results = cursor.mappings().all()
    for result in results:
      cid = result["cid"]
      did = result["did"]
      if cid in courses:
        courses[cid]['did'] = did
    cursor.close()
    return courses  
  except Exception as e:
    print(f"Error from database (courses&prerequisites&offers): {str(e)}") 
    return {}

def get_sec_schedules_time(year, term):
  params_dict = {
    'year': year,
    'term': term
  }
  try:
    query = text("""
                 SELECT sec_num, cid, tid, days_in_a_week FROM Sec_schedules_time
                 WHERE year = :year AND term = :term
                 ORDER BY cid ASC, sec_num ASC, days_in_a_week ASC, tid ASC
                 """)
    cursor = g.conn.execute(query, params_dict)
    sec_schedules_time = []
    results = cursor.mappings().all()
    for result in results:
      sec_num = result["sec_num"]
      tid = result["tid"]
      cid = result["cid"]
      days_in_a_week = result["days_in_a_week"]
      if (sec_num, cid, tid, days_in_a_week) not in sec_schedules_time:
        sec_schedules_time.append((sec_num, cid, tid, days_in_a_week))
    cursor.close()
    return sec_schedules_time  
  except Exception as e:
    print(f"Error from database (sec_schedules_time): {str(e)}") 
    return {}

def get_sec_assigns_at(year, term):
  params_dict = {
    'year': year,
    'term': term
  }
  try:
    query = text("""
                 SELECT sec_num, room_num, cid, address FROM Sec_assigns_at
                 WHERE year = :year AND term = :term
                 ORDER BY cid ASC, sec_num ASC
                 """)
    cursor = g.conn.execute(query, params_dict)
    sec_assigns_at = []
    results = cursor.mappings().all()
    for result in results:
      sec_num = result["sec_num"]
      room_num = result["room_num"]
      cid = result["cid"]
      address = result["address"]
      if (sec_num, room_num, cid, address) not in sec_assigns_at:
        sec_assigns_at.append((sec_num, room_num, cid, address))
    cursor.close()
    return sec_assigns_at  
  except Exception as e:
    print(f"Error from database (sec_assigns_at): {str(e)}") 
    return {}

def get_time_location_info(year, term):
  params_dict = {
    'year': year,
    'term': term
  }
    
  try:
    query = text("""
                 SELECT bname, address, room_num, capacity,
                  days_in_a_week, tid, start_time, end_time
                 FROM Time_Location_Info TLI
                 WHERE year = :year AND term = :term
                 ORDER BY bname ASC, days_in_a_week ASC, tid ASC;
                 """)

    cursor = g.conn.execute(query, params_dict)
    time_location_info = []
    results = cursor.mappings().all()
    for result in results:
      bname = result["bname"]
      address = result["address"]
      room_num = result["room_num"]
      capacity = result["capacity"]
      days_in_a_week = result["days_in_a_week"]
      tid = result["tid"]
      start_time = result["start_time"]
      end_time = result["end_time"]
      # print('.....................')
      # print(result)
      if (bname, address, room_num, capacity, days_in_a_week, tid, start_time, end_time) not in time_location_info:
        time_location_info.append([bname, address, room_num, capacity, days_in_a_week, tid, start_time, end_time])
    cursor.close()
    return time_location_info  
  except Exception as e:
    print(f"Error from database (time_location_info): {str(e)}") 
    return {}

def get_time_instructor_info(year, term):
  params_dict = {
    'year': year,
    'term': term
  }

  try:
    query = text("""
                 SELECT id, name, email,
                  days_in_a_week, tid, start_time, end_time
                 FROM Time_Instructor_Info TII
                 WHERE year = :year AND term = :term
                 ORDER BY id ASC, days_in_a_week ASC, tid ASC;
                 """)

    cursor = g.conn.execute(query, params_dict)
    time_instructor_info = []
    results = cursor.mappings().all()
    for result in results:
      id = result["id"]
      name = result["name"]
      email = result["email"]
      days_in_a_week = result["days_in_a_week"]
      tid = result["tid"]
      start_time = result["start_time"]
      end_time = result["end_time"]
      # print('.....................')
      # print(result)
      if (id, name, email, days_in_a_week, tid, start_time, end_time) not in time_instructor_info:
        time_instructor_info.append([id, name, email, days_in_a_week, tid, start_time, end_time])
    cursor.close()
    return time_instructor_info  
  except Exception as e:
    print(f"Error from database (time_instructor_info): {str(e)}") 
    return {}

def get_course_section_info(year, term):
  params_dict = {
    'year': year,
    'term': term
  }
  try:
    query = text("""
                 SELECT cid, cname, credits, major, academic_level, cid_prerequisite,
                 sec_num, instruction_mode, max_capacity, actual_enrollment, tid, days_in_a_week,
                 start_time, end_time, room_num, sec_address, capacity, bname, course_dept,
                 dname, course_dept_address, id, name, email, instru_dept, since
                 FROM Course_Section_Info CSI
                 WHERE year = :year AND term = :term
                 ORDER BY cid ASC, sec_num ASC, days_in_a_week ASC;
                 """)

    cursor = g.conn.execute(query, params_dict)
    course_section_info = {}
    results = cursor.mappings().all()
    for result in results:
      cid = result["cid"]
      cname = result["cname"]
      credits = result["credits"]
      major = result["major"]
      academic_level = result["academic_level"]
      cid_prerequisite = result["cid_prerequisite"]
      sec_num = result["sec_num"]
      instruction_mode = result["instruction_mode"]
      max_capacity = result["max_capacity"]
      actual_enrollment = result["actual_enrollment"]
      tid = result["tid"]
      days_in_a_week = result["days_in_a_week"]
      start_time = result["start_time"]
      end_time = result["end_time"]
      room_num = result["room_num"]
      sec_address = result["sec_address"]
      capacity = result["capacity"]
      bname = result["bname"]
      course_dept = result["course_dept"]
      dname = result["dname"]
      course_dept_address = result["course_dept_address"]
      id = result["id"]
      name = result["name"]
      email = result["email"]
      instru_dept = result["instru_dept"]
      since = result["since"]
      # print('.....................')
      # print(result)
      if cid not in course_section_info:
        course_section_info[cid] = {
            'cname': cname,
            'credits': credits,
            'major': major,
            'academic_level': academic_level,
            'cid_prerequisite': cid_prerequisite,
            'course_dept': course_dept,
            'dname': dname,
            'course_dept_address': course_dept_address,
          }
      if sec_num not in course_section_info[cid]:
          course_section_info[cid][sec_num] = {
            'instruction_mode': instruction_mode,
            'max_capacity': max_capacity,
            'actual_enrollment': actual_enrollment,
            'address': {'bname': bname,
                      'room_num': room_num,
                      'sec_address': sec_address,
                      'capacity': capacity},
            'instructor': {'id': id,
                           'name': name,
                           'email': email,
                           'instru_dept': instru_dept,
                           'since': since},
            'time': {}
          }

      if days_in_a_week not in course_section_info[cid][sec_num]['time']:
          course_section_info[cid][sec_num]['time'][days_in_a_week] = {
            'tid': tid,
            'start_time': start_time,
            'end_time': end_time
          }
    cursor.close()
    return course_section_info  
  except Exception as e:
    print(f"Error from database (course_section_info): {str(e)}") 
    return {}
  
def get_course_section_info_details(year, term):
  params_dict = {
    'year': year,
    'term': term
  }
  try:
    query = text("""
                 SELECT cid, cname, credits, major, academic_level, cid_prerequisite,
                 sec_num, instruction_mode, max_capacity, actual_enrollment, tid, days_in_a_week,
                 start_time, end_time, room_num, sec_address, capacity, bname, course_dept,
                 dname, course_dept_address, id, name, email, instru_dept, since
                 FROM Course_Section_Info CSI
                 WHERE year = :year AND term = :term
                 ORDER BY cid ASC, sec_num ASC, days_in_a_week ASC;
                 """)

    cursor = g.conn.execute(query, params_dict)
    course_section_info_details = {
      'cid': [],
      'cname': [],
      'major': [],
      'academic_level': [],
      'instruction_mode': [],
      'days_in_a_week': [],
      'course_dept': [],
      'dname': [],
      'id': [],
      'name': []
    }
    results = cursor.mappings().all()
    for result in results:
      cid = result["cid"]
      cname = result["cname"]
      credits = result["credits"]
      major = result["major"]
      academic_level = result["academic_level"]
      cid_prerequisite = result["cid_prerequisite"]
      sec_num = result["sec_num"]
      instruction_mode = result["instruction_mode"]
      max_capacity = result["max_capacity"]
      actual_enrollment = result["actual_enrollment"]
      tid = result["tid"]
      days_in_a_week = result["days_in_a_week"]
      start_time = result["start_time"]
      end_time = result["end_time"]
      room_num = result["room_num"]
      sec_address = result["sec_address"]
      capacity = result["capacity"]
      bname = result["bname"]
      course_dept = result["course_dept"]
      dname = result["dname"]
      course_dept_address = result["course_dept_address"]
      id = result["id"]
      name = result["name"]
      email = result["email"]
      instru_dept = result["instru_dept"]
      since = result["since"]
      # print('.....................')
      # print(result)
      if cid not in course_section_info_details['cid']:
        course_section_info_details['cid'].append(cid)
      
      if cname not in course_section_info_details['cname']:
        course_section_info_details['cname'].append(cname)

      if major not in course_section_info_details['major']:
        course_section_info_details['major'].append(major)
      
      if academic_level not in course_section_info_details['academic_level']:
        course_section_info_details['academic_level'].append(academic_level)
      
      if instruction_mode not in course_section_info_details['instruction_mode']:
        course_section_info_details['instruction_mode'].append(instruction_mode)

      if days_in_a_week not in course_section_info_details['days_in_a_week']:
        course_section_info_details['days_in_a_week'].append(days_in_a_week)
      
      if course_dept not in course_section_info_details['course_dept']:
        course_section_info_details['course_dept'].append(course_dept)

      if dname not in course_section_info_details['dname']:
        course_section_info_details['dname'].append(dname)
      
      if id not in course_section_info_details['id']:
        course_section_info_details['id'].append(id)

      if name not in course_section_info_details['name']:
        course_section_info_details['name'].append(name)

    cursor.close()
    return course_section_info_details  
  except Exception as e:
    print(f"Error from database (course_section_info_details): {str(e)}") 
    return {}

def get_course_section_info_filter(year, term, where):
  params_dict = {
    'year': year,
    'term': term
  }
  #print(where)
  try:
    query = """
                 SELECT cid, cname, credits, major, academic_level, cid_prerequisite,
                 sec_num, instruction_mode, max_capacity, actual_enrollment, tid, days_in_a_week,
                 start_time, end_time, room_num, sec_address, capacity, bname, course_dept,
                 dname, course_dept_address, id, name, email, instru_dept, since
                 FROM Course_Section_Info CSI
                 WHERE year = :year AND term = :term
                 """
    
    query += where
    query += """ ORDER BY cid ASC, sec_num ASC, days_in_a_week ASC;"""
    query = text(query)
    # print(query)

    cursor = g.conn.execute(query, params_dict)
    course_section_info = {}
    results = cursor.mappings().all()
    for result in results:
      cid = result["cid"]
      cname = result["cname"]
      credits = result["credits"]
      major = result["major"]
      academic_level = result["academic_level"]
      cid_prerequisite = result["cid_prerequisite"]
      sec_num = result["sec_num"]
      instruction_mode = result["instruction_mode"]
      max_capacity = result["max_capacity"]
      actual_enrollment = result["actual_enrollment"]
      tid = result["tid"]
      days_in_a_week = result["days_in_a_week"]
      start_time = result["start_time"]
      end_time = result["end_time"]
      room_num = result["room_num"]
      sec_address = result["sec_address"]
      capacity = result["capacity"]
      bname = result["bname"]
      course_dept = result["course_dept"]
      dname = result["dname"]
      course_dept_address = result["course_dept_address"]
      id = result["id"]
      name = result["name"]
      email = result["email"]
      instru_dept = result["instru_dept"]
      since = result["since"]
      # print('.....................')
      # print(result)
      if cid not in course_section_info:
        course_section_info[cid] = {
            'cname': cname,
            'credits': credits,
            'major': major,
            'academic_level': academic_level,
            'cid_prerequisite': cid_prerequisite,
            'course_dept': course_dept,
            'dname': dname,
            'course_dept_address': course_dept_address,
          }
      if sec_num not in course_section_info[cid]:
          course_section_info[cid][sec_num] = {
            'instruction_mode': instruction_mode,
            'max_capacity': max_capacity,
            'actual_enrollment': actual_enrollment,
            'address': {'bname': bname,
                      'room_num': room_num,
                      'sec_address': sec_address,
                      'capacity': capacity},
            'instructor': {'id': id,
                           'name': name,
                           'email': email,
                           'instru_dept': instru_dept,
                           'since': since},
            'time': {}
          }

      if days_in_a_week not in course_section_info[cid][sec_num]['time']:
          course_section_info[cid][sec_num]['time'][days_in_a_week] = {
            'tid': tid,
            'start_time': start_time,
            'end_time': end_time
          }
    cursor.close()
    return course_section_info  
  except Exception as e:
    print(f"Error from database (course_section_info_filter): {str(e)}") 
    return {}
  

def get_ins_time_loc_info(year, term):
  params_dict = {
    'year': year,
    'term': term
  }
  try:
    query = text("""
                 SELECT id, name, email, days_in_a_week, tid, 
                 address, bname, room_num, capacity,
                 start_time, end_time
                 FROM Instructor_Time_Location_Info ITL
                 WHERE year = :year AND term = :term
                 ORDER BY id ASC, days_in_a_week ASC, tid ASC, bname ASC, room_num ASC;
                 """)
    cursor = g.conn.execute(query, params_dict)
    ins_time_loc = []
    results = cursor.mappings().all()
    for result in results:
      id = result["id"].strip()
      name = result["name"].strip()
      email = result["email"].strip()
      days_in_a_week = result["days_in_a_week"].strip()
      tid = result["tid"]
      address = result["address"].strip()
      bname = result["bname"].strip()
      room_num = result["room_num"]
      capacity = result["capacity"]
      start_time = result["start_time"]
      end_time = result["end_time"]
      # print('.....................')
      # print(result)
      ins_time_loc.append([id, name, email, days_in_a_week, tid, start_time, end_time, address, bname, room_num, capacity])
    cursor.close()
    return ins_time_loc  
  except Exception as e:
    print(f"Error from database (ins_time_loc): {str(e)}") 
    return {}
  
def get_occupied_ins_time_loc_info(year, term):
  try:
    course_section_info = get_course_section_info(year, term)
    occupied_time_location = []
    occupied_time_instructor = []
    occupied_ins_time_loc = []
    # print(course_section_info)
    for cid, course in course_section_info.items():
      for sec_num, section in course.items():
        if sec_num not in ['cname', 'credits', 'major', 'academic_level', 'cid_prerequisite', 'course_dept', 'dname', 'course_dept_address']:
          for day, time in section['time'].items():
            occupied_time_location.append([section['address']['bname'].strip(), section['address']['sec_address'].strip(), section['address']['room_num'], section['address']['capacity'],
                                           day.strip(), time['tid'], time['start_time'], time['end_time']])
            occupied_time_instructor.append([section['instructor']['id'].strip(), section['instructor']['name'].strip(), section['instructor']['email'].strip(),
                                           day.strip(), time['tid'], time['start_time'], time['end_time']])
            occupied_ins_time_loc.append([section['instructor']['id'].strip(), section['instructor']['name'].strip(), section['instructor']['email'].strip(),
                                          day.strip(), time['tid'], time['start_time'], time['end_time'],
                                          section['address']['sec_address'].strip(), section['address']['bname'].strip(), section['address']['room_num'], section['address']['capacity']])
    return occupied_ins_time_loc  
  except Exception as e:
    print(f"Error from database (occupied_ins_time_loc_info): {str(e)}") 
    return {}

def get_available_ins_time_loc_info(year, term):
  instructor_timeslot_location = get_ins_time_loc_info(year, term)
  occupied_ins_time_loc = get_occupied_ins_time_loc_info(year, term)
  available_ins_time_loc = []
  # [id, name, email, days_in_a_week, tid, start_time, end_time, address, bname, room_num, capacity]
  # print(f"instructor_timeslot_location: {len(instructor_timeslot_location)}")

  try:
    for i in range(len(instructor_timeslot_location)):
      ins_time_loc = instructor_timeslot_location[i]
      is_available = True

      for j in range(len(occupied_ins_time_loc)):
        occupied = occupied_ins_time_loc[j]
        
        if ins_time_loc[:6] == occupied[:6]:
          is_available = False
          break

        if ins_time_loc[3:] == occupied[3:]:
          is_available = False
          break
        
      if is_available:
        available_ins_time_loc.append(ins_time_loc)

    
    # print(f"available_ins_time_loc: {len(available_ins_time_loc)}")
    # for i in available_ins_time_loc:
    #   print(i)
    # print(available_ins_time_loc)
    # print(f"occupied_ins_time_loc: {len(occupied_ins_time_loc)}")
    # for i in occupied_ins_time_loc:
    #   print(i)
    # print(occupied_ins_time_loc)
    return available_ins_time_loc  
  except Exception as e:
    print(f"Error from database (available_ins_time_loc): {str(e)}") 
    return {}

def get_enrolls_info(year, term):
  params_dict = {
    'year': year,
    'term': term
  }
  try:
    query = text("""
                 SELECT E.sid, S.sname, S.semail, S.major, S.academic_level, S.gpa, E.cid, E.sec_num, E.grade
                 FROM Sections_Enrolls E
                 INNER JOIN Students S ON S.sid = E.sid
                 WHERE year = :year AND term = :term
                 ORDER BY sid ASC, cid ASC, sec_num ASC;
                 """)
    
    cursor = g.conn.execute(query, params_dict)
    enrolls = {}
    results = cursor.mappings().all()
    for result in results:
      sid = result["sid"]
      sname = result["sname"]
      semail = result["semail"]
      major = result["major"]
      academic_level = result["academic_level"]
      gpa = result["gpa"]
      cid = result["cid"]
      sec_num = result["sec_num"]
      grade = result["grade"]
      if (sid, cid, sec_num) not in enrolls:
        enrolls[(sid, cid, sec_num)] = {
          'sname': sname,
          'semail': semail,
          'major': major,
          'academic_level': academic_level,
          'gpa': gpa,
          'grade': grade
        } 
    cursor.close()
    return enrolls  
  except Exception as e:
    print(f"Error from database (enrolls): {str(e)}") 
    return {}
  
def get_waitlists_info(year, term):
  params_dict = {
    'year': year,
    'term': term
  }
  try:
    query = text("""
                 SELECT W.sid, S.sname, S.semail, S.major, S.academic_level, S.gpa, W.cid, W.sec_num, W.join_date
                 FROM Sections_Waitlists W
                 INNER JOIN Students S ON S.sid = W.sid
                 WHERE year = :year AND term = :term
                 ORDER BY sid ASC, cid ASC, sec_num ASC;
                 """)
    
    cursor = g.conn.execute(query, params_dict)
    waitlists = {}
    results = cursor.mappings().all()
    for result in results:
      sid = result["sid"]
      sname = result["sname"]
      semail = result["semail"]
      major = result["major"]
      academic_level = result["academic_level"]
      gpa = result["gpa"]
      cid = result["cid"]
      sec_num = result["sec_num"]
      join_date = result["join_date"]
      if (sid, cid, sec_num) not in waitlists:
        waitlists[(sid, cid, sec_num)] = {
          'sname': sname,
          'semail': semail,
          'major': major,
          'academic_level': academic_level,
          'gpa': gpa,
          'join_date': join_date
        } 
    cursor.close()
    return waitlists  
  except Exception as e:
    print(f"Error from database (waitlists): {str(e)}") 
    return {}

def get_ins_course_info(year, term, id):
  params_dict = {
    'year': year,
    'term': term,
    'id': id,
  }
  try:
    query = text("""
                 SELECT cid, cname, credits, major, academic_level, cid_prerequisite,
                 sec_num, instruction_mode, max_capacity, actual_enrollment, tid, days_in_a_week,
                 start_time, end_time, room_num, sec_address, capacity, bname, course_dept,
                 dname, course_dept_address, id, name, email, instru_dept, since
                 FROM Course_Section_Info CSI
                 WHERE id = :id AND year = :year AND term = :term
                 ORDER BY cid ASC, sec_num ASC, days_in_a_week ASC;
                 """)

    cursor = g.conn.execute(query, params_dict)
    ins_course = {}
    results = cursor.mappings().all()
    for result in results:
      cid = result["cid"]
      cname = result["cname"]
      credits = result["credits"]
      major = result["major"]
      academic_level = result["academic_level"]
      cid_prerequisite = result["cid_prerequisite"]
      sec_num = result["sec_num"]
      instruction_mode = result["instruction_mode"]
      max_capacity = result["max_capacity"]
      actual_enrollment = result["actual_enrollment"]
      tid = result["tid"]
      days_in_a_week = result["days_in_a_week"]
      start_time = result["start_time"]
      end_time = result["end_time"]
      room_num = result["room_num"]
      sec_address = result["sec_address"]
      capacity = result["capacity"]
      bname = result["bname"]
      course_dept = result["course_dept"]
      dname = result["dname"]
      course_dept_address = result["course_dept_address"]
      id = result["id"]
      name = result["name"]
      email = result["email"]
      instru_dept = result["instru_dept"]
      since = result["since"]
      if cid not in ins_course:
        ins_course[cid] = {
            'cname': cname,
            'credits': credits,
            'major': major,
            'academic_level': academic_level,
            'cid_prerequisite': cid_prerequisite,
            'course_dept': course_dept,
            'dname': dname,
            'course_dept_address': course_dept_address,
          }
      if sec_num not in ins_course[cid]:
          ins_course[cid][sec_num] = {
            'instruction_mode': instruction_mode,
            'max_capacity': max_capacity,
            'actual_enrollment': actual_enrollment,
            'address': {'bname': bname,
                      'room_num': room_num,
                      'sec_address': sec_address,
                      'capacity': capacity},
            'instructor': {'id': id,
                           'name': name,
                           'email': email,
                           'instru_dept': instru_dept,
                           'since': since},
            'time': {}
          }

      if days_in_a_week not in ins_course[cid][sec_num]['time']:
          ins_course[cid][sec_num]['time'][days_in_a_week] = {
            'tid': tid,
            'start_time': start_time,
            'end_time': end_time
          }
    cursor.close()
    return ins_course  
  except Exception as e:
    print(f"Error from database (ins_course): {str(e)}") 
    return {}

def get_stu_enroll_info(year, term, sid):
  params_dict = {
    'year': year,
    'term': term,
    'sid': sid,
  }
  try:
    query = text("""
                 SELECT E.cid, CSI.cname, CSI.credits, CSI.sec_num, CSI.instruction_mode, 
                 CSI.tid, CSI.days_in_a_week, CSI.start_time, CSI.end_time, 
                 CSI.sec_address, CSI.bname, CSI.room_num, CSI.capacity, CSI.course_dept, CSI.dname, 
                 CSI.id, CSI.name, CSI.email, 
                 CSI.major, CSI.academic_level, CSI.cid_prerequisite, E.grade
                 FROM Sections_Enrolls E
                 INNER JOIN Students S ON S.sid = E.sid
                 INNER JOIN Course_Section_Info CSI ON CSI.cid = E.cid AND CSI.sec_num = E.sec_num AND CSI.year = E.year AND CSI.term = E.term
                 WHERE E.sid = :sid AND E.year = :year AND E.term = :term
                 ORDER BY E.sid ASC, E.cid ASC, CSI.sec_num ASC, CSI.days_in_a_week, CSI.tid;
                 """)
    
    cursor = g.conn.execute(query, params_dict)
    stu_enroll = {}
    results = cursor.mappings().all()
    for result in results:
      cid = result["cid"]
      cname = result["cname"]
      credits = result["credits"]
      sec_num = result["sec_num"]
      instruction_mode = result["instruction_mode"]
      tid = result["tid"]
      days_in_a_week = result["days_in_a_week"]
      start_time = result["start_time"]
      end_time = result["end_time"]
      sec_address = result["sec_address"]
      bname = result["bname"]
      room_num = result["room_num"]
      capacity = result["capacity"]
      course_dept = result["course_dept"]
      dname = result["dname"]
      id = result["id"]
      name = result["name"]
      email = result["email"]
      major = result["major"]
      academic_level = result["academic_level"]
      cid_prerequisite = result["cid_prerequisite"]
      grade = result["grade"]
      if cid not in stu_enroll:
        stu_enroll[cid] = {}

      if sec_num not in stu_enroll[cid]:
        stu_enroll[cid][sec_num] = {
          'cname': cname,
          'credits': credits,
          'instruction_mode': instruction_mode,
          'sec_address': sec_address,
          'bname': bname,
          'room_num': room_num,
          'capacity': capacity,
          'course_dept': course_dept,
          'dname': dname,
          'id': id,
          'name': name,
          'email': email,
          'major': major,
          'academic_level': academic_level,
          'cid_prerequisite': cid_prerequisite,
          'grade': grade,
          'time': {}
        }
      
      if days_in_a_week not in stu_enroll[cid][sec_num]['time']:
          stu_enroll[cid][sec_num]['time'][days_in_a_week] = {
            'tid': tid,
            'start_time': start_time,
            'end_time': end_time
          }

    cursor.close()
    return stu_enroll  
  except Exception as e:
    print(f"Error from database (stu_enroll): {str(e)}") 
    return {}

def get_stu_enroll_info0(sid):
  params_dict = {
    'sid': sid
  }
  try:
    query = text("""
                 SELECT E.cid, CSI.cname, CSI.credits, CSI.sec_num, CSI.instruction_mode, 
                 CSI.tid, CSI.days_in_a_week, CSI.start_time, CSI.end_time, 
                 CSI.sec_address, CSI.bname, CSI.room_num, CSI.capacity, CSI.course_dept, CSI.dname, 
                 CSI.id, CSI.name, CSI.email, 
                 CSI.major, CSI.academic_level, CSI.cid_prerequisite, E.grade
                 FROM Sections_Enrolls E
                 INNER JOIN Students S ON S.sid = E.sid
                 INNER JOIN Course_Section_Info CSI ON CSI.cid = E.cid AND CSI.sec_num = E.sec_num AND CSI.year = E.year AND CSI.term = E.term
                 WHERE E.sid = :sid
                 ORDER BY E.sid ASC, E.cid ASC, CSI.sec_num ASC, CSI.days_in_a_week, CSI.tid;
                 """)
    
    cursor = g.conn.execute(query, params_dict)
    stu_enroll = {}
    results = cursor.mappings().all()
    for result in results:
      cid = result["cid"]
      cname = result["cname"]
      credits = result["credits"]
      sec_num = result["sec_num"]
      instruction_mode = result["instruction_mode"]
      tid = result["tid"]
      days_in_a_week = result["days_in_a_week"]
      start_time = result["start_time"]
      end_time = result["end_time"]
      sec_address = result["sec_address"]
      bname = result["bname"]
      room_num = result["room_num"]
      capacity = result["capacity"]
      course_dept = result["course_dept"]
      dname = result["dname"]
      id = result["id"]
      name = result["name"]
      email = result["email"]
      major = result["major"]
      academic_level = result["academic_level"]
      cid_prerequisite = result["cid_prerequisite"]
      grade = result["grade"]
      if cid not in stu_enroll:
        stu_enroll[cid] = {}

      if sec_num not in stu_enroll[cid]:
        stu_enroll[cid][sec_num] = {
          'cname': cname,
          'credits': credits,
          'instruction_mode': instruction_mode,
          'sec_address': sec_address,
          'bname': bname,
          'room_num': room_num,
          'capacity': capacity,
          'course_dept': course_dept,
          'dname': dname,
          'id': id,
          'name': name,
          'email': email,
          'major': major,
          'academic_level': academic_level,
          'cid_prerequisite': cid_prerequisite,
          'grade': grade,
          'time': {}
        }
      
      if days_in_a_week not in stu_enroll[cid][sec_num]['time']:
          stu_enroll[cid][sec_num]['time'][days_in_a_week] = {
            'tid': tid,
            'start_time': start_time,
            'end_time': end_time
          }

    cursor.close()
    return stu_enroll  
  except Exception as e:
    print(f"Error from database (stu_enroll): {str(e)}") 
    return {}


def get_stu_waitlist_info(year, term, sid):
  params_dict = {
    'year': year,
    'term': term,
    'sid': sid,
  }
  try:
    query = text("""
                SELECT W.cid, CSI.cname, CSI.credits, CSI.sec_num, CSI.instruction_mode, 
                  CSI.tid, CSI.days_in_a_week, CSI.start_time, CSI.end_time, 
                  CSI.sec_address, CSI.bname, CSI.room_num, CSI.capacity, CSI.course_dept, CSI.dname, 
                  CSI.id, CSI.name, CSI.email, 
                  CSI.major, CSI.academic_level, CSI.cid_prerequisite, W.join_date
                FROM Sections_Waitlists W
                INNER JOIN Students S ON S.sid = W.sid
                INNER JOIN Course_Section_Info CSI ON CSI.cid = W.cid AND CSI.sec_num = W.sec_num AND CSI.year = W.year AND CSI.term = W.term
                WHERE W.sid = :sid AND W.year = :year AND W.term = :term
                ORDER BY W.sid ASC, W.cid ASC, CSI.sec_num ASC;
                """)
    cursor = g.conn.execute(query, params_dict)
    stu_wl = {}
    results = cursor.mappings().all()
    for result in results:
        cid = result["cid"]
        cname = result["cname"]
        credits = result["credits"]
        sec_num = result["sec_num"]
        instruction_mode = result["instruction_mode"]
        tid = result["tid"]
        days_in_a_week = result["days_in_a_week"]
        start_time = result["start_time"]
        end_time = result["end_time"]
        sec_address = result["sec_address"]
        bname = result["bname"]
        room_num = result["room_num"]
        capacity = result["capacity"]
        course_dept = result["course_dept"]
        dname = result["dname"]
        id = result["id"]
        name = result["name"]
        email = result["email"]
        major = result["major"]
        academic_level = result["academic_level"]
        cid_prerequisite = result["cid_prerequisite"]
        join_date = result["join_date"]
        if cid not in stu_wl:
          stu_wl[cid] = {}

        if sec_num not in stu_wl[cid]:
          stu_wl[cid][sec_num] = {
            'cname': cname,
            'credits': credits,
            'instruction_mode': instruction_mode,
            'sec_address': sec_address,
            'bname': bname,
            'room_num': room_num,
            'capacity': capacity,
            'course_dept': course_dept,
            'dname': dname,
            'id': id,
            'name': name,
            'email': email,
            'major': major,
            'academic_level': academic_level,
            'cid_prerequisite': cid_prerequisite,
            'join_date': join_date,
            'time': {}
          }
        
        if days_in_a_week not in stu_wl[cid][sec_num]['time']:
            stu_wl[cid][sec_num]['time'][days_in_a_week] = {
              'tid': tid,
              'start_time': start_time,
              'end_time': end_time
            }
    cursor.close()
    return stu_wl  
  except Exception as e:
    print(f"Error from database (waitlists): {str(e)}") 
    return {}

  
@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass

@app.route('/')
def index():
  # DEBUG: this is debugging code to see what request looks like
  print(request.args)
  return render_template("index.html")

# Instructor login
@app.route('/login/instructor', methods = ['GET', 'POST'])
def instructor_login():
  if request.method == 'POST':
    instructor_id = request.form['ID']
    password = request.form['password']
    params_dict = {"instructor_id": instructor_id}

    error_message = None
    if not instructor_id or not password:
      error_message = "ID and Password cannot be empty!"
      return render_template('login.html', role = "Instructor", error_message = error_message)

    query = text("SELECT password FROM instructors_works_in WHERE id = :instructor_id")
    cursor = g.conn.execute(query, params_dict)
    
    instructor_password = None
    for result in cursor:
      instructor_password = result[0]
    cursor.close()
    
    if instructor_password:
      if instructor_password == password:
        session['instructor_id'] = instructor_id 
        return redirect(url_for('instructor_dashboard'))
      else:
        error_message =  "Wrong passward!"
    else:
      error_message = "ID does not exist, please check！"
    return render_template('login.html', role = "Instructor", error_message = error_message)

  return render_template('login.html', role = "Instructor")

# Student login 
@app.route('/login/student', methods = ['GET', 'POST'])
def student_login():
  if request.method == 'POST':
    student_id = request.form['ID']
    password = request.form['password']
    params_dict = {"student_id": student_id}

    error_message = None
    if not student_id or not password:
      error_message = "ID and Password cannot be empty!"
      return render_template('login.html', role = "Student", error_message = error_message)

    query = text("SELECT password FROM students WHERE sid = :student_id")
    cursor = g.conn.execute(query, params_dict)
    
    student_password = None
    for result in cursor:
      student_password = result[0]
    cursor.close()
    
    if student_password:
      if student_password == password:
        session['student_id'] = student_id 
        return redirect(url_for('student_dashboard'))
      else:
        error_message =  "Wrong passward!"
    else:
      error_message = "ID does not exist, please check！"
    return render_template('login.html', role = "Student", error_message = error_message)

  return render_template('login.html', role = "Student")

# Admin login
@app.route('/login/admin', methods = ['GET', 'POST'])
def admin_login():
  if request.method == 'POST':
    admin_id = request.form['ID']
    password = request.form['password']
    params_dict = {"admin_id": admin_id}

    error_message = None
    if not admin_id or not password:
      error_message = "ID and Password cannot be empty!"
      return render_template('login.html', role = "Admin", error_message = error_message)

    query = text("SELECT password FROM Admins WHERE aid = :admin_id")
    cursor = g.conn.execute(query, params_dict)
    
    admin_password = None
    for result in cursor:
      admin_password = result[0]
    cursor.close()
    
    if admin_password:
      if admin_password == password:
        session['admin_id'] = admin_id
        return redirect(url_for('admin_dashboard'))
      else:
        error_message =  "Wrong passward!"
    else:
      error_message = "ID does not exist, please check！"
    return render_template('login.html', role = "Admin", error_message = error_message)
  
  return render_template('login.html', role = "Admin")

# Admin dashboard
@app.route('/admin/dashboard',  methods = ['GET', 'POST'])
def admin_dashboard():
  admin_id = session.get('admin_id') 
  if not admin_id: 
      return redirect(url_for('admin_login'))
  
  query = text("SELECT year, term FROM Calendar ORDER BY year DESC, term DESC")
  cursor = g.conn.execute(query)
  
  year_terms = {}
  results = cursor.mappings().all()
  for result in results:
    year = result["year"]
    term = result["term"]
    if year not in year_terms:
      year_terms[year] = []
    year_terms[year].append(term) 
  cursor.close()

  if request.method == 'GET':
    selected_year_term = request.args.get('year_terms')
    # print(selected_year_term) 
    if selected_year_term:
      year, term = selected_year_term.split(',')
      # print(f"Year: {year}, Term: {term}") 
      return redirect(url_for('admin_manage', year = year, term = term))
    
    
  elif request.method == 'POST':
    new_year = request.form.get('new_year')
    new_term = request.form.get('new_term')
    add_wl_ddl = request.form.get('add_wl_ddl')
    drop_ddl = request.form.get('drop_ddl')

    if not new_year or not new_term:
      error_message = "Year and Term are required!"
      return render_template('admin/dashboard.html', year_terms = year_terms, error_message = error_message, admin_id = admin_id)

    if not re.match(r'^\d{4}$', new_year):
      error_message = "Year must be 4-digit number (e.g. 2024)!"
      return render_template('admin/dashboard.html', year_terms = year_terms, error_message = error_message, admin_id = admin_id)

    try:
      if add_wl_ddl and drop_ddl:
        add_wl_ddl = datetime.strptime(add_wl_ddl, '%Y-%m-%d')
        drop_ddl = datetime.strptime(drop_ddl, '%Y-%m-%d')
    except ValueError:
      error_message = "Deadline date must be vaild dates (yyyy-mm-dd)!"
      return render_template('admin/dashboard.html', year_terms = year_terms, error_message = error_message, admin_id = admin_id)

    if add_wl_ddl >= drop_ddl:
      error_message = "Deadline for drop courses must be late than deadline for add/waitlist courses!"
      return render_template('admin/dashboard.html', year_terms = year_terms, error_message = error_message, admin_id = admin_id)
    
    if new_term == 'Fall':
      add_start = datetime(int(new_year), 8, 16)  
      add_end = datetime(int(new_year), 12, 31) 
      drop_start = add_start
      drop_end = add_end
    elif new_term == 'Spring':
      add_start = datetime(int(new_year), 1, 1)  
      add_end = datetime(int(new_year), 5, 24)   
      drop_start = add_start
      drop_end = add_end
    elif new_term == 'Summer':
      add_start = datetime(int(new_year), 5, 25) 
      add_end = datetime(int(new_year), 8, 15)  
      drop_start = add_start
      drop_end = add_end
    else:
      error_message = "Invalid term selected!"
      return render_template('admin/dashboard.html', year_terms = year_terms, error_message = error_message, admin_id = admin_id)

    if not (add_start <= add_wl_ddl <= add_end):
      error_message = f"Add/Waitlist deadline must be between {add_start.date()} and {add_end.date()}!"
      return render_template('admin/dashboard.html', year_terms = year_terms, error_message = error_message, admin_id = admin_id)

    if not (drop_start <= drop_ddl <= drop_end):
      error_message = f"Drop deadline must be between {drop_start.date()} and {drop_end.date()}!"
      return render_template('admin/dashboard.html', year_terms = year_terms, error_message = error_message, admin_id = admin_id)

    params_dict = {
      'year': new_year, 
      'term': new_term, 
      'add_wl_ddl': add_wl_ddl,
      'drop_ddl': drop_ddl
    }
    
    try:
      query = text("""
                  INSERT INTO Calendar (year, term, add_waitlist_ddl, drop_ddl) 
                  VALUES (:year, :term, :add_wl_ddl, :drop_ddl)
                  """)
      g.conn.execute(query, params_dict)

      query1 = text("""
                  INSERT INTO Courses 
                  VALUES ('None', 'None', 0, 'None', 'None', :year, :term)
                  """)
      g.conn.execute(query1, params_dict)
      g.conn.commit()
      message = f"Successfully created {new_year} {new_term}!"
      
      query = text("SELECT year, term FROM Calendar ORDER BY year DESC, term DESC")
      cursor = g.conn.execute(query)
  
      year_terms = {}
      results = cursor.mappings().all()
      for result in results:
        year = result["year"]
        term = result["term"]
        if year not in year_terms:
          year_terms[year] = []
        year_terms[year].append(term) 
      cursor.close()
      courses = get_courses(year, term)
      params_dict['courses'] = courses
      return render_template('admin/dashboard.html', 
                             message = message, year_terms = year_terms, admin_id = admin_id, **params_dict)
    except Exception as e:
      error_message = f"Error from database: {str(e)}!"
      return render_template('admin/dashboard.html', year_terms = year_terms, error_message = error_message, admin_id = admin_id)
  return render_template('admin/dashboard.html', 
                         year_terms = year_terms, admin_id = admin_id)

# Admin manage
@app.route('/admin/manage/<year>/<term>', methods = ['GET', 'POST'])
def admin_manage(year, term):
  admin_id = session.get('admin_id')
  if not admin_id:
    return redirect(url_for('admin_login'))
  
  params_dict = {
    'year': year,
    'term': term,
    'admin_id': admin_id,
  }

  if request.method == 'POST':
    action = request.form.get('action') 
    if action == 'calendar_manage':
      return redirect(url_for('admin_calendar_manage', year = year, term = term))
    elif action == 'timeslot_manage':
      return redirect(url_for('admin_timeslot_manage', year = year, term = term))
    
  return render_template('admin/manage.html', **params_dict)

# Admin manage calendar
@app.route('/admin/manage/calendar/<year>/<term>', methods = ['GET', 'POST'])
def admin_manage_calendar(year, term):
  admin_id = session.get('admin_id') 
  if not admin_id: 
      return redirect(url_for('admin_login'))
  
  holidays = get_holidays(year, term)
  ddls = get_calendar(year, term)

  params_dict = {
    'holidays': holidays, 
    'ddls': ddls,  
    'year': year, 
    'term': term, 
    'admin_id': admin_id
  }
  
  if request.method == 'POST':
    update_holiday = None
    delete_holiday = None
    add_holiday = request.form.get('add_holiday')

    for hname in holidays.keys():
      if request.form.get(f'update_{hname}'):
        update_holiday = hname
      elif request.form.get(f'delete_{hname}'):
        delete_holiday = hname

    update_ddl = request.form.get('update_ddl')
    new_hname = request.form.get('new_hname')
    new_from_date = request.form.get('new_from_date')
    new_to_date = request.form.get('new_to_date')
    new_add_wl_ddl = request.form.get('new_add_wl_ddl')
    new_drop_ddl = request.form.get('new_drop_ddl')

    try:
      if new_from_date and new_to_date:
        new_from_date = datetime.strptime(new_from_date, '%Y-%m-%d')
        new_to_date = datetime.strptime(new_to_date, '%Y-%m-%d')
    except ValueError:
      calendar_error_message = "Date must be vaild dates (yyyy-mm-dd)!"
      return render_template('admin/manage_calendar.html', 
                             calendar_error_message = calendar_error_message, **params_dict)

    if not new_add_wl_ddl:
      new_add_wl_ddl = ddls[0]['add_waitlist_ddl']
    else: 
      new_add_wl_ddl = datetime.strptime(new_add_wl_ddl, '%Y-%m-%d')

    if not new_drop_ddl:
      new_drop_ddl = ddls[0]['drop_ddl']
    else:
      new_drop_ddl = datetime.strptime(new_drop_ddl, '%Y-%m-%d')
    
    if new_add_wl_ddl >= new_drop_ddl:
      calendar_error_message = "Deadline for drop courses must be late than deadline for add/waitlist courses!"
      return render_template('admin/manage_calendar.html', 
                             calendar_error_message = calendar_error_message, **params_dict)
    
    if update_holiday:
      try:
        update_from_date = request.form.get(f'from_date_{update_holiday}')
        update_to_date = request.form.get(f'to_date_{update_holiday}')
        # print(update_from_date)
        # print(update_to_date)
        # print(update_holiday)

        if not update_from_date:
          update_from_date = holidays[update_holiday]['from_date']
        else: 
          update_from_date = datetime.strptime(update_from_date, '%Y-%m-%d')

        if not update_to_date:
          update_to_date =  holidays[update_holiday]['to_date']
        else:
          update_to_date = datetime.strptime(update_to_date, '%Y-%m-%d')
        
        query_update = text("""
                            UPDATE Holiday_falls_in 
                            SET from_date = :from_date, to_date = :to_date
                            WHERE hname = :hname AND year = :year AND term = :term
                            """)
        g.conn.execute(query_update, {'hname': update_holiday,
                                      'from_date': update_from_date,
                                      'to_date': update_to_date,
                                      'year': year,
                                      'term': term})
        g.conn.commit()
        calendar_message = f"Successfully update the hoilday {update_holiday}!"
        holidays = get_holidays(year, term)
        params_dict['holidays'] = holidays
        return render_template('admin/manage_calendar.html', 
                              calendar_message = calendar_message, **params_dict)
      except Exception as e:
        calendar_error_message = f"Error from database: {str(e)}"
        return render_template('admin/manage_calendar.html', 
                               calendar_error_message = calendar_error_message, **params_dict)

    if delete_holiday:
      try:
        query_delete = text("""
                            DELETE FROM Holiday_falls_in
                            WHERE hname = :hname AND year = :year AND term = :term
                            """)
        g.conn.execute(query_delete, {'hname': delete_holiday,
                                      'year': year,
                                      'term': term})
        g.conn.commit()
        calendar_message = f"Successfully delete the hoilday {delete_holiday}!"
        holidays = get_holidays(year, term)
        params_dict['holidays'] = holidays
        return render_template('admin/manage_calendar.html', 
                               calendar_message = calendar_message, **params_dict)
      except Exception as e:
        calendar_error_message = f"Error from database: {str(e)}"
        return render_template('admin/manage_calendar.html', 
                               calendar_error_message = calendar_error_message, **params_dict)

    if add_holiday and new_hname and new_from_date and new_to_date:
      try:
        query_insert = text("""
                            INSERT INTO Holiday_falls_in (hname, from_date, to_date, year, term)
                            VALUES (:hname, :from_date, :to_date, :year, :term)
                            """)
        g.conn.execute(query_insert, {'hname': new_hname, 
                                      'from_date': new_from_date,
                                      'to_date': new_to_date,
                                      'year': year,
                                      'term': term})
        g.conn.commit()
        calendar_message = f"Successfully add a new hoilday {new_hname} from date {new_from_date} to date {new_to_date}!"
        holidays = get_holidays(year, term)
        params_dict['holidays'] = holidays
        return render_template('admin/manage_calendar.html', 
                              calendar_message = calendar_message, **params_dict)
      except Exception as e:
        calendar_error_message = f"Error from database: {str(e)}"
        return render_template('admin/manage_calendar.html', 
                               calendar_error_message = calendar_error_message, **params_dict)

    if update_ddl:
      try:
        query_update = text("""
                            UPDATE Calendar 
                            SET add_waitlist_ddl = :add_wl_ddl, drop_ddl = :drop_ddl
                            WHERE year = :year AND term = :term
                            """)
        g.conn.execute(query_update, {'add_wl_ddl': new_add_wl_ddl, 
                                      'drop_ddl': new_drop_ddl,
                                      'year': year,
                                      'term': term})
        g.conn.commit()
        calendar_message = f"Successfully update add/waitlist deadline {new_add_wl_ddl} and drop deadline {new_drop_ddl} to {year} {term}!"
        ddls = get_calendar(year, term)
        params_dict['ddls'] = ddls
        return render_template('admin/manage_calendar.html', 
                              calendar_message = calendar_message, **params_dict)
      
      except Exception as e:
        calendar_error_message = f"Error from database: {str(e)}"
        return render_template('admin/manage_calendar.html', 
                               calendar_error_message = calendar_error_message, **params_dict)
  return render_template('admin/manage_calendar.html', **params_dict)
   
# Admin manage timeslot
@app.route('/admin/manage/timeslot/<year>/<term>', methods = ['GET', 'POST'])
def admin_manage_timeslot(year, term):
  admin_id = session.get('admin_id') 
  if not admin_id: 
      return redirect(url_for('admin_login'))

  timeslots = get_timeslot_allocates(year, term)

  params_dict = { 
    'year': year, 
    'term': term, 
    'admin_id': admin_id,
    'timeslots': timeslots
  }
  
  if request.method == 'POST':
    update_timeslot = None
    delete_timeslot = None
    add_timeslot = request.form.get('add_timeslot')
    
    for (tid, day) in timeslots.keys():
      if request.form.get(f'update_{tid}_{day}'):
        update_timeslot = (tid, day)
      elif request.form.get(f'delete_{tid}_{day}'):
        delete_timeslot = (tid, day)

    new_tid = request.form.get('new_tid')
    new_day = request.form.get('new_day')
    new_start_time = request.form.get('new_start_time')
    new_end_time = request.form.get('new_end_time')

    if add_timeslot and new_tid and new_day and new_start_time and new_end_time:
      try:
        query_insert = text("""
                            INSERT INTO Timeslot_allocates (tid, days_in_a_week, start_time, end_time, year, term)
                            VALUES (:tid, :days_in_a_week, :start_time, :end_time, :year, :term)
                            """)
        g.conn.execute(query_insert, {'tid': new_tid, 
                                      'days_in_a_week': new_day,
                                      'start_time': new_start_time,
                                      'end_time': new_end_time,
                                      'year': year,
                                      'term': term})
        g.conn.commit()
        time_message = f"Successfully add a new timeslot {new_tid} on {new_day} from {new_start_time} to {new_end_time}!"
        timeslots = get_timeslot_allocates(year, term)
        params_dict['timeslots'] = timeslots
        return render_template('admin/manage_timeslot.html', 
                              time_message = time_message, **params_dict)
      except Exception as e:
        time_error_message = f"Error from database: {str(e)}"
        return render_template('admin/manage_timeslot.html', 
                               time_error_message = time_error_message, **params_dict)

    if update_timeslot:
      try:
        update_start_time = request.form.get(f'start_time_{tid}_{day}')
        update_end_time = request.form.get(f'end_time_{tid}_{day}')
        # print(update_start_time)
        # print(update_end_time)

        if not update_start_time:
          update_start_time = timeslots[update_timeslot]['start_time']

        if not update_end_time:
          update_end_time =  timeslots[update_timeslot]['end_time']
        
        query_update = text("""
                            UPDATE Timeslot_allocates 
                            SET start_time = :start_time, end_time = :end_time
                            WHERE tid = :tid AND days_in_a_week = :days_in_a_week AND year = :year AND term = :term
                            """)
        g.conn.execute(query_update, {'tid': update_timeslot[0],
                                      'days_in_a_week': update_timeslot[1],
                                      'start_time': update_start_time,
                                      'end_time': update_end_time,
                                      'year': year,
                                      'term': term})
        g.conn.commit()
        time_message = f"Successfully update the timeslot {update_timeslot[0]} on {update_timeslot[1]} from {update_start_time} to {update_end_time}!"
        timeslots = get_timeslot_allocates(year, term)
        params_dict['timeslots'] = timeslots
        return render_template('admin/manage_timeslot.html', 
                              time_message = time_message, **params_dict)
      except Exception as e:
        time_error_message = f"Error from database: {str(e)}"
        return render_template('admin/manage_timeslot.html', 
                               time_error_message = time_error_message, **params_dict)

    if delete_timeslot:
      try:
        query_delete = text("""
                            DELETE FROM Timeslot_allocates
                            WHERE tid = :tid AND days_in_a_week = :days_in_a_week AND year = :year AND term = :term
                            """)
        g.conn.execute(query_delete, {'tid': delete_timeslot[0],
                                      'days_in_a_week': delete_timeslot[1],
                                      'year': year,
                                      'term': term})
        g.conn.commit()
        time_message = f"Successfully delete the timeslot {delete_timeslot[0]} on {delete_timeslot[1]}!"
        timeslots = get_timeslot_allocates(year, term)
        params_dict['timeslots'] = timeslots
        return render_template('admin/manage_timeslot.html', 
                               time_message = time_message, **params_dict)
      except Exception as e:
        time_error_message = f"Error from database: {str(e)}"
        return render_template('admin/manage_timeslot.html', 
                               time_error_message = time_error_message, **params_dict)
  return render_template('admin/manage_timeslot.html', **params_dict)

# Admin manage courses
@app.route('/admin/manage/course/<year>/<term>', methods = ['GET', 'POST'])
def admin_manage_course(year, term):
  admin_id = session.get('admin_id') 
  if not admin_id: 
      return redirect(url_for('admin_login'))

  # time_location_info = get_time_location_info(year, term)
  # time_instructor_info = get_time_instructor_info(year, term)
  # time_instructor_info1 = []
  # time_location_info1 = []
  courses = get_courses(year, term)
  departments = get_departments()
  course_section_info = get_course_section_info(year, term)
  instructor_timeslot_location = get_ins_time_loc_info(year, term)
  occupied_ins_time_loc = get_occupied_ins_time_loc_info(year, term)
  available_ins_time_loc = get_available_ins_time_loc_info(year, term)
  instructors = get_instructors_works_in()
  classrooms = get_classrooms()
  # print(len(occupied_ins_time_loc))
  # print(len(available_ins_time_loc))

  params_dict = { 
    'year': year, 
    'term': term, 
    'admin_id': admin_id,
    'courses': courses,
    'departments': departments,
    'course_section_info': course_section_info,
    # 'time_location_info': time_location_info,
    # 'time_instructor_info': time_instructor_info,
    # 'time_instructor_info1': time_instructor_info1,
    # 'time_location_info1': time_location_info1
    'instructor_timeslot_location': instructor_timeslot_location,
    'occupied_ins_time_loc': occupied_ins_time_loc,
    'available_ins_time_loc': available_ins_time_loc,
    'instructors': instructors,
    'classrooms': classrooms
  }
  
  if request.method == 'POST':
    delete_course = None
    delete_course_section = None
    add_course = request.form.get('add_course')
    add_course_section = request.form.get('add_course_section')
    select_instructor = request.form.get('select_instructor')
   
    for cid in course_section_info.keys():
      if request.form.get(f'delete_{cid}'):
        delete_course = cid
    
    if delete_course:
      try:
        query_delete1 = text("""
                            DELETE FROM Prerequisites
                            WHERE cid_Course = :cid AND year = :year AND term = :term
                            """)
        g.conn.execute(query_delete1, {'cid': delete_course,
                                      'year': year,
                                      'term': term})
        

        query_delete2 = text("""
                             UPDATE prerequisites 
                             SET cid_prerequisite = 'None' 
                             WHERE cid_Prerequisite = :cid AND year = :year AND term = :term
                            """)
        g.conn.execute(query_delete2, {'cid': delete_course,
                                      'year': year,
                                      'term': term})
        
        query_delete3 = text("""
                            DELETE FROM Coordinates
                            WHERE cid = :cid AND year = :year AND term = :term
                            """)
        g.conn.execute(query_delete3, {'cid': delete_course,
                                      'year': year,
                                      'term': term})
        
        query_delete4 = text("""
                            DELETE FROM Offers
                            WHERE cid = :cid AND year = :year AND term = :term
                            """)
        g.conn.execute(query_delete4, {'cid': delete_course,
                                      'year': year,
                                      'term': term})
        
        query_delete5 = text("""
                            DELETE FROM Sec_Schedules_Time
                            WHERE cid = :cid AND year = :year AND term = :term
                            """)
        g.conn.execute(query_delete5, {'cid': delete_course,
                                      'year': year,
                                      'term': term})
        
        query_delete6 = text("""
                            DELETE FROM Sec_Assigns_at
                            WHERE cid = :cid AND year = :year AND term = :term
                            """)
        g.conn.execute(query_delete6, {'cid': delete_course,
                                      'year': year,
                                      'term': term})
        
        query_delete7 = text("""
                            DELETE FROM Sections_Enrolls
                            WHERE cid = :cid AND year = :year AND term = :term
                            """)
        g.conn.execute(query_delete7, {'cid': delete_course,
                                      'year': year,
                                      'term': term})
        
        query_delete8 = text("""
                            DELETE FROM Sections_Waitlists
                            WHERE cid = :cid AND year = :year AND term = :term
                            """)
        g.conn.execute(query_delete8, {'cid': delete_course,
                                      'year': year,
                                      'term': term})
  
        query_delete = text("""
                            DELETE FROM Courses
                            WHERE cid = :cid AND year = :year AND term = :term
                            """)
        g.conn.execute(query_delete, {'cid': delete_course,
                                      'year': year,
                                      'term': term})


        g.conn.commit()

        course_message = f"Successfully delete the course {delete_course}!"
        courses = get_courses(year, term)
        course_section_info = get_course_section_info(year, term)
        instructor_timeslot_location = get_ins_time_loc_info(year, term)
        occupied_ins_time_loc = get_occupied_ins_time_loc_info(year, term)
        available_ins_time_loc = get_available_ins_time_loc_info(year, term)
        params_dict['courses'] = courses
        params_dict['course_section_info'] = course_section_info
        params_dict['instructor_timeslot_location'] = instructor_timeslot_location
        params_dict['occupied_ins_time_loc'] = occupied_ins_time_loc
        params_dict['available_ins_time_loc'] = available_ins_time_loc
        return render_template('admin/manage_course.html', 
                               course_message = course_message, **params_dict)
      except Exception as e:
        course_error_message = f"Error from database: {str(e)}"
        return render_template('admin/manage_course.html', 
                               course_error_message = course_error_message, **params_dict)

    for cid, course in course_section_info.items():
      for sec_num, section in course.items():
        if sec_num not in ['cname', 'credits', 'major', 'academic_level', 'cid_prerequisite', 'course_dept', 'dname', 'course_dept_address']:
          if request.form.get(f'delete_{cid}_{sec_num}'):
            delete_course_section = [cid, sec_num]

    if delete_course_section:
      try:
        query_delete5 = text("""
                            DELETE FROM Sec_Schedules_Time
                            WHERE cid = :cid AND sec_num = :sec_num AND year = :year AND term = :term
                            """)
        g.conn.execute(query_delete5, {'cid': delete_course_section[0],
                                      'sec_num': delete_course_section[1],
                                      'year': year,
                                      'term': term})
        
        query_delete6 = text("""
                            DELETE FROM Sec_Assigns_at
                            WHERE cid = :cid AND sec_num = :sec_num AND year = :year AND term = :term
                            """)
        g.conn.execute(query_delete6, {'cid': delete_course_section[0],
                                      'sec_num': delete_course_section[1],
                                      'year': year,
                                      'term': term})
        
        query_delete7 = text("""
                            DELETE FROM Sections_Enrolls
                            WHERE cid = :cid AND sec_num = :sec_num AND year = :year AND term = :term
                            """)
        g.conn.execute(query_delete7, {'cid': delete_course_section[0],
                                      'sec_num': delete_course_section[1],
                                      'year': year,
                                      'term': term})
        
        query_delete8 = text("""
                            DELETE FROM Sections_Waitlists
                            WHERE cid = :cid AND sec_num = :sec_num AND year = :year AND term = :term
                            """)
        g.conn.execute(query_delete8, {'cid': delete_course_section[0],
                                      'sec_num': delete_course_section[1],
                                      'year': year,
                                      'term': term})
  
        query_delete = text("""
                            DELETE FROM Sections_belongs_teaches
                            WHERE cid = :cid AND sec_num = :sec_num AND year = :year AND term = :term
                            """)
        g.conn.execute(query_delete, {'cid': delete_course_section[0],
                                      'sec_num': delete_course_section[1],
                                      'year': year,
                                      'term': term})


        g.conn.commit()
        course_message = f"Successfully delete the section {delete_course_section[1]} of the course {delete_course_section[0]}!"
        courses = get_courses(year, term)
        course_section_info = get_course_section_info(year, term)
        instructor_timeslot_location = get_ins_time_loc_info(year, term)
        occupied_ins_time_loc = get_occupied_ins_time_loc_info(year, term)
        available_ins_time_loc = get_available_ins_time_loc_info(year, term)
        params_dict['courses'] = courses
        params_dict['course_section_info'] = course_section_info
        params_dict['instructor_timeslot_location'] = instructor_timeslot_location
        params_dict['occupied_ins_time_loc'] = occupied_ins_time_loc
        params_dict['available_ins_time_loc'] = available_ins_time_loc
        return render_template('admin/manage_course.html', 
                               course_message = course_message, **params_dict)
      except Exception as e:
        course_error_message = f"Error from database: {str(e)}"
        return render_template('admin/manage_course.html', 
                               course_error_message = course_error_message, **params_dict)
      
    new_cid = request.form.get('new_cid')
    new_cname = request.form.get('new_cname')
    new_credits = request.form.get('new_credits')
    new_course_major = request.form.get('new_course_major')
    new_academic_level = request.form.get('new_academic_level')
    new_prerequisites = request.form.get('new_prerequisites')
    new_did = request.form.get('new_did')

    if add_course and new_cid and new_cname and new_credits and new_course_major and new_academic_level and new_prerequisites and new_did:
      try:
        query_insert = text("""
                            INSERT INTO Courses (cid, cname, credits, major, academic_level, year, term)
                            VALUES (:cid, :cname, :credits, :major, :academic_level, :year, :term)
                            """)
        g.conn.execute(query_insert, {'cid': new_cid, 
                                      'cname': new_cname,
                                      'credits': new_credits,
                                      'major': new_course_major, 
                                      'academic_level': new_academic_level,
                                      'year': year,
                                      'term': term})
        
        query_insert1 = text("""
                            INSERT INTO Coordinates (cid, year, term)
                            VALUES (:cid, :year, :term)
                            """)
        g.conn.execute(query_insert1, {'cid': new_cid, 
                                      'year': year,
                                      'term': term})
        
        query_insert2 = text("""
                            INSERT INTO Offers (cid, did, year, term)
                            VALUES (:cid, :did, :year, :term)
                            """)
        g.conn.execute(query_insert2, {'cid': new_cid, 
                                      'did': new_did,
                                      'year': year,
                                      'term': term})
        
        query_delete3 = text("""
                             INSERT INTO prerequisites (cid_course, cid_prerequisite, year, term)
                            VALUES (:cid_course, :cid_prerequisite, :year, :term)
                            """)
        g.conn.execute(query_delete3, {'cid_course': new_cid, 
                                       'cid_prerequisite': new_prerequisites,
                                      'year': year,
                                      'term': term})

        g.conn.commit()
        course_message = f"Successfully add a new course {new_cid} offered by department {new_did}!"
        courses = get_courses(year, term)
        course_section_info = get_course_section_info(year, term)
        instructor_timeslot_location = get_ins_time_loc_info(year, term)
        occupied_ins_time_loc = get_occupied_ins_time_loc_info(year, term)
        available_ins_time_loc = get_available_ins_time_loc_info(year, term)
        params_dict['courses'] = courses
        params_dict['course_section_info'] = course_section_info
        params_dict['instructor_timeslot_location'] = instructor_timeslot_location
        params_dict['occupied_ins_time_loc'] = occupied_ins_time_loc
        params_dict['available_ins_time_loc'] = available_ins_time_loc
        
        return render_template('admin/manage_course.html', 
                               course_message = course_message, **params_dict)
      except Exception as e:
        course_error_message = f"Error from database: {str(e)}"
        return render_template('admin/manage_course.html', 
                               course_error_message = course_error_message, **params_dict)
    
    
    # occupied_time_location_instructor
    # [section['instructor']['id'], section['instructor']['name'], section['instructor']['email'],
    #  section['address']['bname'], section['address']['sec_address'], section['address']['room_num'], section['address']['capacity'],
    #  day, time['tid'], time['start_time'], time['end_time']]

    # time_location_info
    # [bname, address, room_num, capacity, days_in_a_week, tid, start_time, end_time]
    # time_instructor_info
    # [id, name, email, days_in_a_week, tid, start_time, end_time]
    
    
    new_sec_cid = request.form.get('new_sec_cid')
    new_sec_num = request.form.get('new_sec_num')
    new_sec_max_capacity = request.form.get('new_sec_max_capacity')
    new_sec_instruction_mode = request.form.get('new_sec_instruction_mode')
    new_sec_instructor_time_loc = request.form.get('new_sec_instructor_time_loc')
    new_sec_instructor_time_loc = list(map(str.strip, new_sec_instructor_time_loc.split(','))) 
    
    
    # instructor_timeslot_location
    # ins_time_loc.append([id, name, email, days_in_a_week, tid, start_time, end_time, address 7 , bname 8, room_num 9, capacity])
    # occupied_ins_time_loc
    # available_ins_time_loc
    
    if add_course_section and new_sec_cid and new_sec_num and new_sec_instruction_mode and new_sec_max_capacity and new_sec_instructor_time_loc:
      try:
        query_insert = text("""
                            INSERT INTO Sections_Belongs_Teaches (sec_num, instruction_mode, id, cid, year, term, max_capacity, actual_enrollment)
                            VALUES (:sec_num, :instruction_mode, :id, :cid, :year, :term, :max_capacity, :actual_enrollment)
                            """)
        g.conn.execute(query_insert, {'sec_num': new_sec_num, 
                                      'instruction_mode': new_sec_instruction_mode, 
                                      'id': new_sec_instructor_time_loc[0], 
                                      'cid': new_sec_cid, 
                                      'year': year,
                                      'term': term,
                                      'max_capacity': new_sec_max_capacity, 
                                      'actual_enrollment': 0})
          
        query_insert1 = text("""
                            INSERT INTO Sec_Schedules_Time (sec_num, cid, tid, days_in_a_week, year, term)
                            VALUES (:sec_num, :cid, :tid, :days_in_a_week, :year, :term)
                            """)
        g.conn.execute(query_insert1, {'sec_num': new_sec_num, 
                                      'cid': new_sec_cid, 
                                      'tid': new_sec_instructor_time_loc[4], 
                                      'days_in_a_week': new_sec_instructor_time_loc[3], 
                                      'year': year,
                                      'term': term})
        
        query_insert2 = text("""
                            INSERT INTO Sec_Assigns_at (sec_num, room_num, cid, address, year, term)
                            VALUES (:sec_num, :room_num, :cid, :address, :year, :term)
                            """)
        g.conn.execute(query_insert2, {'sec_num': new_sec_num,
                                       'room_num': new_sec_instructor_time_loc[9], 
                                      'cid': new_sec_cid,  
                                      'address': new_sec_instructor_time_loc[7], 
                                      'year': year,
                                      'term': term})
        

        g.conn.commit()
        course_message = f"Successfully add a new section {new_sec_num} of course {new_sec_cid}!"
        courses = get_courses(year, term)
        departments = get_departments()
        course_section_info = get_course_section_info(year, term)
        instructor_timeslot_location = get_ins_time_loc_info(year, term)
        occupied_ins_time_loc0 = occupied_ins_time_loc
        occupied_ins_time_loc = get_occupied_ins_time_loc_info(year, term)
        # print(occupied_ins_time_loc0 == occupied_ins_time_loc)
        print(len(occupied_ins_time_loc0))
        print(len(occupied_ins_time_loc))
        # for i in occupied_ins_time_loc:
        #   for j in occupied_ins_time_loc0:
        #     if j != i:
        #       print(i)
        available_ins_time_loc0 = available_ins_time_loc
        available_ins_time_loc = get_available_ins_time_loc_info(year, term)
        # print(available_ins_time_loc0 == available_ins_time_loc)
        print(len(available_ins_time_loc0))
        print(len(available_ins_time_loc))
        # for i in available_ins_time_loc:
        #   for j in available_ins_time_loc0:
        #     if j != i:
        #       print(i)
        params_dict['courses'] = courses
        params_dict['departments'] = departments
        params_dict['course_section_info'] = course_section_info
        params_dict['instructor_timeslot_location'] = instructor_timeslot_location
        params_dict['occupied_ins_time_loc'] = occupied_ins_time_loc
        params_dict['available_ins_time_loc'] = available_ins_time_loc
        return render_template('admin/manage_course.html', 
                               course_message = course_message, **params_dict)
      except Exception as e:
        course_error_message = f"Error from database: {str(e)}"
        return render_template('admin/manage_course.html', 
                               course_error_message = course_error_message, **params_dict)
  return render_template('admin/manage_course.html', **params_dict)

# Admin manage student
@app.route('/admin/manage/student/<year>/<term>', methods = ['GET', 'POST'])
def admin_manage_student(year, term):
  admin_id = session.get('admin_id') 
  if not admin_id: 
      return redirect(url_for('admin_login'))
  
  enrolls = get_enrolls_info(year, term)
  waitlists = get_waitlists_info(year, term)
  course_section_info = get_course_section_info(year, term)
  params_dict = { 
    'year': year, 
    'term': term, 
    'enrolls': enrolls,
    'waitlists': waitlists,
    'course_section_info': course_section_info
  }

  if request.method == 'POST':
    delete_enrollment = None
    update_waitlist = None
    delete_waitlist = None

    for (sid, cid, sec_num) in enrolls.keys():
      if request.form.get(f"delete_{sid}_{cid}_{sec_num}"):
        delete_enrollment = [sid, cid, sec_num]
    
    for (sid, cid, sec_num) in waitlists.keys():
      if request.form.get(f"update_waitlist_{sid}_{cid}_{sec_num}"):
        update_waitlist = [sid, cid, sec_num]
    
    for (sid, cid, sec_num) in waitlists.keys():
      if request.form.get(f"delete_waitlist_{sid}_{cid}_{sec_num}"):
        delete_waitlist = [sid, cid, sec_num]

    if delete_enrollment:
      try:
        query_delete = text("""
                            DELETE FROM Sections_Enrolls
                            WHERE sid = :sid AND cid = :cid AND sec_num = :sec_num AND year = :year AND term = :term
                            """)
        g.conn.execute(query_delete, {'sid': delete_enrollment[0],
                                      'cid': delete_enrollment[1],
                                      'sec_num': delete_enrollment[2],
                                      'year': year,
                                      'term': term})
        g.conn.commit()
        student_message = f"Successfully delete the enrollment for student {delete_enrollment[0]} in course {delete_enrollment[1]} section {delete_enrollment[2]}!"
        enrolls = get_enrolls_info(year, term)
        waitlists = get_waitlists_info(year, term)
        course_section_info = get_course_section_info(year, term)
        params_dict['enrolls'] = enrolls
        params_dict['waitlists'] = waitlists
        params_dict['course_section_info'] = course_section_info
        return render_template('admin/manage_student.html', 
                               student_message = student_message, **params_dict)
      except Exception as e:
        student_error_message = f"Error from database: {str(e)}"
        return render_template('admin/manage_student.html', 
                               student_error_message = student_error_message, **params_dict)

    if delete_waitlist:
      try:
        query_delete = text("""
                            DELETE FROM Sections_Waitlists
                            WHERE sid = :sid AND cid = :cid AND sec_num = :sec_num AND year = :year AND term = :term
                            """)
        g.conn.execute(query_delete, {'sid': delete_waitlist[0],
                                      'cid': delete_waitlist[1],
                                      'sec_num': delete_waitlist[2],
                                      'year': year,
                                      'term': term})
        g.conn.commit()
        student_message = f"Successfully delete the waitlist for student {delete_waitlist[0]} in course {delete_waitlist[1]} section {delete_waitlist[2]}!"
        
        enrolls = get_enrolls_info(year, term)
        waitlists = get_waitlists_info(year, term)
        course_section_info = get_course_section_info(year, term)
        params_dict['enrolls'] = enrolls
        params_dict['waitlists'] = waitlists
        params_dict['course_section_info'] = course_section_info
        return render_template('admin/manage_student.html', 
                               student_message = student_message, **params_dict)
      except Exception as e:
        student_error_message = f"Error from database: {str(e)}"
        return render_template('admin/manage_student.html', 
                               student_error_message = student_error_message, **params_dict)
      
    if update_waitlist:
      try:
        query_insert = text("""
                            DELETE FROM Sections_Waitlists
                            WHERE sid = :sid AND cid = :cid AND sec_num = :sec_num AND year = :year AND term = :term
                            """)
        g.conn.execute(query_insert, {'sec_num': update_waitlist[2],
                                      'sid': update_waitlist[0],
                                      'cid': update_waitlist[1],
                                      'year': year,
                                      'term': term})
        g.conn.commit()

        query_insert = text("""
                            INSERT INTO Sections_Enrolls (sec_num, sid, cid, grade, year, term)
                            VALUES (:sec_num, :sid, :cid, :grade, :year, :term)
                            """)
        g.conn.execute(query_insert, {'sec_num': update_waitlist[2],
                                      'sid': update_waitlist[0],
                                      'cid': update_waitlist[1],
                                      'grade': 'NA',
                                      'year': year,
                                      'term': term})
        g.conn.commit()
        student_message = f"Successfully enroll student {update_waitlist[0]} in course {update_waitlist[1]} section {update_waitlist[2]}!"
        
        enrolls = get_enrolls_info(year, term)
        waitlists = get_waitlists_info(year, term)
        course_section_info = get_course_section_info(year, term)
        params_dict['enrolls'] = enrolls
        params_dict['waitlists'] = waitlists
        params_dict['course_section_info'] = course_section_info
        return render_template('admin/manage_student.html', 
                               student_message = student_message, **params_dict)
      except Exception as e:
        student_error_message = f"Error from database: {str(e)}"
        return render_template('admin/manage_student.html', 
                               student_error_message = student_error_message, **params_dict)
      
  return render_template('admin/manage_student.html', **params_dict)
   

# Instructor dashboard
@app.route('/instructor/dashboard',  methods = ['GET', 'POST'])
def instructor_dashboard():
  instructor_id = session.get('instructor_id') 
  if not instructor_id: 
      return redirect(url_for('instructor_login'))

  query = text("SELECT year, term FROM Calendar ORDER BY year DESC, term DESC")
  cursor = g.conn.execute(query)
  
  year_terms = {}
  results = cursor.mappings().all()
  for result in results:
    year = result["year"]
    term = result["term"]
    if year not in year_terms:
      year_terms[year] = []
    year_terms[year].append(term) 
  cursor.close()

  if request.method == 'GET':
    selected_year_term = request.args.get('year_terms')
    # print(selected_year_term) 
    if selected_year_term:
      year, term = selected_year_term.split(',')
      # print(f"Year: {year}, Term: {term}") 
      return redirect(url_for('instructor_manage', year = year, term = term))
  
  
  return render_template('instructor/dashboard.html', 
                         year_terms = year_terms, instructor_id = instructor_id)

# Instructor manage
@app.route('/instructor/manage/<year>/<term>', methods = ['GET', 'POST'])
def instructor_manage(year, term):
  instructor_id = session.get('instructor_id')
  if not instructor_id:
    return redirect(url_for('instructor_login'))
  
  params_dict = {
    'year': year,
    'term': term,
    'instructor_id': instructor_id,
  }
  return render_template('instructor/manage.html', **params_dict)

# Instructor manage calendar
@app.route('/instructor/manage/calendar/<year>/<term>', methods = ['GET', 'POST'])
def instructor_manage_calendar(year, term):
  instructor_id = session.get('instructor_id') 
  if not instructor_id: 
      return redirect(url_for('instructor_login'))
  
  ins_course = get_ins_course_info(year, term, instructor_id)
  holidays = get_holidays(year, term)
  ddls = get_calendar(year, term)

  params_dict = { 
    'year': year, 
    'term': term, 
    'holidays': holidays, 
    'ddls': ddls,  
    'instructor_id': instructor_id,
    'ins_course': ins_course
  }

  return render_template('instructor/manage_calendar.html', **params_dict)

# Instructor manage student
@app.route('/instructor/manage/student/<year>/<term>', methods = ['GET', 'POST'])
def instructor_manage_student(year, term):
  instructor_id = session.get('instructor_id') 
  if not instructor_id: 
      return redirect(url_for('instructor_login'))
  
  ins_course = get_ins_course_info(year, term, instructor_id)
  enrolls = get_enrolls_info(year, term)
  enrolls_dict = {}
  for (sid, cid, sec_num), enroll in enrolls.items():
    if (cid, sec_num) not in enrolls_dict:
      enrolls_dict[(cid, sec_num)]= {}
    if sid not in enrolls_dict[(cid, sec_num)]:
      enrolls_dict[(cid, sec_num)][sid] = enrolls[sid, cid, sec_num]
  # print(enrolls_dict)

  course_section_info = get_course_section_info(year, term)
  cid_sec = []

  for cid, course in ins_course.items():
    for sec_num, section in course.items():
      if sec_num  not in ['cname', 'credits', 'major', 'academic_level', 'cid_prerequisite', 'course_dept', 'dname', 'course_dept_address']:
         cid_sec.append((cid, sec_num))
  # print(cid_sec)
  
  params_dict = { 
    'year': year, 
    'term': term, 
    'enrolls': enrolls,
    'course_section_info': course_section_info, 
    'instructor_id': instructor_id,
    'ins_course': ins_course,
    'cid_sec': cid_sec,
    'enrolls_dict': enrolls_dict
  }


  if request.method == 'POST':
    update_grade = None

    for (sid, cid, sec_num) in enrolls.keys():
      if request.form.get(f"update_{sid}_{cid}_{sec_num}"):
        update_grade = [sid, cid, sec_num]
    
    if update_grade:
      new_grade = request.form.get(f'new_grade_{update_grade[0]}_{update_grade[1]}_{update_grade[2]}')
    # print(new_grade)
    
    if update_grade:
      try:
        query_update = text("""
                            UPDATE Sections_Enrolls
                            SET grade = :grade
                            WHERE sid = :sid AND cid = :cid AND sec_num = :sec_num AND year = :year AND term = :term
                            """)
        g.conn.execute(query_update, {'sid': update_grade[0],
                                      'cid': update_grade[1],
                                      'sec_num': update_grade[2],
                                      'grade': new_grade,
                                      'year': year,
                                      'term': term})
        g.conn.commit()
        student_message = f"Successfully update grade {new_grade} for student {update_grade[0]} in course {update_grade[1]} section {update_grade[2]}!"
        
        ins_course = get_ins_course_info(year, term, instructor_id)
        enrolls = get_enrolls_info(year, term)
        enrolls_dict = {}
        for (sid, cid, sec_num), enroll in enrolls.items():
          if (cid, sec_num) not in enrolls_dict:
            enrolls_dict[(cid, sec_num)]= {}
          if sid not in enrolls_dict[(cid, sec_num)]:
            enrolls_dict[(cid, sec_num)][sid] = enrolls[sid, cid, sec_num]
        # print(enrolls_dict)

        course_section_info = get_course_section_info(year, term)
        cid_sec = []

        for cid, course in ins_course.items():
          for sec_num, section in course.items():
            if sec_num  not in ['cname', 'credits', 'major', 'academic_level', 'cid_prerequisite', 'course_dept', 'dname', 'course_dept_address']:
              cid_sec.append((cid, sec_num))

        params_dict['enrolls'] = enrolls
        params_dict['ins_course'] = ins_course
        params_dict['enrolls_dict'] = enrolls_dict
        params_dict['course_section_info'] = course_section_info
        params_dict['cid_sec'] = cid_sec
        
        return render_template('instructor/manage_student.html', 
                               student_message = student_message, **params_dict)
      except Exception as e:
        student_error_message = f"Error from database: {str(e)}"
        return render_template('instructor/manage_student.html', 
                               student_error_message = student_error_message, **params_dict)  
  
  return render_template('instructor/manage_student.html', **params_dict)


# Student dashboard
@app.route('/student/dashboard',  methods = ['GET', 'POST'])
def student_dashboard():
  student_id = session.get('student_id') 
  if not student_id: 
      return redirect(url_for('student_login'))

  query = text("SELECT year, term FROM Calendar ORDER BY year DESC, term DESC")
  cursor = g.conn.execute(query)
  
  year_terms = {}
  results = cursor.mappings().all()
  for result in results:
    year = result["year"]
    term = result["term"]
    if year not in year_terms:
      year_terms[year] = []
    year_terms[year].append(term) 
  cursor.close()

  if request.method == 'GET':
    selected_year_term = request.args.get('year_terms')
    # print(selected_year_term) 
    if selected_year_term:
      year, term = selected_year_term.split(',')
      # print(f"Year: {year}, Term: {term}") 
      return redirect(url_for('student_manage', year = year, term = term))
  
  
  return render_template('student/dashboard.html', 
                         year_terms = year_terms, student_id = student_id)

# Student manage
@app.route('/student/manage/<year>/<term>', methods = ['GET', 'POST'])
def student_manage(year, term):
  student_id = session.get('student_id')
  if not student_id:
    return redirect(url_for('student_login'))
  
  params_dict = {
    'year': year,
    'term': term,
    'student_id': student_id,
  }
  return render_template('student/manage.html', **params_dict)

# Student manage calendar
@app.route('/student/manage/calendar/<year>/<term>', methods = ['GET', 'POST'])
def student_manage_calendar(year, term):
  student_id = session.get('student_id') 
  if not student_id: 
      return redirect(url_for('student_login'))
  
  holidays = get_holidays(year, term)
  ddls = get_calendar(year, term)
  enrolls = get_enrolls_info(year, term)
  wl = get_waitlists_info(year, term)
  stu_enroll = get_stu_enroll_info(year, term, student_id)
  stu_wl = get_stu_waitlist_info(year, term, student_id)
  course_section_info = get_course_section_info(year, term)
  current_date = datetime.now().date()
  days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
  weekly_courses = {day: [] for day in days_of_week}

  # print(stu_enroll)
  for cid, enroll in stu_enroll.items():
    for sec_num, section in enroll.items():
      for day, time in section['time'].items():
        # print(day)
        if day in weekly_courses:
          weekly_courses[day].append({
            'cid': cid,
            'sec_num': sec_num,
            'section': section
          })
  print(weekly_courses)

  params_dict = { 
    'year': year, 
    'term': term, 
    'holidays': holidays, 
    'ddls': ddls,  
    'student_id': student_id,
    'stu_enroll': stu_enroll,
    'enrolls': enrolls,
    'wl': wl,
    'stu_wl': stu_wl,
    'course_section_info': course_section_info,
    'current_date': current_date,
    'weekly_courses': weekly_courses
  }


  return render_template('student/manage_calendar.html', **params_dict)

# Student manage enrollment
@app.route('/student/manage/enrollment/<year>/<term>', methods = ['GET', 'POST'])
def student_manage_enrollment(year, term):
  student_id = session.get('student_id') 
  if not student_id: 
      return redirect(url_for('student_login'))
  
  holidays = get_holidays(year, term)
  ddls = get_calendar(year, term)
  enrolls = get_enrolls_info(year, term)
  wl = get_waitlists_info(year, term)
  stu_enroll = get_stu_enroll_info(year, term, student_id)
  stu_wl = get_stu_waitlist_info(year, term, student_id)
  course_section_info = get_course_section_info(year, term)
  current_date = datetime.now().date()

  params_dict = { 
    'year': year, 
    'term': term, 
    'holidays': holidays, 
    'ddls': ddls,  
    'student_id': student_id,
    'stu_enroll': stu_enroll,
    'enrolls': enrolls,
    'wl': wl,
    'stu_wl': stu_wl,
    'course_section_info': course_section_info,
    'current_date': current_date
  }

  if request.method == 'POST':
    delete_enrollment = None
    delete_waitlist = None

    for (sid, cid, sec_num) in enrolls.keys():
      if request.form.get(f"delete_{sid}_{cid}_{sec_num}"):
        delete_enrollment = [sid, cid, sec_num]

    for (sid, cid, sec_num) in wl.keys():
      if request.form.get(f"delete_wl_{sid}_{cid}_{sec_num}"):
        delete_waitlist = [sid, cid, sec_num]

    if delete_enrollment:
      try:
        if current_date > ddls[0]['drop_ddl']:
          student_error_message = f"Cannot drop the course since it pasts drop deadline {ddls[0]['drop_ddl']}!"
          return render_template('student/manage_enrollment.html', 
                                 student_error_message = student_error_message, **params_dict)
        
        query_delete = text("""
                            DELETE FROM Sections_Enrolls
                            WHERE sid = :sid AND cid = :cid AND sec_num = :sec_num AND year = :year AND term = :term
                            """)
        g.conn.execute(query_delete, {'sid': delete_enrollment[0],
                                      'cid': delete_enrollment[1],
                                      'sec_num': delete_enrollment[2],
                                      'year': year,
                                      'term': term})
      
        
        g.conn.commit()
        student_message = f"Successfully delete the enrollment in course {delete_enrollment[1]} section {delete_enrollment[2]}!"
        enrolls = get_enrolls_info(year, term)
        wl = get_waitlists_info(year, term)
        stu_enroll = get_stu_enroll_info(year, term, student_id)
        stu_wl = get_stu_waitlist_info(year, term, student_id)
        course_section_info = get_course_section_info(year, term)

        params_dict['enrolls'] = enrolls
        params_dict['wl'] = wl
        params_dict['stu_enroll'] = stu_enroll
        params_dict['stu_wl'] = stu_wl
        params_dict['course_section_info'] = course_section_info

        return render_template('student/manage_enrollment.html', 
                               student_message = student_message, **params_dict)
      except Exception as e:
        student_error_message = f"Error from database: {str(e)}"
        return render_template('student/manage_enrollment.html', 
                               student_error_message = student_error_message, **params_dict)

    if delete_waitlist:
      try:
        query_delete = text("""
                            DELETE FROM Sections_Waitlists
                            WHERE sid = :sid AND cid = :cid AND sec_num = :sec_num AND year = :year AND term = :term
                            """)
        g.conn.execute(query_delete, {'sid': delete_waitlist[0],
                                      'cid': delete_waitlist[1],
                                      'sec_num': delete_waitlist[2],
                                      'year': year,
                                      'term': term})
        g.conn.commit()
        student_message = f"Successfully delete the waitlist in course {delete_waitlist[1]} section {delete_waitlist[2]}!"
        
        enrolls = get_enrolls_info(year, term)
        wl = get_waitlists_info(year, term)
        stu_enroll = get_stu_enroll_info(year, term, student_id)
        stu_wl = get_stu_waitlist_info(year, term, student_id)
        course_section_info = get_course_section_info(year, term)

        params_dict['enrolls'] = enrolls
        params_dict['wl'] = wl
        params_dict['stu_enroll'] = stu_enroll
        params_dict['stu_wl'] = stu_wl
        params_dict['course_section_info'] = course_section_info

        return render_template('student/manage_enrollment.html', 
                               student_message = student_message, **params_dict)
      except Exception as e:
        student_error_message = f"Error from database: {str(e)}"
        return render_template('student/manage_enrollment.html', 
                               student_error_message = student_error_message, **params_dict)
      
  return render_template('student/manage_enrollment.html', **params_dict)


# Student manage course
@app.route('/student/manage/courseSearch/<year>/<term>', methods = ['GET', 'POST'])
def student_manage_courseSearch(year, term):
  student_id = session.get('student_id') 
  if not student_id: 
      return redirect(url_for('student_login'))
  
  enrolls = get_enrolls_info(year, term)
  wl = get_waitlists_info(year, term)
  stu_enroll = get_stu_enroll_info(year, term, student_id)
  stu_enroll0 = get_stu_enroll_info0(student_id)
  stu_wl = get_stu_waitlist_info(year, term, student_id)
  ddls = get_calendar(year, term)
  courses = get_courses(year, term)
  departments = get_departments()
  course_section_info = get_course_section_info(year, term)
  instructor_timeslot_location = get_ins_time_loc_info(year, term)
  occupied_ins_time_loc = get_occupied_ins_time_loc_info(year, term)
  available_ins_time_loc = get_available_ins_time_loc_info(year, term)
  instructors = get_instructors_works_in()
  classrooms = get_classrooms()
  course_section_info_details = get_course_section_info_details(year, term)
  where = ""
  course_section_info_filter = get_course_section_info_filter(year, term, where)
  current_date = datetime.now().date()
  students = get_students()

  params_dict = { 
    'year': year, 
    'term': term, 
    'student_id': student_id,
    'stu_enroll': stu_enroll,
    'stu_enroll0': stu_enroll,
    'enrolls': enrolls,
    'wl': wl,
    'stu_wl': stu_wl,
    'ddls': ddls,
    'courses': courses,
    'departments': departments,
    'course_section_info': course_section_info,
    'instructor_timeslot_location': instructor_timeslot_location,
    'occupied_ins_time_loc': occupied_ins_time_loc,
    'available_ins_time_loc': available_ins_time_loc,
    'instructors': instructors,
    'classrooms': classrooms,
    'course_section_info_details': course_section_info_details,
    'course_section_info_filter': course_section_info_filter,
    'students': students
  }
  
  if request.method == 'POST':
    search_course = request.form.get('search_course')
    if search_course:
      try:
        new_cid = request.form.get('new_cid')
        new_cname = request.form.get('new_cname')
        new_credits = request.form.get('new_credits')
        new_course_major = request.form.get('new_course_major')
        new_sec_days_in_a_week = request.form.get('new_sec_days_in_a_week')
        new_sec_instruction_mode = request.form.get('new_sec_instruction_mode')
        new_academic_level = request.form.get('new_academic_level')
        new_did = request.form.get('new_did')
        new_id = request.form.get('new_id')

        filters = []
        if new_cid:
            filters.append(f"cid = '{new_cid}'")
        if new_cname:
            filters.append(f"cname = '{new_cname}'")
        if new_course_major:
            filters.append(f"major = '{new_course_major}'")
        if new_academic_level:
            filters.append(f"academic_level = '{new_academic_level}'")
        if new_sec_instruction_mode:
            filters.append(f"instruction_mode = '{new_sec_instruction_mode}'")
        if new_sec_days_in_a_week:
            filters.append(f"days_in_a_week = '{new_sec_days_in_a_week}'")
        if new_did:
            filters.append(f"course_dept = '{new_did}'")
        if new_credits:
            filters.append(f"credits = {new_credits}")
        if new_id:
            filters.append(f"id = '{new_id}'")

        if filters:
          where = " AND " + " AND ".join(str(item) for item in filters)
          mesg = " AND ".join(str(item) for item in filters)
          course_message = f"Search results for {mesg}:"
        else:
          where = ""
          course_message = f"No filters submit, show all available courses:"


        course_section_info_filter = get_course_section_info_filter(year, term, where)
        # print(course_section_info_filter)

        params_dict['course_section_info_filter'] = course_section_info_filter

        return render_template('student/manage_courseSearch.html', 
                               course_message = course_message, **params_dict)
      except Exception as e:
        course_error_message = f"Error from database: {str(e)}"
        return render_template('student/manage_courseSearch.html', 
                               course_error_message = course_error_message, **params_dict)


    for cid, course in course_section_info.items():
      for sec_num, section in course.items():
        if sec_num not in ['cname', 'credits', 'major', 'academic_level', 'cid_prerequisite', 'course_dept', 'dname', 'course_dept_address']:
          if request.form.get(f'add_{cid}_{sec_num}'):
            add_course = [cid, sec_num]

    if add_course:
      try:
        if current_date > ddls[0]['add_waitlist_ddl']:
          course_error_message = f"Cannot add the course since it pasts add/waitlist deadline {ddls[0]['add_waitlist_ddl']}!"
          return render_template('student/manage_courseSearch.html', 
                                 course_error_message = course_error_message, **params_dict)
        
      
        if add_course[0] in stu_enroll0:
          # print('TRUE')
          course_error_message = f"Already taken same course {add_course[0]} in previous term!"
          return render_template('student/manage_courseSearch.html', 
                                 course_error_message = course_error_message, **params_dict)

        for cid, enroll in stu_enroll.items():
          if add_course[0] == cid:
            course_error_message = f"Cannot enroll in the section {add_course[1]} since it already enrolled in one section of the course {add_course[0]}!"
            return render_template('student/manage_courseSearch.html', 
                                  course_error_message = course_error_message, **params_dict)
          
        if students[student_id]['major'] != courses[add_course[0]]['major'] or students[student_id]['academic_level'] != courses[add_course[0]]['academic_level']:
          course_error_message = f"Cannot enroll in the section {add_course[1]} of course {add_course[0]} since you didn't belong to major {courses[add_course[0]]['major']} or in academic_level {courses[add_course[0]]['academic_level']}!"
          return render_template('student/manage_courseSearch.html', 
                                 course_error_message = course_error_message, **params_dict)
        
        # print(courses[add_course[0]]['prerequisites'] not in stu_enroll)
        # print(courses[add_course[0]]['prerequisites'])

        if courses[add_course[0]]['prerequisites'] not in stu_enroll0:
          course_error_message = f"Cannot enroll in the section {add_course[1]} of course {add_course[0]} since you need to take the prerequisite {courses[add_course[0]]['prerequisites']} first!"
          return render_template('student/manage_courseSearch.html', 
                                 course_error_message = course_error_message, **params_dict)
        
        if course_section_info[add_course[0]][add_course[1]]['actual_enrollment'] >= course_section_info[add_course[0]][add_course[1]]['max_capacity']:
          query_insert = text("""
                              INSERT INTO Sections_Waitlists (sec_num, sid, cid, join_date, year, term)
                              VALUES (:sec_num, :sid, :cid, :join_date, :year, :term)
                              """)
          g.conn.execute(query_insert, {'sec_num': add_course[1],
                                        'sid': student_id,
                                        'cid': add_course[0],
                                        'join_date': current_date,
                                        'year': year,
                                        'term': term})
          
          g.conn.commit()
          course_error_message = f"Cannot enroll in the section {add_course[1]} of course {add_course[0]} since its already full, add you to waitlist!"
          return render_template('student/manage_courseSearch.html', 
                                 course_error_message = course_error_message, **params_dict)

        
        query_insert = text("""
                            INSERT INTO Sections_Enrolls (sec_num, sid, cid, grade, year, term)
                            VALUES (:sec_num, :sid, :cid, :grade, :year, :term)
                            """)
        g.conn.execute(query_insert, {'sec_num': add_course[1],
                                      'sid': student_id,
                                      'cid': add_course[0],
                                      'grade': 'NA',
                                      'year': year,
                                      'term': term})
        
        g.conn.commit()
        course_message = f"Successfully enroll student {student_id} in course {add_course[0]} section {add_course[1]}!"

        
        
        enrolls = get_enrolls_info(year, term)
        wl = get_waitlists_info(year, term)
        stu_enroll = get_stu_enroll_info(year, term, student_id)
        stu_wl = get_stu_waitlist_info(year, term, student_id)
        courses = get_courses(year, term)
        departments = get_departments()
        course_section_info = get_course_section_info(year, term)
        instructor_timeslot_location = get_ins_time_loc_info(year, term)
        occupied_ins_time_loc = get_occupied_ins_time_loc_info(year, term)
        available_ins_time_loc = get_available_ins_time_loc_info(year, term)
        instructors = get_instructors_works_in()
        classrooms = get_classrooms()
        course_section_info_details = get_course_section_info_details(year, term)
        course_section_info_filter = get_course_section_info_filter(year, term, where)
        students = get_students()
        stu_enroll0 = get_stu_enroll_info0(student_id)

        params_dict['enrolls'] = enrolls
        params_dict['wl'] = wl
        params_dict['stu_enroll'] = stu_enroll
        params_dict['stu_enroll0'] = stu_enroll0
        params_dict['stu_wl'] = stu_wl
        params_dict['courses'] = courses
        params_dict['course_section_info'] = course_section_info
        params_dict['instructor_timeslot_location'] = instructor_timeslot_location
        params_dict['occupied_ins_time_loc'] = occupied_ins_time_loc
        params_dict['available_ins_time_loc'] = available_ins_time_loc
        params_dict['departments'] = departments
        params_dict['instructors'] = instructors
        params_dict['classrooms'] = classrooms
        params_dict['course_section_info_details'] = course_section_info_details
        params_dict['course_section_info_filter'] = course_section_info_filter
        params_dict['students'] = students

        return render_template('student/manage_courseSearch.html', 
                               course_message = course_message, **params_dict)
      except Exception as e:
        course_error_message = f"Error from database: {str(e)}"
        return render_template('student/manage_courseSearch.html', 
                               course_error_message = course_error_message, **params_dict)
  return render_template('student/manage_courseSearch.html', **params_dict)


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python3 server.py

    Show the help text using:

        python3 server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
