import os
import csv
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import threading


### PLEASE READ #######
# Hi! This program was created by Elton Dias for educational and experiamental purposes only. Use with caution. DO NOT USE AS GAMBLING ADVICE!!!
# 
# The program creates a file that the results will be saved to. Click load a file a select the text file only if you have ran a previous prediction before. The more previous data there is, 
# the more accurate your prediction will become. Accurate stat input is crucial to the prediction as any misentered data will greatly effect your accuracy.
# 
# Next, enter a players name followed by their stats. (inputs go by their last 5 games written on the same line. ex. (15 3 2 5 3)).
# 
# Hit predict. You get returned a 1st prediction every time. A "2nd prediction"(literally named it that I'm sorry) only appears if you loaded a previous file with a player you inputted before.
# The 2nd prediction becomes more accurate with more data inputted. The AI prediction is a formula I requested an AI return. The AI prediction appears every time but on 1st player input, it will
# be identical to the main prediction. Returns a true prediction if both the 1st and 2nd predictions are present. This model ONLY SAVES THE 1ST PREDICTION. After gaames/study cases are played and
# actual outcomes are known, return and load up that file. Click on update and enter the actual player's outcomes. This ensures that the model can adjust predictions for the next time.
#
#
# From past data this model hits at a target of 66% accuracy. With more inputs, the 2nd and AI predictions become more accurate over time. The 1st predicition is solemnly based off the initial user
# inputs. Injuries, hot performing out of the blue games, and player emotional factors all come into a factor. Analyze each game and see if the model was incorrect or something happened in a game 
# that the model can't account for.
#
#
#





# File structure headers (How data will appear in the save file)
HEADERS = ["Name", "Minutes", "SeasonAvg", "Last5Pts", "Last5Reb", "Last5Ast", "FG%", 
           "DefAvg", "PredScore", "ActualScore"]


# Prediction function for 1st only
def calculate_first_prediction(minutes, season_avg, last5_pts, last5_reb, last5_ast, fg_percent, def_avg):
    season_pts, season_reb, season_ast = map(float, season_avg.split())
    last5_pts_list = list(map(float, last5_pts.split()))
    last5_reb_list = list(map(float, last5_reb.split()))
    last5_ast_list = list(map(float, last5_ast.split()))
    fg_percent = float(fg_percent)
    def_pts, def_reb, def_ast = map(float, def_avg.split())

    base_pts = (season_pts * 0.4) + (sum(last5_pts_list) / 5 * 0.6)
    base_reb = (season_reb * 0.4) + (sum(last5_reb_list) / 5 * 0.6)
    base_ast = (season_ast * 0.4) + (sum(last5_ast_list) / 5 * 0.6)

    minutes_factor = float(minutes) / 36
    adj_pts = base_pts * minutes_factor
    adj_reb = base_reb * minutes_factor
    adj_ast = base_ast * minutes_factor

    pred_pts = adj_pts * 1.05 if def_pts > adj_pts else adj_pts * 0.95
    pred_reb = adj_reb * 1.05 if def_reb > adj_reb else adj_reb * 0.95
    pred_ast = adj_ast * 1.05 if def_ast > adj_ast else adj_ast * 0.95

    if fg_percent > 50:
        pred_pts *= 1.05
    elif fg_percent < 43:
        pred_pts *= 0.95

    return f"{round(pred_pts)} {round(pred_reb)} {round(pred_ast)}"


