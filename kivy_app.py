from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.filechooser import FileChooserIconView

import sqlite3
import pandas as pd
import os

# ------------------ Database ------------------
conn = sqlite3.connect("functions.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS functions (
    sno INTEGER PRIMARY KEY AUTOINCREMENT,
    function_date TEXT,
    function_name TEXT,
    organised_by TEXT,
    resource_person TEXT,
    time TEXT,
    total_participants INTEGER,
    photo_path TEXT,
    welcome_address TEXT,
    chief_guest_address TEXT,
    vote_of_thanks TEXT
)
""")
conn.commit()

# ------------------ Helper Functions ------------------
def show_message(title, message):
    popup = Popup(title=title,
                  content=Label(text=message),
                  size_hint=(None, None), size=(400, 200))
    popup.open()

# ------------------ Main App GUI ------------------
class FunctionApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 5

        # Dictionary to store inputs
        self.inputs = {}

        # Fields
        fields = [
            ("S.No (for update only)", "sno"),
            ("Function Date", "date"),
            ("Function Name", "name"),
            ("Organised By", "organiser"),
            ("Resource Person", "resource"),
            ("Time", "time"),
            ("Total Participants", "participants"),
            ("Photo Path", "photo"),
            ("Welcome Address", "welcome"),
            ("Chief Guest Address", "chief"),
            ("Vote of Thanks", "vote")
        ]

        for label_text, key in fields:
            box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            box.add_widget(Label(text=label_text, size_hint_x=0.4))
            ti = TextInput(multiline=False)
            box.add_widget(ti)
            self.inputs[key] = ti
            self.add_widget(box)
        
        # Photo upload button
        upload_btn = Button(text="Upload Photo", size_hint_y=None, height=40)
        upload_btn.bind(on_press=self.upload_photo)
        self.add_widget(upload_btn)

        # Buttons
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=5)
        submit_btn = Button(text="Submit", background_color=(0,1,0,1))
        submit_btn.bind(on_press=self.submit_data)
        update_btn = Button(text="Update", background_color=(1,0.65,0,1))
        update_btn.bind(on_press=self.update_data)
        report_btn = Button(text="Generate Report", background_color=(0,0,1,1))
        report_btn.bind(on_press=self.generate_report)
        view_btn = Button(text="View Records", background_color=(0.5,0,0.5,1))
        view_btn.bind(on_press=self.view_data)

        btn_layout.add_widget(submit_btn)
        btn_layout.add_widget(update_btn)
        btn_layout.add_widget(report_btn)
        btn_layout.add_widget(view_btn)

        self.add_widget(btn_layout)

    # ------------------ Functions ------------------
    def upload_photo(self, instance):
        content = FileChooserIconView()
        popup = Popup(title="Select Photo", content=content, size_hint=(0.9, 0.9))
        def select_file(instance, selection):
            if selection:
                self.inputs['photo'].text = selection[0]
                popup.dismiss()
        content.bind(on_submit=select_file)
        popup.open()

    def submit_data(self, instance):
        try:
            cursor.execute("""
            INSERT INTO functions (function_date, function_name, organised_by, resource_person, time, 
                                   total_participants, photo_path, welcome_address, chief_guest_address, vote_of_thanks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.inputs['date'].text,
                self.inputs['name'].text,
                self.inputs['organiser'].text,
                self.inputs['resource'].text,
                self.inputs['time'].text,
                self.inputs['participants'].text,
                self.inputs['photo'].text,
                self.inputs['welcome'].text,
                self.inputs['chief'].text,
                self.inputs['vote'].text
            ))
            conn.commit()
            show_message("Success", "Data Submitted Successfully!")
        except Exception as e:
            show_message("Error", str(e))

    def update_data(self, instance):
        try:
            sno = int(self.inputs['sno'].text)
            cursor.execute("""
            UPDATE functions SET function_date=?, function_name=?, organised_by=?, resource_person=?,
                                 time=?, total_participants=?, photo_path=?, welcome_address=?, 
                                 chief_guest_address=?, vote_of_thanks=? WHERE sno=?
            """, (
                self.inputs['date'].text,
                self.inputs['name'].text,
                self.inputs['organiser'].text,
                self.inputs['resource'].text,
                self.inputs['time'].text,
                self.inputs['participants'].text,
                self.inputs['photo'].text,
                self.inputs['welcome'].text,
                self.inputs['chief'].text,
                self.inputs['vote'].text,
                sno
            ))
            conn.commit()
            show_message("Success", "Data Updated Successfully!")
        except Exception as e:
            show_message("Error", str(e))

    def generate_report(self, instance):
        try:
            file_path = os.path.join("D:\\", "function_report.xlsx")
            df = pd.read_sql_query("SELECT * FROM functions", conn)
            df.to_excel(file_path, index=False)
            show_message("Report", f"Report generated successfully at:\n{file_path}")
        except Exception as e:
            show_message("Error", str(e))

    def view_data(self, instance):
        popup = Popup(title="All Records", size_hint=(0.9, 0.9))
        layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        scroll = ScrollView(size_hint=(1,1))
        scroll.add_widget(layout)

        cursor.execute("SELECT * FROM functions")
        rows = cursor.fetchall()
        for row in rows:
            layout.add_widget(Label(text=str(row), size_hint_y=None, height=40))

        popup.content = scroll
        popup.open()

# ------------------ Run App ------------------
class FunctionAppMain(App):
    def build(self):
        return FunctionApp()

if __name__ == "__main__":
    FunctionAppMain().run()
