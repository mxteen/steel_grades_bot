import sqlite3
import pandas as pd
import os

def init_database():
    # Check if the Excel file exists
    if not os.path.exists('steel_grades.xlsx'):
        print("Error: steel_grades.xlsx file not found!")
        print("Please create an Excel file with the following columns:")
        print("steel_grade, specification, C_min, C_max, Si_min, Si_max, Mn_min, Mn_max, S_min, S_max, P_min, P_max, Cr_min, Cr_max, Ni_min, Ni_max, Cu_min, Cu_max, Mo_min, Mo_max, V_min, V_max, Nb_min, Nb_max, Ti_min, Ti_max, N_min, N_max, W_min, W_max, B_min, B_max, Co_min, Co_max, Al_min, Al_max")
        return False

    # Connect to the database
    conn = sqlite3.connect('steel_database.db')
    cursor = conn.cursor()

    # Create the steel_grades table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS steel_grades (
        steel_grade TEXT,
        specification TEXT,
        C_min REAL,
        C_max REAL,
        Si_min REAL,
        Si_max REAL,
        Mn_min REAL,
        Mn_max REAL,
        S_min REAL,
        S_max REAL,
        P_min REAL,
        P_max REAL,
        Cr_min REAL,
        Cr_max REAL,
        Ni_min REAL,
        Ni_max REAL,
        Cu_min REAL,
        Cu_max REAL,
        Mo_min REAL,
        Mo_max REAL,
        V_min REAL,
        V_max REAL,
        Nb_min REAL,
        Nb_max REAL,
        Ti_min REAL,
        Ti_max REAL,
        N_min REAL,
        N_max REAL,
        W_min REAL,
        W_max REAL,
        B_min REAL,
        B_max REAL,
        Co_min REAL,
        Co_max REAL,
        Al_min REAL,
        Al_max REAL
    )
    ''')

    # Read the Excel file
    try:
        df = pd.read_excel('steel_grades.xlsx')
        print('df.columns', df.columns)

        # Check if all required columns are present
        required_columns = [
            'steel_grade', 'specification',
            'C_min', 'C_max', 'Si_min', 'Si_max', 'Mn_min', 'Mn_max',
            'S_min', 'S_max', 'P_min', 'P_max', 'Cr_min', 'Cr_max',
            'Ni_min', 'Ni_max', 'Cu_min', 'Cu_max', 'Mo_min', 'Mo_max',
            'V_min', 'V_max', 'Nb_min', 'Nb_max', 'Ti_min', 'Ti_max',
            'N_min', 'N_max', 'W_min', 'W_max', 'B_min', 'B_max',
            'Co_min', 'Co_max', 'Al_min', 'Al_max'
        ]

        missing_columns = [col for col in required_columns if col not in df.columns]
        print('missing_columns', missing_columns)
        if len(missing_columns) > 0:
            print(f"Error: The following columns are missing in the Excel file: {', '.join(missing_columns)}")
            return False

        # Clear existing data
        cursor.execute("DELETE FROM steel_grades")

        # Insert data from Excel
        for _, row in df.iterrows():
            placeholders = ', '.join(['?' for _ in range(len(required_columns))])
            cursor.execute(
                f"INSERT INTO steel_grades ({', '.join(required_columns)}) VALUES ({placeholders})",
                [row[col] for col in required_columns]
            )

        conn.commit()
        print(f"Database updated successfully with {len(df)} steel grades from steel_grades.xlsx")
        return True

    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    init_database()