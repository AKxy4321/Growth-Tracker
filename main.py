import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView


# File to store goals and progress
STORAGE_FILE = "growth_tracker.json"


class GrowthTrackerApp(App):
    def build(self):
        # Load stored data
        self.data = self.load_data()

        # Main layout
        self.layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Add Goal Section
        self.add_goal_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=50)
        self.goal_input = TextInput(hint_text="Enter a new goal", size_hint_x=0.7)
        self.add_goal_layout.add_widget(self.goal_input)

        add_goal_btn = Button(text="Add Goal", size_hint_x=0.3)
        add_goal_btn.bind(on_press=self.add_goal)
        self.add_goal_layout.add_widget(add_goal_btn)

        self.layout.add_widget(self.add_goal_layout)

        # Progress Header
        self.progress_label = Label(
            text="Progress",
            size_hint_y=None,
            height=30,
            halign="center",
            valign="center",
        )
        self.progress_label.bind(size=self.progress_label.setter("text_size"))
        self.layout.add_widget(self.progress_label)

        self.progress_header = BoxLayout(orientation="horizontal", size_hint_y=None, height=30)
        self.progress_header.add_widget(Label(text="Goals", size_hint_x=0.4))  
        for progress_label in ["20%", "40%", "60%", "80%", "100%"]:
            self.progress_header.add_widget(Label(text=progress_label, size_hint_x=0.12))
        self.progress_header.add_widget(Label(text="Actions", size_hint_x=0.2))
        self.layout.add_widget(self.progress_header)

        # Goals List
        scroll_view = ScrollView(size_hint=(1, 1))  # ScrollView to allow scrolling when many goals are added
        self.goals_layout = BoxLayout(
            orientation="vertical",  # Stack items vertically
            spacing=10,
            size_hint_y=None,  # Let the height be dynamically set
        )
        self.goals_layout.bind(minimum_height=self.goals_layout.setter("height"))  # Update height dynamically

        scroll_view.add_widget(self.goals_layout)
        self.layout.add_widget(scroll_view)

        # Populate existing goals
        for goal_data in reversed(self.data.get("goals", [])):
            self.add_goal_widget(goal_data["goal"], goal_data["progress"])

        # Clear All Goals Button
        clear_all_btn = Button(text="Clear All Goals", size_hint_y=None, height=50)
        clear_all_btn.bind(on_press=self.clear_all_goals)
        self.layout.add_widget(clear_all_btn)

        # Save Button
        save_btn = Button(text="Save All Progress", size_hint_y=None, height=50)
        save_btn.bind(on_press=self.save_data)
        self.layout.add_widget(save_btn)

        return self.layout

    def add_goal(self, instance):
        """Add a new goal to the UI and data."""
        goal_text = self.goal_input.text.strip()
        if goal_text:  # Only add non-empty goals
            self.add_goal_widget(goal_text, [False] * 5, add_to_top=True)
            self.data["goals"].insert(0, {"goal": goal_text, "progress": [False] * 5})
            self.goal_input.text = ""

    def add_goal_widget(self, goal_text, progress, add_to_top=False):
        """Add a goal widget with progress checkboxes."""
        goal_box = BoxLayout(orientation="horizontal", size_hint_y=None, height=50)

        # Goal Label
        goal_label = Label(text=goal_text, size_hint_x=0.4, halign="left", valign="middle")
        goal_label.bind(size=goal_label.setter("text_size"))
        goal_box.add_widget(goal_label)

        # Progress Checkboxes
        checkboxes = []
        for i in range(5):
            checkbox = CheckBox(size_hint_x=0.12)
            checkbox.active = progress[i]
            checkboxes.append(checkbox)
            goal_box.add_widget(checkbox)

        # Delete Button
        delete_btn = Button(text="Delete", size_hint_x=0.2)
        delete_btn.bind(on_press=lambda instance: self.delete_goal(goal_box))
        goal_box.add_widget(delete_btn)

        # Store checkbox references
        goal_box.checkboxes = checkboxes
        goal_box.goal_text = goal_text

        # Add the goal at the top of the layout
        self.goals_layout.add_widget(goal_box, index=0)


    def delete_goal(self, goal_box):
        """Remove a specific goal from the UI and data."""
        self.goals_layout.remove_widget(goal_box)
        self.data["goals"] = [
            g for g in self.data["goals"] if g["goal"] != goal_box.goal_text
        ]
        self.save_data()

    def clear_all_goals(self, instance):
        """Remove all goals."""
        self.goals_layout.clear_widgets()
        self.data["goals"] = []
        self.save_data()

    def save_data(self, instance=None):
        """Save all goals and their progress to local storage."""
        self.data["goals"] = []
        for goal_box in self.goals_layout.children:
            progress_states = [cb.active for cb in goal_box.checkboxes]
            self.data["goals"].append({"goal": goal_box.goal_text, "progress": progress_states})

        with open(STORAGE_FILE, "w") as f:
            json.dump(self.data, f)
        print("All progress saved!")

    def load_data(self):
        """Load goals and progress from local storage."""
        try:
            with open(STORAGE_FILE, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"goals": []}


if __name__ == "__main__":
    GrowthTrackerApp().run()
