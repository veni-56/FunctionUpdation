from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.core.window import Window

import sqlite3
import pandas as pd
import os

# Database setup
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

class FunctionApp(App):

    def build(self):
        self.title = "Function Data Collection App"
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # GridLayout for form inputs
        self.grid = GridLayout(cols=2, spacing=10, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))

        self.inputs = {}  # store references to TextInput widgets

        fields = ["S.No (for update only)", "Function Date", "Function Name", "Organised By", 
                  "Resource Person", "Time", "Total Participants", "Photo Path", 
                  "Welcome Address", "Chief Guest Address", "Vote of Thanks"]

        for field in fields:
            self.grid.add_widget(Label(text=field))
            ti = TextInput(multiline=False, size_hint_y=None, height=30)
            self.inputs[field] = ti
            self.grid.add_widget(ti)

        # ScrollView for form
        scroll = ScrollView(size_hint=(1, 0.6))
        scroll.add_widget(self.grid)
        layout.add_widget(scroll)

        # Buttons layout
        btn_layout = GridLayout(cols=3, spacing=10, size_hint_y=None, height=40)
        btn_submit = Button(text="Submit", background_color=(0,1,0,1))
        btn_submit.bind(on_press=self.submit_data)
        btn_update = Button(text="Update", background_color=(1,0.5,0,1))
        btn_update.bind(on_press=self.update_data)
        btn_report = Button(text="Generate Report", background_color=(0,0,1,1))
        btn_report.bind(on_press=self.generate_report)

        btn_layout.add_widget(btn_submit)
        btn_layout.add_widget(btn_update)
        btn_layout.add_widget(btn_report)
        layout.add_widget(btn_layout)

        # Bottom buttons
        bottom_layout = GridLayout(cols=3, spacing=10, size_hint_y=None, height=40)
        btn_view = Button(text="View Records", background_color=(0.5,0,0.5,1))
        btn_view.bind(on_press=self.view_data)
        btn_upload = Button(text="Upload Photo", background_color=(0,0.5,0.5,1))
        btn_upload.bind(on_press=self.upload_photo)
        btn_close = Button(text="Close App", background_color=(1,0,0,1))
        btn_close.bind(on_press=self.close_app)

        bottom_layout.add_widget(btn_view)
        bottom_layout.add_widget(btn_upload)
        bottom_layout.add_widget(btn_close)

        layout.add_widget(bottom_layout)

        return layout

    # --- Button Functions ---
    def upload_photo(self, instance):
        chooser = FileChooserIconView(path=os.getcwd())
        popup = Popup(title="Select Photo", content=chooser, size_hint=(0.9, 0.9))
        def select_photo(instance_btn):
            selection = chooser.selection
            if selection:
                self.inputs["Photo Path"].text = selection[0]
                popup.dismiss()
        chooser.bind(on_submit=lambda chooser, selection, touch: select_photo(None))
        popup.open()

    def submit_data(self, instance):
        cursor.execute("""
        INSERT INTO functions (function_date, function_name, organised_by, resource_person, time, 
                               total_participants, photo_path, welcome_address, chief_guest_address, vote_of_thanks)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.inputs["Function Date"].text,
            self.inputs["Function Name"].text,
            self.inputs["Organised By"].text,
            self.inputs["Resource Person"].text,
            self.inputs["Time"].text,
            self.inputs["Total Participants"].text,
            self.inputs["Photo Path"].text,
            self.inputs["Welcome Address"].text,
            self.inputs["Chief Guest Address"].text,
            self.inputs["Vote of Thanks"].text
        ))
        conn.commit()
        popup = Popup(title="Success", content=Label(text="Data Submitted Successfully!"), size_hint=(0.5,0.3))
        popup.open()

    def update_data(self, instance):
        try:
            sno = int(self.inputs["S.No (for update only)"].text)
            cursor.execute("""
            UPDATE functions SET function_date=?, function_name=?, organised_by=?, resource_person=?,
                                 time=?, total_participants=?, photo_path=?, welcome_address=?, 
                                 chief_guest_address=?, vote_of_thanks=? WHERE sno=?
            """, (
                self.inputs["Function Date"].text,
                self.inputs["Function Name"].text,
                self.inputs["Organised By"].text,
                self.inputs["Resource Person"].text,
                self.inputs["Time"].text,
                self.inputs["Total Participants"].text,
                self.inputs["Photo Path"].text,
                self.inputs["Welcome Address"].text,
                self.inputs["Chief Guest Address"].text,
                self.inputs["Vote of Thanks"].text,
                sno
            ))
            conn.commit()
            popup = Popup(title="Success", content=Label(text="Data Updated Successfully!"), size_hint=(0.5,0.3))
            popup.open()
        except Exception as e:
            popup = Popup(title="Error", content=Label(text=str(e)), size_hint=(0.5,0.3))
            popup.open()

    def generate_report(self, instance):
        file_path = r"D:\function_report.xlsx"
        df = pd.read_sql_query("SELECT * FROM functions", conn)
        df.to_excel(file_path, index=False)
        popup = Popup(title="Report Generated", content=Label(text=f"Report saved at:\n{file_path}"), size_hint=(0.6,0.4))
        popup.open()

    def view_data(self, instance):
        rows = cursor.execute("SELECT * FROM functions").fetchall()
        content = "\n".join([str(row) for row in rows])
        popup = Popup(title="All Records", content=Label(text=content), size_hint=(0.9,0.9))
        popup.open()

    def close_app(self, instance):
        App.get_running_app().stop()
        Window.close()

if __name__ == "__main__":
    FunctionApp().run()
