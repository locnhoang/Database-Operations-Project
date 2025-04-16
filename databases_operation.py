import mysql.connector
# Connects user to the login 
con = mysql.connector.connect(host="localhost", user="", password="", database="Company")
# Creates cursor to execute SQL queries
cursor = con.cursor()
# Connect to database named Company
cursor.execute('USE Company')
# Helper functions
def update_emp_record(Employee_ssn, field, new_value):
    try:
        # Update query with parameterized inputs
        update_query = f'UPDATE Employee SET {field} = %s WHERE Ssn = %s'
        cursor.execute(update_query, (new_value, Employee_ssn))
        print(f'{field} updated successfully.')
    except mysql.connector.Error as err:
        print(f'Error updating {field}:', err)
#1 
def add_employee():
    Fname = input('Enter the first name of the employee you would like to add: ')
    Minit = input('Enter their middle initial: ')
    Lname = input('Enter their last name: ')
    Ssn = input('Enter their SSN: ')
    Bdate = input('Enter their Birthdate as YYYY-MM-DD: ')
    Address = input('Enter their address:' )
    Sex = input('Enter their sex (M/F): ')
    Salary = input("Enter their salary: ")
    Super_ssn = input("Enter their supervisor's SSN: ")
    Dno = input("Enter their department number: ")
    try:
        cursor.execute("""
                       INSERT INTO EMPLOYEE (Fname, Minit, Lname, Ssn, Bdate, Address, Sex, Salary, Super_ssn, Dno) 
                       VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
                       (Fname, Minit, Lname, Ssn, Bdate, Address, Sex, Salary, Super_ssn if Super_ssn else None, Dno))
        # check for integrity error
    except mysql.connector.IntegrityError:
        print('\nError: Integrity violated!')
        con.rollback() # rolls back any changes if insertion fails
        menu()
        #check for datatype integrity
    except mysql.connector.DataError:
        print('\nError: Incorrect Data type or length entered')
        con.rollback()
        menu()
    # If all is well, commit insert query, and employee is added, return to menu
    con.commit()
    print("Employee added into Company successfully!")
    menu()
#2
def view_employee():
    Employee_ssn = input('Enter Employee SSN: ')
    # Parameterized queries to prevent SQL injection
    query = 'SELECT * FROM Employee WHERE Ssn = %s'
    query1 = 'SELECT CONCAT(F.Fname, " ", F.Lname) FROM Employee F JOIN Employee S ON S.Super_ssn = F.Ssn WHERE S.Ssn = %s'
    query2 = 'SELECT Dname FROM DEPARTMENT JOIN Employee ON Dnumber = Dno WHERE Ssn = %s'
    query3 = 'SELECT D.Dependent_name FROM DEPENDENT D JOIN Employee E ON D.ESsn = E.Ssn WHERE E.Ssn = %s'

    try:
        # Execute and fetch employee information
        cursor.execute(query, (Employee_ssn,))
        employee_info = cursor.fetchone()
        if employee_info:
            print('Employee Information:', employee_info)
        else:
            print('No employee found with that SSN.')
            return
        # Execute and fetch supervisor name
        cursor.execute(query1, (Employee_ssn,))
        supervisor = cursor.fetchone()
        if supervisor:
            print('Supervisor Name:', supervisor[0])
        else:
            print('No supervisor found for this employee.')

        # Execute and fetch department name
        cursor.execute(query2, (Employee_ssn,))
        department = cursor.fetchone()
        if department:
            print('Department Name:', department[0])
        else:
            print('No department found for this employee.')

        # Execute and fetch dependents
        cursor.execute(query3, (Employee_ssn,))
        dependents = cursor.fetchall()
        if dependents:
            dependent_names = [dep[0] for dep in dependents]
            print('Dependents:', ', '.join(dependent_names))
        else:
            print('No dependents found for this employee.')

    except mysql.connector.Error as err:
        print('Error:', err)
    finally:
        menu()

#3
def modify_employee():
    Employee_ssn = input('Enter Employee SSN: ')
    cursor.execute('START TRANSACTION')
    # Parameterized query to lock the employee record for updates
    query = 'SELECT * FROM Employee WHERE Ssn = %s FOR UPDATE'
    cursor.execute(query, (Employee_ssn,))
    employee_info = cursor.fetchone()
    if employee_info:
        print("Employee Info: ", employee_info)  # Prints out employee details
        keepUpdating = True
        # List of fields that can be updated
        valid_fields = ["Address", "Sex", "Salary", "Super_ssn", "Dno"]
        while keepUpdating:
            choice = input("What do you wish to change? (Address, Sex, Salary, Super_ssn, Dno, Exit to Exit): ")
            if choice in valid_fields:
                updated = input("Enter the new value for " + choice + ": ")
                update_emp_record(Employee_ssn, choice, updated)  # Calls helper function to update record   
            elif choice == "Exit":
                keepUpdating = False
            else:
                print("Invalid field. Please enter a valid field to update.")
        # Commit changes after modification
        con.commit()
    else:
        print("No employee found with that SSN.")
    # Rolls back any locking done to the record after we finish modifying it
    con.rollback()
    menu()

#4
def remove_employee():
    Employee_ssn = input('Enter Employee SSN: ')
    cursor.execute("START TRANSACTION")  # Locks records

    # Parameterized query to lock the record
    query = 'SELECT * FROM Employee WHERE Ssn = %s FOR UPDATE'
    cursor.execute(query, (Employee_ssn,))
    employee_info = cursor.fetchone()
    if employee_info:
        print('Employee info:', employee_info)
        confirm = input("Do you wish to delete this employee? (Y/N): ")
        if confirm.upper() == 'N':
            con.rollback()
            menu()
        elif confirm.upper() == 'Y':
            # Delete query with parameterized input
            query2 = 'DELETE FROM Employee WHERE Ssn = %s'
            try:
                cursor.execute(query2, (Employee_ssn,))
                con.commit()
                print('Employee deleted successfully.')
            except mysql.connector.IntegrityError as e:
                print('\nError: Integrity Violated. This employee has dependents or other associated records.')
                print('Details:', e)
                con.rollback()
        else:
            print('Invalid input. Aborting operation.')
            con.rollback()
    else:
        print('No employee found with that SSN.')
        con.rollback()
    menu()

#5
def add_dependent():
    Employee_ssn = input("Enter Employee SSN: ")
    cursor.execute("START TRANSACTION")  # Locks record
    
    # Query to check if the employee exists
    employee_query = 'SELECT * FROM Employee WHERE Ssn = %s'
    cursor.execute(employee_query, (Employee_ssn,))
    employee = cursor.fetchone()
    
    if not employee:
        print('Invalid SSN: No employee found with this SSN.')
        con.rollback()
        menu()
        return  # Exit function if no valid SSN is found

    # Query to fetch current dependents
    query = 'SELECT Dependent_name, Sex, Bdate, Relationship FROM DEPENDENT WHERE Essn = %s'
    cursor.execute(query, (Employee_ssn,))
    dependents = cursor.fetchall()
    
    if dependents:
        print('Current dependents:')
        for dep in dependents:
            print(dep)
    else:
        print('No dependents found for this employee. You can add a new dependent.')

    # Ask for user's input on new dependent information
    Dependent_name = input("What is your dependent's name: ")
    Sex = input("What is your dependent's sex (M/F): ")
    Bdate = input("What is your dependent's Birthdate (YYYY-MM-DD): ")
    Relationship = input("What is the dependent's relationship to you (Daughter/Son/Spouse): ")

    # Insert new dependent with parameterized query
    try:
        insert_query = 'INSERT INTO DEPENDENT (Essn, Dependent_name, Sex, Bdate, Relationship) VALUES (%s, %s, %s, %s, %s)'
        cursor.execute(insert_query, (Employee_ssn, Dependent_name, Sex, Bdate, Relationship))
        con.commit()
        print("Dependent added successfully.")
    except mysql.connector.Error as err:
        print('Error:', err)
        con.rollback()
    
    menu()

#6
def remove_dependent():
    Employee_ssn = input("Enter Employee SSN: ")
    cursor.execute("START TRANSACTION")
    # Parameterized query to check if the employee has dependents
    query = 'SELECT * FROM DEPENDENT JOIN EMPLOYEE ON Essn = Ssn WHERE Ssn = %s'
    cursor.execute(query, (Employee_ssn,))
    dependents = cursor.fetchall()
    if dependents:
        print('Dependent info:')
        for dep in dependents:
            print(dep)
        Dependent_name = input("Enter the name of the dependent you wish to delete: ")
        # Parameterized query to delete the specified dependent
        query_delete = 'DELETE FROM DEPENDENT WHERE Essn = %s AND Dependent_name = %s'
        try:
            cursor.execute(query_delete, (Employee_ssn, Dependent_name))
            if cursor.rowcount > 0:
                con.commit()
                print("Dependent deleted successfully.")
            else:
                print("No dependent found with the provided name.")
                con.rollback()
        except mysql.connector.Error as err:
            print('Error:', err)
            con.rollback()
    else:
        print('No dependents found for this employee or invalid SSN.')
        con.rollback()
    menu()

#7
def add_department():
    DName = input("Enter the name of the department you wish to add: ")
    try:
        DNumber = int(input("Enter the number of the department you wish to add: "))
    except ValueError:
        print("Error: Department number must be an integer.")
        menu()
        return
    MSsn = input("Enter the manager's SSN: ")
    MDate = input("Enter the manager's start date as YYYY-MM-DD: ")
    try:
        # Takes user's inputs and inserts them into the table
        cursor.execute("INSERT INTO Department (Dname, Dnumber, Mgr_ssn, Mgr_start_date) VALUES (%s, %s, %s, %s)",
                       (DName, DNumber, MSsn, MDate))
        con.commit()
        print("Department added successfully.")
    except mysql.connector.IntegrityError as e:  # Checks for referential integrity issues
        print("\nError: Integrity Violated. Make sure the manager's SSN exists in the Employee table.")
        print("Details:", e)
        con.rollback()
    except mysql.connector.Error as e:
        print("\nDatabase Error:", e)
        con.rollback()

    menu()

#8
def view_department():
    DNum = input("Enter the number of the department you want to view: ")
    try:
        # Parameterized queries to prevent SQL injection
        query1 = "SELECT Dname FROM Department WHERE Dnumber = %s"
        query2 = "SELECT Fname, Minit, Lname FROM Employee JOIN Department ON Ssn = Mgr_ssn WHERE Dnumber = %s"
        query3 = "SELECT Dlocation FROM DEPT_LOCATIONS DL JOIN Department D ON DL.Dnumber = D.Dnumber WHERE D.Dnumber = %s"
        # Execute and print department name
        cursor.execute(query1, (DNum,))
        department_name = cursor.fetchone()
        if department_name:
            print("Department Name:", department_name[0])
        else:
            print("No department found with this number.")
            menu()
            return
        # Execute and print manager's name
        cursor.execute(query2, (DNum,))
        manager_name = cursor.fetchone()
        if manager_name:
            print("Manager's Name:", f"{manager_name[0]} {manager_name[1]} {manager_name[2]}")
        else:
            print("No manager found for this department.")
        # Execute and print department locations
        cursor.execute(query3, (DNum,))
        locations = cursor.fetchall()
        if locations:
            print("Department's Locations:", ', '.join([loc[0] for loc in locations]))
        else:
            print("No locations found for this department.")
    except mysql.connector.Error as e:
        print("\nDatabase Error:", e)
    menu()

    
#9
def delete_department():
    DNum = input("Enter the number of the department you wish to delete: ")
    cursor.execute("START TRANSACTION")  # Starts transaction and locks records as needed
    # Query with parameterized input for safety
    query = 'SELECT * FROM DEPARTMENT WHERE Dnumber = %s FOR UPDATE'
    cursor.execute(query, (DNum,))
    department_info = cursor.fetchone()
    if department_info:
        print("Department Information:", department_info)
    else:
        print("No department found with this number.")
        con.rollback()  #Roll back transaction if no department is found
        menu()
        return  #Exit the function to prevent further execution
    confirm = input("Are you sure you wish to delete this department? (Y/N) ")
    if confirm.upper() == 'N':  # Ensure case insensitivity
        con.rollback()  # Rollback all changes if the user cancels the action
        print("Operation cancelled.")
        menu()
        return  #Exit the function to prevent further execution
    #Corrected delete query with parameterized input for safety
    query2 = 'DELETE FROM DEPARTMENT WHERE Dnumber = %s'
    try:
        cursor.execute(query2, (DNum,))
        con.commit()  #Commit transaction if deletion is successful
        print("Department deleted.")
    except mysql.connector.IntegrityError:  # Checks for referential integrity
        print("\nError: Integrity Violated. This department has dependencies. Please remove them first before deletion.")
        con.rollback()  # Roll back changes if referential integrity is violated
    menu()

def add_dep_location():
    DNum = input("Enter the number of the department you want to add a location to: ")
    try:
        cursor.execute('START TRANSACTION')  # Start transaction and lock records as needed
        # Use parameterized query to avoid SQL injection
        query = 'SELECT * FROM DEPARTMENT WHERE Dnumber = %s FOR UPDATE'
        cursor.execute(query, (DNum,))
        department_info = cursor.fetchone()
        if department_info:
            print("Department Information:", department_info)
        else:
            print("No department found with this number.")
            con.rollback()  # Rollback transaction if department not found
            menu()
            return  # Exit function to prevent further execution
        # Retrieve and print existing department locations
        query2 = 'SELECT Dlocation FROM DEPT_LOCATIONS WHERE Dnumber = %s'
        cursor.execute(query2, (DNum,))
        locations = cursor.fetchall()
        if locations:
            print("Department's Current Locations:", ', '.join([loc[0] for loc in locations]))
        else:
            print("This department has no existing locations.")
        # Get new location input
        location = input("Enter the new location you wish to add: ")
        # Insert new location into DEPT_LOCATIONS table
        cursor.execute('INSERT INTO DEPT_LOCATIONS (Dnumber, Dlocation) VALUES (%s, %s)', (DNum, location))
        con.commit()  # Commit transaction if insertion is successful
        print("Department location added successfully!")
    except mysql.connector.Error as e:
        print("\nDatabase Error:", e)
        con.rollback()  # Rollback transaction in case of an error
    menu()

def remove_dep_location():
    DNum = input("Enter the number of the department you want to remove a location from: ")
    try:
        cursor.execute('START TRANSACTION')  # Starts transaction and locks records as needed
        # Parameterized query to safely fetch department
        query = 'SELECT * FROM DEPARTMENT WHERE Dnumber = %s FOR UPDATE'
        cursor.execute(query, (DNum,))
        department_info = cursor.fetchone()
        if department_info:
            print("Department Information:", department_info)
        else:
            print("No department found with this number.")
            con.rollback()  # Rollback transaction if no department found
            menu()
            return  # Exit function to prevent further execution
        # Fetch and display current department locations
        query2 = 'SELECT Dlocation FROM DEPT_LOCATIONS WHERE Dnumber = %s'
        cursor.execute(query2, (DNum,))
        locations = cursor.fetchall()
        if locations:
            print("Department's Current Locations:", ', '.join([loc[0] for loc in locations]))
        else:
            print("No locations found for this department.")
            con.rollback()
            menu()
            return  # Exit function if no locations are found
        # Get location input to delete
        location = input("Enter the location you wish to delete: ")
        # Parameterized query to safely delete the specified location
        query3 = 'DELETE FROM DEPT_LOCATIONS WHERE Dlocation = %s AND Dnumber = %s'
        cursor.execute(query3, (location, DNum))
        # Check if the delete operation affected any rows
        if cursor.rowcount > 0:
            con.commit()  # Commit changes if deletion was successful
            print("Department location deleted successfully!")
        else:
            print("No matching location found for deletion.")
            con.rollback()  # Rollback transaction if no rows were affected
    except mysql.connector.Error as e:
        print("\nDatabase Error:", e)
        con.rollback()  # Rollback transaction in case of an error

    menu()

    
def menu():
    print('Select an option:')
    print('1: Add New Employee')
    print('2: View Employee')
    print('3: Modify Employee')
    print('4: Remove Employee')
    print('5: Add New Dependent')
    print('6: Remove Dependent')
    print('7: Add New Department')
    print('8: View Department')
    print('9: Remove Department')
    print('10: Add Department Location')
    print('11: Remove Department Location')
    print('12: Exit')
    choice = int(input("Enter your choice (0-12):"))
    match choice: 
        case 0: exit(0)
        case 1: add_employee()
        case 2: view_employee()
        case 3: modify_employee()
        case 4: remove_employee()
        case 5: add_dependent()
        case 6: remove_dependent()
        case 7: add_department()
        case 8: view_department()
        case 9: delete_department()
        case 10: add_dep_location()
        case 11: remove_dep_location()
        case 12: exit()
        
if __name__ == '__main__':
    print("Welcome to Project 2: Company Database Operations!")
    menu()