# Prediction function for 2nd prediction (Only returns if data is found from a previous entry. If you want to see the 2nd prediction, you have to make sure you load a file with a previous entry
# data. This prediciton becomes more accurate with more entries overtime.)
def calculate_second_prediction(name, pred_score, filename):
    pred_pts, pred_reb, pred_ast = map(int, pred_score.split())
    past_entries = []

    if os.path.exists(filename):
        with open(filename, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["Name"] == name and row["ActualScore"]:
                    past_entries.append(row)

    if not past_entries:
        return None

    pts_error, reb_error, ast_error = 0, 0, 0
    for entry in past_entries:
        pred = list(map(int, entry["PredScore"].split()))
        actual = list(map(int, entry["ActualScore"].split()))
        pts_error += (pred[0] - actual[0])
        reb_error += (pred[1] - actual[1])
        ast_error += (pred[2] - actual[2])

    avg_pts_error = pts_error / len(past_entries)
    avg_reb_error = reb_error / len(past_entries)
    avg_ast_error = ast_error / len(past_entries)

    adj_pts = pred_pts - avg_pts_error
    adj_reb = pred_reb - avg_reb_error
    adj_ast = pred_ast - avg_ast_error

    return f"{round(adj_pts)} {round(adj_reb)} {round(adj_ast)}", len(past_entries)


# AI prediction appears witb every prediciton. Algorithm came from an AI request. Most accurate when you have both predictions. Usually the same as 1st prediction if no 2nd prediction is returned.
def calculate_ai_prediction(pred_score, last5_pts, last5_reb, last5_ast, filename, name):
    pred_pts, pred_reb, pred_ast = map(int, pred_score.split())
    last5_pts_list = list(map(float, last5_pts.split()))
    last5_reb_list = list(map(float, last5_reb.split()))
    last5_ast_list = list(map(float, last5_ast.split()))

    pts_trend = 1.0
    reb_trend = 1.0
    if last5_pts_list[0] < last5_pts_list[4]:
        pts_trend = 0.95
    elif last5_pts_list[0] > last5_pts_list[4]:
        pts_trend = 1.05
    
    if last5_reb_list[0] < last5_reb_list[4]:
        reb_trend = 0.95
    elif last5_reb_list[0] > last5_reb_list[4]:
        reb_trend = 1.05

    ast_trend = 1.0
    ast_avg_first_two = (last5_ast_list[0] + last5_ast_list[1]) / 2
    ast_avg_last_two = (last5_ast_list[3] + last5_ast_list[4]) / 2
    ast_middle = last5_ast_list[2]
    if ast_avg_first_two > ast_middle and ast_middle > ast_avg_last_two:
        ast_trend = 1.05
    elif ast_avg_first_two < ast_middle and ast_middle < ast_avg_last_two:
        ast_trend = 0.95

    trend_pts = pred_pts * pts_trend
    trend_reb = pred_reb * reb_trend
    trend_ast = pred_ast * ast_trend

    past_entries = []
    if os.path.exists(filename):
        with open(filename, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["Name"] == name and row["ActualScore"]:
                    past_entries.append(row)

    if not past_entries:
        return f"{round(trend_pts)} {round(trend_reb)} {round(trend_ast)}"

    pts_error, reb_error, ast_error = 0, 0, 0
    for entry in past_entries:
        pred = list(map(int, entry["PredScore"].split()))
        actual = list(map(int, entry["ActualScore"].split()))
        pts_error += (pred[0] - actual[0])
        reb_error += (pred[1] - actual[1])
        ast_error += (pred[2] - actual[2])

    avg_pts_error = min(max(pts_error / len(past_entries), -2), 2)
    avg_reb_error = min(max(reb_error / len(past_entries), -2), 2)
    avg_ast_error = min(max(ast_error / len(past_entries), -2), 2)

    ai_pts = trend_pts - avg_pts_error
    ai_reb = trend_reb - avg_reb_error
    ai_ast = trend_ast - avg_ast_error

    return f"{round(ai_pts)} {round(ai_reb)} {round(ai_ast)}"

# UI App (Updated UI). The app helps make the user experience better. I's very glitchy in terms of responsiveness. Just enlarge the window from the corners slowly and the buttons will respond again.
class StatPredictorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Player Stat Predictor")
        self.root.geometry("800x600")
        self.root.configure(bg="#FFFFFF")  # White background
        self.filename = None
        self.frames = {}
        self.entries = {}
        
        # Sidebar with vertical buttons (navy blue)
        sidebar_frame = tk.Frame(self.root, bg="#0C2340", width=150)
        sidebar_frame.pack(side="left", fill="y", padx=10, pady=10)
        buttons = [
            ("Main", self.show_main_frame),
            ("Predict", self.show_predict_frame),
            ("Load", self.show_load_frame),
            ("Update", self.show_update_frame),
            ("Stats", self.show_stats_frame)
        ]
        for i, (text, command) in enumerate(buttons):
            btn = tk.Button(sidebar_frame, text=text, font=("Arial", 18), width=15, height=2, 
                            bg="#FFFFFF", fg="#000000", command=command)  # White buttons, black text
            btn.grid(row=i, column=0, pady=10)

        # Content frame (white)
        self.content_frame = tk.Frame(self.root, bg="#FFFFFF")
        self.content_frame.pack(side="left", expand=True, fill="both", padx=10, pady=10)

        # Run frames
        self.frames["main"] = self.create_main_frame()
        self.frames["predict"] = self.create_predict_frame()
        self.frames["load"] = self.create_load_frame()
        self.frames["update"] = self.create_update_frame()
        self.frames["stats"] = self.create_stats_frame()

        # Show main
        self.show_frame("main")
        self.root.after(2000, self.show_main_frame)  # Splash-like delay

    def show_frame(self, frame_name):
        for frame in self.frames.values():
            frame.pack_forget()
        self.frames[frame_name].pack(expand=True, fill="both")

    def create_main_frame(self):
        frame = tk.Frame(self.content_frame, bg="#FFFFFF")
        tk.Label(frame, text="Welcome to Player Stat Predictor", font=("Arial", 20), 
                 bg="#FFFFFF", fg="#FFC107").pack(pady=20)  # Gold text
        tk.Button(frame, text="Exit", font=("Arial", 18), width=15, height=2, 
                  bg="#FFFFFF", fg="#000000", command=self.root.quit).pack(pady=10)
        return frame

    def create_predict_frame(self):
        frame = tk.Frame(self.content_frame, bg="#FFFFFF")
        labels = ["Name", "Minutes", "Season Avg (pts reb ast)", "Last 5 Pts", "Last 5 Reb", 
                  "Last 5 Ast", "FG%", "Def Avg (pts reb ast)"]
        self.entries = {}
        for i, label in enumerate(labels):
            tk.Label(frame, text=label, font=("Arial", 12), bg="#FFFFFF", fg="#FFC107").grid(row=i, column=0, 
                                                                                            padx=10, pady=5, sticky="e")  # Gold labels
            entry = tk.Entry(frame, font=("Arial", 12), width=40)
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries[label] = entry

        tk.Button(frame, text="Predict", font=("Arial", 18), width=15, height=2, 
                  bg="#FFFFFF", fg="#000000", command=self.make_prediction).grid(row=len(labels), column=0, pady=20)
        tk.Button(frame, text="New File", font=("Arial", 18), width=15, height=2, 
                  bg="#FFFFFF", fg="#000000", command=self.new_prediction).grid(row=len(labels), column=1, pady=20)
        return frame

    def create_load_frame(self):
        frame = tk.Frame(self.content_frame, bg="#FFFFFF")
        tk.Label(frame, text="Select a File", font=("Arial", 16), bg="#FFFFFF", fg="#FFC107").pack(pady=10)
        
        # Treeview for files
        self.load_tree = ttk.Treeview(frame, columns=("File", "Size", "Date"), show="headings", height=10)
        self.load_tree.heading("File", text="File Name")
        self.load_tree.heading("Size", text="Size (KB)")
        self.load_tree.heading("Date", text="Created")
        self.load_tree.column("File", width=250)
        self.load_tree.column("Size", width=100)
        self.load_tree.column("Date", width=150)
        self.load_tree.pack(pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.load_tree.yview)
        self.load_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        # Bindings
        self.load_tree.bind("<Double-1>", lambda e: self.load_file())
        self.load_tree.bind("<Return>", lambda e: self.load_file())
        
        tk.Button(frame, text="Load", font=("Arial", 18), width=15, height=2, 
                  bg="#FFFFFF", fg="#000000", command=self.load_file).pack(pady=10)
        self.refresh_load_list_threaded()
        return frame

    def create_update_frame(self):
        frame = tk.Frame(self.content_frame, bg="#FFFFFF")
        tk.Label(frame, text="Update Actual Results", font=("Arial", 16), bg="#FFFFFF", fg="#FFC107").pack(pady=10)
        
        # Treeview for updates
        self.update_tree = ttk.Treeview(frame, columns=("Index", "Name", "PredScore"), show="headings", height=10)
        self.update_tree.heading("Index", text="Index")
        self.update_tree.heading("Name", text="Player Name")
        self.update_tree.heading("PredScore", text="Predicted Score")
        self.update_tree.column("Index", width=50)
        self.update_tree.column("Name", width=200)
        self.update_tree.column("PredScore", width=150)
        self.update_tree.pack(pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.update_tree.yview)
        self.update_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        # Bindings
        self.update_tree.bind("<Double-1>", lambda e: self.update_selected())
        self.update_tree.bind("<Return>", lambda e: self.update_selected())
        
        self.update_entry = tk.Entry(frame, font=("Arial", 12), width=30)
        self.update_entry.pack(pady=5)
        tk.Label(frame, text="Enter actual (pts reb ast) or 'NA'", font=("Arial", 10), 
                 bg="#FFFFFF", fg="#FFC107").pack()
        tk.Button(frame, text="Update", font=("Arial", 18), width=15, height=2, 
                  bg="#FFFFFF", fg="#000000", command=self.update_selected).pack(pady=10)
        self.refresh_update_list_threaded()
        return frame

    def create_stats_frame(self):
        frame = tk.Frame(self.content_frame, bg="#FFFFFF")
        tk.Label(frame, text="Check Player Stats", font=("Arial", 16), bg="#FFFFFF", fg="#FFC107").pack(pady=10)  # Gold text
        self.stats_entry = tk.Entry(frame, font=("Arial", 12), width=30)
        self.stats_entry.pack(pady=5)
        tk.Label(frame, text="Enter player name", font=("Arial", 10), bg="#FFFFFF", fg="#FFC107").pack()  # Gold text
        tk.Button(frame, text="Check", font=("Arial", 18), width=15, height=2, 
                  bg="#FFFFFF", fg="#000000", command=self.check_stats).pack(pady=10)
        return frame

    def show_main_frame(self):
        self.show_frame("main")

    def show_predict_frame(self):
        if not self.filename:
            self.new_prediction()
        self.show_frame("predict")

    def show_load_frame(self):
        self.refresh_load_list_threaded()
        self.show_frame("load")

    def show_update_frame(self):
        if not self.filename:
            messagebox.showerror("Error", "Please load or create a file first.")
            return
        self.refresh_update_list_threaded()
        self.show_frame("update")

    def show_stats_frame(self):
        if not self.filename:
            messagebox.showerror("Error", "Please load or create a file first.")
            return
        self.show_frame("stats")

    def new_prediction(self):
        self.filename = f"stats_{datetime.now().strftime('%Y%m%d')}.csv"
        messagebox.showinfo("Info", f"New file created: {self.filename}")

    def load_file(self):
        selection = self.load_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Select a file.")
            return
        self.filename = self.load_tree.item(selection[0])["values"][0]
        messagebox.showinfo("Info", f"Loaded: {self.filename}")
        self.show_main_frame()

    def refresh_load_list_threaded(self):
        def load():
            self.load_tree.delete(*self.load_tree.get_children())
            files = [f for f in os.listdir() if f.endswith(".csv")]
            for i, f in enumerate(files):
                size = os.path.getsize(f) / 1024  # KB
                date = datetime.fromtimestamp(os.path.getctime(f)).strftime("%Y-%m-%d")
                self.load_tree.insert("", "end", values=(f, f"{size:.1f}", date))
        threading.Thread(target=load).start()

    # Function to make prediction. Has errors built in if fields aren't correct. Will return responses then write the results to the save file.
    def make_prediction(self):
        inputs = [self.entries[label].get() for label in ["Name", "Minutes", "Season Avg (pts reb ast)", 
                                                          "Last 5 Pts", "Last 5 Reb", "Last 5 Ast", "FG%", 
                                                          "Def Avg (pts reb ast)"]]
        if not all(inputs):
            messagebox.showerror("Error", "All fields must be filled.")
            return

        pred_score = calculate_first_prediction(inputs[1], inputs[2], inputs[3], inputs[4], inputs[5], inputs[6], inputs[7])
        pred_pts, pred_reb, pred_ast = pred_score.split()

        result = f"{inputs[0]} predicted: {pred_pts} pts, {pred_reb} reb, {pred_ast} ast\n"
        second_pred = calculate_second_prediction(inputs[0], pred_score, self.filename)
        if second_pred:
            pred, entries = second_pred
            pred_pts, pred_reb, pred_ast = pred.split()
            result += f"Based on past data ({entries} entries): {pred_pts} pts, {pred_reb} reb, {pred_ast} ast\n"

        ai_pred = calculate_ai_prediction(pred_score, inputs[3], inputs[4], inputs[5], self.filename, inputs[0])
        ai_pts, ai_reb, ai_ast = ai_pred.split()
        result += f"AI Prediction: {ai_pts} pts, {ai_reb} reb, {ai_ast} ast"

        messagebox.showinfo("Prediction", result)

        row = inputs + [pred_score, ""]
        with open(self.filename, "a", newline="") as f:
            writer = csv.writer(f)
            if os.stat(self.filename).st_size == 0:
                writer.writerow(HEADERS)
            writer.writerow(row)

    def refresh_update_list_threaded(self):
        if not self.filename:
            return
        def load():
            self.update_tree.delete(*self.update_tree.get_children())
            with open(self.filename, "r", newline="") as f:
                reader = csv.DictReader(f)
                rows = [row for row in reader if not row["ActualScore"]]
            for i, row in enumerate(rows):
                self.update_tree.insert("", "end", values=(i, row["Name"], row["PredScore"]))
        threading.Thread(target=load).start()

    def update_selected(self):
        if not self.filename:
            return
        selection = self.update_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Select an entry to update.")
            return
        index = int(self.update_tree.item(selection[0])["values"][0])
        actual = self.update_entry.get().strip()
        if not actual:
            messagebox.showerror("Error", "Enter a value or 'NA'.")
            return
        with open(self.filename, "r", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        rows[[i for i, r in enumerate(rows) if not r["ActualScore"]][index]]["ActualScore"] = actual if actual.upper() != "NA" else ""
        with open(self.filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=HEADERS)
            writer.writeheader()
            writer.writerows(rows)
        messagebox.showinfo("Success", "Actual score updated.")
        self.refresh_update_list_threaded()


    # Still in the works. This will be able to search through your files once they get extremely long. The goal is to be able to enter the players name, it will return how many entries, the player's 
    # file averages, as well as other stats. 
    def check_stats(self):
        if not self.filename:
            return
        player_name = self.stats_entry.get().strip()
        if not player_name:
            messagebox.showerror("Error", "Enter a player name.")
            return

        entries = []
        with open(self.filename, "r", newline="") as f:
            reader = csv.DictReader(f)
            entries = [row for row in reader if row["Name"] == player_name]

        if not entries:
            messagebox.showinfo("Info", f"No entries found for {player_name}.")
            return

        pred_pts, pred_reb, pred_ast = 0, 0, 0
        actual_pts, actual_reb, actual_ast = 0, 0, 0
        actual_count = 0
        pts_diff = 0

        for entry in entries:
            p_pts, p_reb, p_ast = map(float, entry["PredScore"].split())
            pred_pts += p_pts
            pred_reb += p_reb
            pred_ast += p_ast
            if entry["ActualScore"]:
                a_pts, a_reb, a_ast = map(float, entry["ActualScore"].split())
                actual_pts += a_pts
                actual_reb += a_reb
                actual_ast += a_ast
                pts_diff += abs(p_pts - a_pts)
                actual_count += 1

        result = f"{player_name} - {len(entries)} entries\n"
        result += f"Avg Predicted: {pred_pts / len(entries):.1f} pts, {pred_reb / len(entries):.1f} reb, {pred_ast / len(entries):.1f} ast\n"
        if actual_count > 0:
            result += f"Avg Actual: {actual_pts / actual_count:.1f} pts, {actual_reb / actual_count:.1f} reb, {actual_ast / actual_count:.1f} ast\n"
            result += f"Avg Pts Diff: {pts_diff / actual_count:.1f}"
        messagebox.showinfo("Player Stats", result)

# Our main call
if __name__ == "__main__":
    root = tk.Tk()
    app = StatPredictorApp(root)
    root.mainloop()