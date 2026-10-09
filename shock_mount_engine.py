# Project: F-150/Tacoma Axle Shock Mount Parametric Engine
# Purpose: Calculates loads and exports CAD sizing variables.

import customtkinter as ctk
import math
import csv
import pandas as pd

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ShockMountSizer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Shock Mount Load Engine v1.0")
        self.geometry("900x650")
        
        # --- Core Calculation Variables ---
        self.vehicle_mass = 2400 # kg
        self.corner_weight_bias = 0.55 # Rear axle static bias
        self.dynamic_g = 3.5 # Jounce G-force
        self.shock_angle_deg = 75 # Angle from horizontal
        self.fastener_dia = 12.7 # mm (1/2")
        self.shock_span = 38.1 # mm (1.5")
        
        # --- Material Database (simplified for GUI) ---
        self.materials = {
            "ASTM A36": {"Sy": 250, "Su": 400, "Se": 160},
            "HSLA 550": {"Sy": 550, "Su": 650, "Se": 260},
            "Domex 700": {"Sy": 700, "Su": 750, "Se": 300},
            "4130 Chromoly": {"Sy": 435, "Su": 670, "Se": 320}
        }

        # --- UI Build ---
        self.tabview = ctk.CTkTabview(self, width=800, height=500)
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)
        
        self.tab_view_inputs = self.tabview.add("Load Inputs")
        self.tab_view_material = self.tabview.add("Material Trade-Off")
        self.tab_view_export = self.tabview.add("DFM & Export")

        self.build_input_tab()
        self.build_material_tab()
        self.build_export_tab()
        
        # Data storage for export
        self.calculated_params = {}
        self.design_variables = {}

    def build_input_tab(self):
        # --- Input Fields for Loads ---
        ctk.CTkLabel(self.tab_view_inputs, text="Vehicle & Load Geometry", font=("Arial", 16, "bold")).pack(pady=10)
        
        self.entries = {}
        fields = [
            ("Vehicle Mass (kg)", self.vehicle_mass),
            ("Corner Weight Bias (0-1)", self.corner_weight_bias),
            ("Jounce G-Load", self.dynamic_g),
            ("Shock Angle (deg)", self.shock_angle_deg)
        ]
        
        for label_text, default in fields:
            frame = ctk.CTkFrame(self.tab_view_inputs, fg_color="transparent")
            frame.pack(pady=5)
            ctk.CTkLabel(frame, text=label_text, width=200, anchor="w").pack(side="left")
            entry = ctk.CTkEntry(frame, width=150)
            entry.insert(0, str(default))
            entry.pack(side="left")
            self.entries[label_text] = entry

        self.btn_calc = ctk.CTkButton(self.tab_view_inputs, text="Calculate Dynamic Loads", command=self.run_calculations)
        self.btn_calc.pack(pady=20)
        
        self.result_label = ctk.CTkLabel(self.tab_view_inputs, text="Ready to calculate...", justify="left")
        self.result_label.pack(pady=10, anchor="w")

    def run_calculations(self):
        mass = float(self.entries["Vehicle Mass (kg)"].get())
        bias = float(self.entries["Corner Weight Bias (0-1)"].get())
        g    = float(self.entries["Jounce G-Load"].get())
        ang  = float(self.entries["Shock Angle (deg)"].get())

        # One bracket carries half the rear axle load
        corner_kg = mass * bias / 2.0
        force_n   = corner_kg * 9.81 * g
        shock_force_n = force_n / math.sin(math.radians(ang))

        # Bending stress using the bracket's actual flange height (76.2 mm)
        moment_arm_mm = 76.2
        bending_moment_nmm = shock_force_n * moment_arm_mm

        t = 4.8      # sheet thickness
        h = 76.2     # flange height (saddle to hole)
        d = 38.1     # clevis span

        I_flange = (t * h**3) / 12
        A_flange = t * h
        I_total  = 2 * I_flange + 2 * A_flange * (d / 2) ** 2
        Z_total  = I_total / (h / 2)

        bending_stress_mpa = bending_moment_nmm / Z_total

        self.calculated_params = {
            "shock_force_N": shock_force_n,
            "bending_moment_Nmm": bending_moment_nmm,
            "bending_stress_MPa": bending_stress_mpa,
        }

        self.result_label.configure(
            text=(f"Shock Force: {shock_force_n:.0f} N\n"
                  f"Bending Stress (Saddle): {bending_stress_mpa:.1f} MPa")
        )
        self.update_material_analysis()

    def build_material_tab(self):
        ctk.CTkLabel(self.tab_view_material, text="Fatigue Safety Factor", font=("Arial", 16, "bold")).pack(pady=10)
        self.material_frame = ctk.CTkFrame(self.tab_view_material)
        self.material_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.mat_labels = {}
        for mat_name in self.materials.keys():
            lbl = ctk.CTkLabel(self.material_frame, text=f"{mat_name}: --", anchor="w")
            lbl.pack(fill="x", padx=20, pady=5)
            self.mat_labels[mat_name] = lbl

    def update_material_analysis(self):
        if not self.calculated_params: return
        
        # Use Goodman Criterion for safety factor
        sigma_a = self.calculated_params["bending_stress_MPa"] # Alternating stress
        
        for mat_name, props in self.materials.items():
            Se = props["Se"]
            # Safety factor n = Se / sigma_a
            nf = Se / sigma_a if sigma_a > 0 else 0
            status = "SAFE" if nf >= 1.0 else "FAIL"
            self.mat_labels[mat_name].configure(
                text=f"{mat_name}: nf = {nf:.2f} [{status}]",
                text_color="green" if nf >= 1.0 else "red"
            )

    def build_export_tab(self):
        ctk.CTkLabel(self.tab_view_export, text="Parametric CAD Variables", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Example DFM variables derived from the design
        # These would be driven by optimization in a real scenario
        self.design_variables = {
            "Axle_Radius_R": 41.25,      # mm
            "Clevis_Span": 38.1,         # mm
            "Hole_Center_Height": 76.2,  # mm
            "Fastener_Dia": 12.7,        # mm
            "Wall_Thickness": 4.8,       # mm
            "Saddle_Inner_Radius": 41.25,
            "Gusset_Angle": 45.0,        # deg
            "Doubler_Ring_Thickness": 2.0
        }
        
        for key, val in self.design_variables.items():
            frame = ctk.CTkFrame(self.tab_view_export, fg_color="transparent")
            frame.pack(pady=2)
            ctk.CTkLabel(frame, text=key, width=200, anchor="w").pack(side="left")
            entry = ctk.CTkEntry(frame, width=100)
            entry.insert(0, str(val))
            entry.pack(side="left")

        self.btn_export = ctk.CTkButton(self.tab_view_export, text="Export Parameterized CSV", command=self.export_csv)
        self.btn_export.pack(pady=20)

    def export_csv(self):
        # In a real tool, you would grab values from the entry fields
        filename = "Inventor_Parameters.csv"
        try:
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = ['Parameter', 'Value', 'Unit']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for key, val in self.design_variables.items():
                    unit = "mm" if "Dia" in key or "Thickness" in key or "Span" in key or "Height" in key or "Radius" in key else "deg"
                    writer.writerow({'Parameter': key, 'Value': val, 'Unit': unit})
            print(f"Successfully exported {filename}")
        except Exception as e:
            print(f"Export failed: {e}")

if __name__ == "__main__":
    app = ShockMountSizer()
    app.mainloop()