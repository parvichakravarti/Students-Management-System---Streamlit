import streamlit as st
import pandas as pd

st.set_page_config(page_title="Student Grade Management System", page_icon="🎓", layout="wide")

# ---------------- TEACHER LOGIN ----------------
st.title("🎓 Student Grade Management System")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def login(username, password):
    # Simple demo login (you can later replace with a database or Firebase)
    if username == "teacher" and password == "12345":
        st.session_state.authenticated = True
        st.success("✅ Login successful!")
    else:
        st.error("❌ Invalid username or password.")

if not st.session_state.authenticated:
    st.subheader("🔐 Teacher Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        login(username.strip(), password.strip())
    st.stop()  # stop rest of app until login

# ---------------- MAIN APP ----------------

st.success("Welcome, Teacher 👩‍🏫")
st.caption("Manage grades, check reports, and track class performance.")

if "student_grades" not in st.session_state:
    st.session_state.student_grades = {}

# Helper Functions
def grade_category(avg):
    if avg >= 90:
        return "A"
    elif avg >= 75:
        return "B"
    elif avg >= 60:
        return "C"
    elif avg >= 40:
        return "D"
    else:
        return "Fail"

def pass_or_fail(marks):
    return "PASS" if all(mark >= 40 for mark in marks.values()) else "FAIL"

def add_student(name, marks):
    total = sum(marks.values())
    avg = total / len(marks)
    category = grade_category(avg)
    result = pass_or_fail(marks)
    st.session_state.student_grades[name] = {
        "marks": marks,
        "total": total,
        "average": avg,
        "category": category,
        "result": result
    }
    st.success(f"✅ Added {name} ({result}) with total {total} and grade {category}")

def update_student(name, marks):
    if name in st.session_state.student_grades:
        total = sum(marks.values())
        avg = total / len(marks)
        category = grade_category(avg)
        result = pass_or_fail(marks)
        st.session_state.student_grades[name] = {
            "marks": marks,
            "total": total,
            "average": avg,
            "category": category,
            "result": result
        }
        st.info(f"✏️ Updated {name}'s record ({result})")
    else:
        st.warning(f"⚠️ {name} not found")

def delete_student(name):
    if name in st.session_state.student_grades:
        del st.session_state.student_grades[name]
        st.success(f"🗑️ Deleted {name}")
    else:
        st.warning(f"⚠️ {name} not found")

def search_student(name):
    if name in st.session_state.student_grades:
        data = st.session_state.student_grades[name]
        st.success(f"🎯 {name}'s Details:")
        st.json(data)
    else:
        st.warning(f"⚠️ {name} not found")

def calculate_statistics():
    if not st.session_state.student_grades:
        return None
    averages = [info["average"] for info in st.session_state.student_grades.values()]
    stats = {
        "Average Score": sum(averages) / len(averages),
        "Highest Average": max(averages),
        "Lowest Average": min(averages)
    }
    return stats

# Subjects
subjects = ["Science", "Maths", "English", "Marathi", "Social Science"]

# Sidebar Navigation
menu = st.sidebar.radio(
    "📋 Menu",
    ["Add Student", "Update Student", "Delete Student", "Search Student", "View Students", "Class Statistics", "Grade Analysis Reports", "About", "Logout"]
)

# ---------------- MENU SECTIONS ----------------

if menu == "Add Student":
    st.subheader("➕ Add New Student")
    name = st.text_input("Enter Student Name")
    marks = {}
    for subject in subjects:
        marks[subject] = st.number_input(f"{subject} Marks", min_value=0, max_value=100, step=1)
    if st.button("Add"):
        if name.strip():
            add_student(name.strip().title(), marks)
        else:
            st.warning("Please enter a valid name.")

elif menu == "Update Student":
    st.subheader("✏️ Update Student")
    name = st.text_input("Enter Student Name")
    marks = {}
    for subject in subjects:
        marks[subject] = st.number_input(f"Enter new marks for {subject}", min_value=0, max_value=100, step=1, key=f"update_{subject}")
    if st.button("Update"):
        update_student(name.strip().title(), marks)

elif menu == "Delete Student":
    st.subheader("🗑️ Delete Student")
    name = st.text_input("Enter Student Name to Delete")
    if st.button("Delete"):
        delete_student(name.strip().title())

elif menu == "Search Student":
    st.subheader("🔍 Search Student")
    name = st.text_input("Enter Student Name to Search")
    if st.button("Search"):
        search_student(name.strip().title())

elif menu == "View Students":
    st.subheader("📚 All Student Records")
    if st.session_state.student_grades:
        data = []
        for name, info in st.session_state.student_grades.items():
            row = {"Name": name, **info["marks"], "Total": info["total"], "Average": round(info["average"], 2),
                   "Grade": info["category"], "Result": info["result"]}
            data.append(row)
        df = pd.DataFrame(data)
        df = df.sort_values(by="Average", ascending=False)
        st.dataframe(df, use_container_width=True)

        # Pass/Fail summary
        pass_count = df["Result"].value_counts().get("PASS", 0)
        fail_count = df["Result"].value_counts().get("FAIL", 0)
        st.markdown(f"### ✅ Pass: {pass_count} ❌ Fail: {fail_count}")

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download CSV", csv, "student_grades.csv", "text/csv")
    else:
        st.info("No students added yet.")

elif menu == "Class Statistics":
    st.subheader("📊 Class Performance Overview")
    stats = calculate_statistics()
    if stats:
        col1, col2, col3 = st.columns(3)
        col1.metric("Average Score", f"{stats['Average Score']:.2f}")
        col2.metric("Highest Average", f"{stats['Highest Average']:.2f}")
        col3.metric("Lowest Average", f"{stats['Lowest Average']:.2f}")

        df = pd.DataFrame([
            {"Name": name, "Average": info["average"], "Grade": info["category"], "Result": info["result"]}
            for name, info in st.session_state.student_grades.items()
        ])
        st.bar_chart(df.set_index("Name")["Average"])

        st.write("### Grade Distribution")
        st.bar_chart(df["Grade"].value_counts())
    else:
        st.warning("No data available yet.")

elif menu == "Grade Analysis Reports":
    st.subheader("📈 Detailed Grade Analysis Reports")
    if st.session_state.student_grades:
        df = pd.DataFrame([
            {"Name": name, **info["marks"], "Average": info["average"], "Grade": info["category"], "Result": info["result"]}
            for name, info in st.session_state.student_grades.items()
        ])

        # Subject-wise average
        st.markdown("### 📘 Subject-wise Average Scores")
        subject_averages = {subject: df[subject].mean() for subject in subjects}
        st.bar_chart(pd.Series(subject_averages, name="Average Marks"))

        # Grade distribution
        st.markdown("### 🏷️ Grade Distribution")
        grade_counts = df["Grade"].value_counts()
        st.bar_chart(grade_counts)

        # Pass/Fail ratio
        st.markdown("### ⚖️ Overall Pass/Fail Ratio")
        pass_fail = df["Result"].value_counts()
        st.bar_chart(pass_fail)

        # Top performers
        st.markdown("### 🥇 Top 5 Performers")
        top_students = df.sort_values(by="Average", ascending=False).head(5)
        st.dataframe(top_students[["Name", "Average", "Grade", "Result"]], use_container_width=True)
    else:
        st.info("No records to analyze yet.")

elif menu == "About":
    st.subheader("ℹ️ About This Project")
    st.write("""
    This **Student Grade Management System** allows teachers to securely manage, track, and analyze student performance.

    ### Features:
    - 🔐 Teacher login for secure access  
    - ➕ Add, update, delete, or search student records  
    - 🧮 Automatic total, average, grade, and pass/fail result  
    - 📊 Class statistics with visual insights  
    - 📈 Grade analysis reports (subject-wise averages, grade and pass ratios)  
    - 📥 Export all data as CSV  

    ### Future Improvements:
    - Store data in SQLite or Firebase  
    - Multi-teacher accounts  
    - Generate printable report cards  
    """)

elif menu == "Logout":
    st.session_state.authenticated = False
    st.success("✅ Logged out successfully! Please log in again.")
    st.rerun()