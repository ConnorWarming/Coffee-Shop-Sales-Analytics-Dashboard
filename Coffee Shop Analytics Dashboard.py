"""
Coffee Shop Sales Analytics Dashboard
Connor Warming

Features:
- OOP with Product, Beverage, and Food classes
- Custom exceptions
- CSV loading with sample fallback
- Sales analytics with Pandas and NumPy
- Tkinter GUI dashboard
- Date and category filters
- CSV export of filtered data
- Revenue and quantity charts

Run:
    pip install pandas numpy matplotlib
    python coffee_shop_dashboard_improved.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# =========================
# Constants
# =========================

CATEGORY_BEVERAGE = "Beverage"
CATEGORY_FOOD = "Food"

COL_DATE = "date"
COL_PRODUCT = "product"
COL_CATEGORY = "category"
COL_QUANTITY = "quantity"
COL_PRICE = "price"
COL_REVENUE = "revenue"

DEFAULT_CSV = "coffee_sales.csv"


# =========================
# Custom Exceptions
# =========================

class InvalidPriceError(Exception):
    def __init__(self, price: float):
        super().__init__(f"Invalid price: {price}. Price must be greater than 0.")


class InvalidQuantityError(Exception):
    def __init__(self, quantity: int):
        super().__init__(f"Invalid quantity: {quantity}. Quantity must be greater than 0.")


# =========================
# Product Classes
# =========================

class Product:
    def __init__(self, name: str, category: str, base_price: float):
        self.name = name.strip()
        self.category = category.strip()
        self.validate_price(base_price)
        self.base_price = float(base_price)

    @staticmethod
    def validate_price(price: float):
        if price <= 0:
            raise InvalidPriceError(price)

    def __str__(self):
        return f"{self.name} ({self.category}): ${self.base_price:.2f}"


class Beverage(Product):
    def __init__(self, name: str, base_price: float, size: str = "Medium", temperature: str = "Hot"):
        super().__init__(name, CATEGORY_BEVERAGE, base_price)
        self.size = size
        self.temperature = temperature

    def __str__(self):
        return f"{self.name} - {self.size} {self.temperature} ({self.category}): ${self.base_price:.2f}"


class Food(Product):
    def __init__(self, name: str, base_price: float, is_vegetarian: bool = False, prep_time: int = 5):
        super().__init__(name, CATEGORY_FOOD, base_price)
        self.is_vegetarian = is_vegetarian
        self.prep_time = prep_time

    def __str__(self):
        status = "Vegetarian" if self.is_vegetarian else "Non-Vegetarian"
        return f"{self.name} - {status} ({self.category}): ${self.base_price:.2f}, Prep: {self.prep_time} min"


# =========================
# Data Analyzer
# =========================

class CoffeeShopAnalyzer:
    def __init__(self, csv_file: str = DEFAULT_CSV):
        self.csv_file = csv_file
        self.df = pd.DataFrame()
        self.load_data(csv_file)

    def load_data(self, csv_file: str):
        try:
            path = Path(csv_file)
            if not path.exists():
                raise FileNotFoundError(f"{csv_file} not found")

            temp_df = pd.read_csv(path)

            if temp_df.shape[1] == 1 and "date,product,category,quantity,price" in temp_df.columns[0]:
                col_name = temp_df.columns[0]
                temp_df = temp_df[col_name].str.split(",", expand=True)
                temp_df.columns = [COL_DATE, COL_PRODUCT, COL_CATEGORY, COL_QUANTITY, COL_PRICE]

            required = [COL_DATE, COL_PRODUCT, COL_CATEGORY, COL_QUANTITY, COL_PRICE]
            missing = [col for col in required if col not in temp_df.columns]
            if missing:
                raise ValueError(f"Missing required columns: {', '.join(missing)}")

            self.df = temp_df.copy()
            self.df[COL_DATE] = pd.to_datetime(self.df[COL_DATE], errors="coerce")
            self.df.dropna(subset=[COL_DATE], inplace=True)

            self.df[COL_QUANTITY] = pd.to_numeric(self.df[COL_QUANTITY], errors="coerce")
            self.df[COL_PRICE] = pd.to_numeric(self.df[COL_PRICE], errors="coerce")
            self.df.dropna(subset=[COL_QUANTITY, COL_PRICE], inplace=True)

            self.df[COL_QUANTITY] = self.df[COL_QUANTITY].astype(int)
            self.df[COL_PRICE] = self.df[COL_PRICE].astype(float)

            self.df = self.df[self.df[COL_QUANTITY] > 0]
            self.df = self.df[self.df[COL_PRICE] > 0]

            self.df[COL_PRODUCT] = self.df[COL_PRODUCT].astype(str).str.strip()
            self.df[COL_CATEGORY] = self.df[COL_CATEGORY].astype(str).str.strip()
            self.df[COL_REVENUE] = self.df[COL_QUANTITY] * self.df[COL_PRICE]

            if self.df.empty:
                raise ValueError("Dataset is empty after cleaning.")

        except Exception as e:
            print(f"Could not load CSV: {e}. Using sample data instead.")
            self.df = self.create_sample_data()

    def create_sample_data(self) -> pd.DataFrame:
        np.random.seed(42)

        products = [
            ("Latte", CATEGORY_BEVERAGE, 4.50),
            ("Cappuccino", CATEGORY_BEVERAGE, 4.00),
            ("Espresso", CATEGORY_BEVERAGE, 3.00),
            ("Mocha", CATEGORY_BEVERAGE, 4.75),
            ("Croissant", CATEGORY_FOOD, 3.25),
            ("Muffin", CATEGORY_FOOD, 2.75),
            ("Bagel", CATEGORY_FOOD, 2.50),
            ("Sandwich", CATEGORY_FOOD, 6.50),
        ]

        dates = pd.date_range("2025-01-01", periods=30, freq="D")
        rows = []

        for current_date in dates:
            for _ in range(np.random.randint(5, 11)):
                product_name, category, price = products[np.random.randint(0, len(products))]
                quantity = np.random.randint(1, 6)
                rows.append({
                    COL_DATE: current_date,
                    COL_PRODUCT: product_name,
                    COL_CATEGORY: category,
                    COL_QUANTITY: quantity,
                    COL_PRICE: price,
                })

        df = pd.DataFrame(rows)
        df[COL_REVENUE] = df[COL_QUANTITY] * df[COL_PRICE]
        return df

    def get_categories(self):
        return ["All"] + sorted(self.df[COL_CATEGORY].dropna().unique().tolist())

    def get_date_range(self):
        if self.df.empty:
            return None, None
        return self.df[COL_DATE].min().date(), self.df[COL_DATE].max().date()

    def filter_data(self, category="All", start_date="", end_date=""):
        filtered = self.df.copy()

        if category and category != "All":
            filtered = filtered[filtered[COL_CATEGORY] == category]

        if start_date.strip():
            try:
                start = pd.to_datetime(start_date)
                filtered = filtered[filtered[COL_DATE] >= start]
            except Exception:
                raise ValueError("Start date must be in YYYY-MM-DD format.")

        if end_date.strip():
            try:
                end = pd.to_datetime(end_date)
                filtered = filtered[filtered[COL_DATE] <= end]
            except Exception:
                raise ValueError("End date must be in YYYY-MM-DD format.")

        return filtered

    def get_summary_metrics(self, df=None):
        if df is None:
            df = self.df

        if df.empty:
            return {
                "total_revenue": 0.0,
                "total_transactions": 0,
                "average_sale": 0.0,
                "best_seller": "N/A",
                "top_category": "N/A",
            }

        total_revenue = float(df[COL_REVENUE].sum())
        total_transactions = int(len(df))
        average_sale = float(df[COL_REVENUE].mean())

        best_seller_series = df.groupby(COL_PRODUCT)[COL_QUANTITY].sum().sort_values(ascending=False)
        best_seller = best_seller_series.index[0] if not best_seller_series.empty else "N/A"

        top_category_series = df.groupby(COL_CATEGORY)[COL_REVENUE].sum().sort_values(ascending=False)
        top_category = top_category_series.index[0] if not top_category_series.empty else "N/A"

        return {
            "total_revenue": total_revenue,
            "total_transactions": total_transactions,
            "average_sale": average_sale,
            "best_seller": best_seller,
            "top_category": top_category,
        }

    def get_best_sellers(self, df=None, top_n=5):
        if df is None:
            df = self.df
        if df.empty:
            return pd.DataFrame(columns=[COL_QUANTITY, COL_REVENUE])

        return (
            df.groupby(COL_PRODUCT)
            .agg({COL_QUANTITY: "sum", COL_REVENUE: "sum"})
            .sort_values(COL_REVENUE, ascending=False)
            .head(top_n)
        )

    def get_category_revenue(self, df=None):
        if df is None:
            df = self.df
        if df.empty:
            return pd.Series(dtype=float)

        return (
            df.groupby(COL_CATEGORY)[COL_REVENUE]
            .sum()
            .sort_values(ascending=False)
        )

    def get_daily_trends(self, df=None):
        if df is None:
            df = self.df
        if df.empty:
            return pd.DataFrame(columns=[COL_DATE, COL_REVENUE, COL_QUANTITY])

        return (
            df.groupby(COL_DATE)
            .agg({COL_REVENUE: "sum", COL_QUANTITY: "sum"})
            .reset_index()
            .sort_values(COL_DATE)
        )

    def get_statistics(self, df=None):
        if df is None:
            df = self.df
        if df.empty:
            return {
                "mean": 0.0,
                "std": 0.0,
                "median": 0.0,
                "min": 0.0,
                "max": 0.0,
                "percentile_25": 0.0,
                "percentile_75": 0.0,
            }

        revenue_array = df[COL_REVENUE].values
        return {
            "mean": float(np.mean(revenue_array)),
            "std": float(np.std(revenue_array)),
            "median": float(np.median(revenue_array)),
            "min": float(np.min(revenue_array)),
            "max": float(np.max(revenue_array)),
            "percentile_25": float(np.percentile(revenue_array, 25)),
            "percentile_75": float(np.percentile(revenue_array, 75)),
        }

    def export_filtered_data(self, df: pd.DataFrame, output_path: str):
        if df.empty:
            raise ValueError("There is no filtered data to export.")
        export_df = df.copy()
        export_df[COL_DATE] = export_df[COL_DATE].dt.strftime("%Y-%m-%d")
        export_df.to_csv(output_path, index=False)


# =========================
# GUI Application
# =========================

class CoffeeShopGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Coffee Shop Sales Analytics Dashboard")
        self.root.geometry("1150x780")
        self.root.configure(bg="#eef3f8")

        try:
            self.analyzer = CoffeeShopAnalyzer(DEFAULT_CSV)
        except Exception as e:
            messagebox.showerror("Startup Error", f"Failed to initialize analyzer:\n{e}")
            raise

        self.filtered_df = self.analyzer.df.copy()
        self.current_canvas = None
        self.current_figure = None

        self.build_ui()
        self.refresh_dashboard()

    def build_ui(self):
        header = tk.Frame(self.root, bg="#204c73", height=60)
        header.pack(fill="x")

        tk.Label(
            header,
            text="Coffee Shop Sales Analytics Dashboard",
            bg="#204c73",
            fg="white",
            font=("Segoe UI", 18, "bold")
        ).pack(side="left", padx=20, pady=12)

        main = tk.Frame(self.root, bg="#eef3f8")
        main.pack(fill="both", expand=True, padx=12, pady=12)

        filter_frame = tk.LabelFrame(main, text="Filters", bg="white", padx=10, pady=10)
        filter_frame.pack(fill="x", pady=(0, 10))

        tk.Label(filter_frame, text="Category", bg="white").grid(row=0, column=0, padx=8, pady=6, sticky="w")
        self.category_var = tk.StringVar(value="All")
        self.category_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.category_var,
            values=self.analyzer.get_categories(),
            state="readonly",
            width=18
        )
        self.category_combo.grid(row=0, column=1, padx=8, pady=6)

        tk.Label(filter_frame, text="Start Date (YYYY-MM-DD)", bg="white").grid(row=0, column=2, padx=8, pady=6, sticky="w")
        self.start_date_var = tk.StringVar()
        tk.Entry(filter_frame, textvariable=self.start_date_var, width=18).grid(row=0, column=3, padx=8, pady=6)

        tk.Label(filter_frame, text="End Date (YYYY-MM-DD)", bg="white").grid(row=0, column=4, padx=8, pady=6, sticky="w")
        self.end_date_var = tk.StringVar()
        tk.Entry(filter_frame, textvariable=self.end_date_var, width=18).grid(row=0, column=5, padx=8, pady=6)

        btn_row = tk.Frame(filter_frame, bg="white")
        btn_row.grid(row=0, column=6, padx=8, pady=6)

        tk.Button(btn_row, text="Apply Filters", width=14, command=self.apply_filters).pack(side="left", padx=4)
        tk.Button(btn_row, text="Reset", width=10, command=self.reset_filters).pack(side="left", padx=4)
        tk.Button(btn_row, text="Export CSV", width=12, command=self.export_csv).pack(side="left", padx=4)

        stats_frame = tk.Frame(main, bg="#eef3f8")
        stats_frame.pack(fill="x", pady=(0, 10))

        self.stat_labels = {}
        stat_names = [
            "Total Revenue",
            "Transactions",
            "Average Sale",
            "Best Seller",
            "Top Category",
        ]

        for i, name in enumerate(stat_names):
            card = tk.Frame(stats_frame, bg="white", bd=1, relief="solid", padx=16, pady=12)
            card.grid(row=0, column=i, padx=6, sticky="nsew")
            stats_frame.grid_columnconfigure(i, weight=1)

            tk.Label(card, text=name, bg="white", font=("Segoe UI", 10, "bold")).pack()
            lbl = tk.Label(card, text="--", bg="white", font=("Segoe UI", 13))
            lbl.pack(pady=(8, 0))
            self.stat_labels[name] = lbl

        content = tk.Frame(main, bg="#eef3f8")
        content.pack(fill="both", expand=True)

        left_panel = tk.Frame(content, bg="#eef3f8")
        left_panel.pack(side="left", fill="both", expand=False, padx=(0, 8))

        right_panel = tk.Frame(content, bg="#eef3f8")
        right_panel.pack(side="left", fill="both", expand=True)

        table_box = tk.LabelFrame(left_panel, text="Top Products", bg="white")
        table_box.pack(fill="both", expand=False, pady=(0, 8))

        self.tree = ttk.Treeview(
            table_box,
            columns=("Product", "Quantity", "Revenue"),
            show="headings",
            height=10
        )
        self.tree.heading("Product", text="Product")
        self.tree.heading("Quantity", text="Quantity Sold")
        self.tree.heading("Revenue", text="Revenue")
        self.tree.column("Product", width=180, anchor="w")
        self.tree.column("Quantity", width=110, anchor="center")
        self.tree.column("Revenue", width=110, anchor="e")
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

        stats_box = tk.LabelFrame(left_panel, text="Revenue Statistics", bg="white")
        stats_box.pack(fill="both", expand=True)

        self.stats_text = tk.Text(stats_box, width=38, height=12, font=("Consolas", 10))
        self.stats_text.pack(fill="both", expand=True, padx=8, pady=8)
        self.stats_text.config(state="disabled")

        chart_controls = tk.Frame(right_panel, bg="#eef3f8")
        chart_controls.pack(fill="x", pady=(0, 8))

        tk.Button(chart_controls, text="Category Revenue", width=18, command=lambda: self.show_chart("category")).pack(side="left", padx=4)
        tk.Button(chart_controls, text="Daily Revenue", width=18, command=lambda: self.show_chart("daily_revenue")).pack(side="left", padx=4)
        tk.Button(chart_controls, text="Daily Quantity", width=18, command=lambda: self.show_chart("daily_quantity")).pack(side="left", padx=4)

        self.chart_frame = tk.LabelFrame(right_panel, text="Visualization", bg="white")
        self.chart_frame.pack(fill="both", expand=True)

    def apply_filters(self):
        try:
            self.filtered_df = self.analyzer.filter_data(
                category=self.category_var.get(),
                start_date=self.start_date_var.get(),
                end_date=self.end_date_var.get()
            )
            self.refresh_dashboard()
        except Exception as e:
            messagebox.showerror("Filter Error", str(e))

    def reset_filters(self):
        self.category_var.set("All")
        self.start_date_var.set("")
        self.end_date_var.set("")
        self.filtered_df = self.analyzer.df.copy()
        self.refresh_dashboard()

    def export_csv(self):
        try:
            if self.filtered_df.empty:
                messagebox.showinfo("Export", "There is no filtered data to export.")
                return

            path = filedialog.asksaveasfilename(
                title="Save Filtered Data",
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv")]
            )
            if not path:
                return

            self.analyzer.export_filtered_data(self.filtered_df, path)
            messagebox.showinfo("Export Complete", f"Filtered data exported to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def refresh_dashboard(self):
        metrics = self.analyzer.get_summary_metrics(self.filtered_df)

        self.stat_labels["Total Revenue"].config(text=f"${metrics['total_revenue']:.2f}")
        self.stat_labels["Transactions"].config(text=str(metrics["total_transactions"]))
        self.stat_labels["Average Sale"].config(text=f"${metrics['average_sale']:.2f}")
        self.stat_labels["Best Seller"].config(text=metrics["best_seller"])
        self.stat_labels["Top Category"].config(text=metrics["top_category"])

        for item in self.tree.get_children():
            self.tree.delete(item)

        best_sellers = self.analyzer.get_best_sellers(self.filtered_df, top_n=8)
        for product, row in best_sellers.iterrows():
            self.tree.insert(
                "",
                "end",
                values=(
                    product,
                    int(row[COL_QUANTITY]),
                    f"${row[COL_REVENUE]:.2f}"
                )
            )

        stats = self.analyzer.get_statistics(self.filtered_df)
        lines = [
            "Revenue Statistics",
            "-----------------------------",
            f"Mean:            ${stats['mean']:.2f}",
            f"Std Dev:         ${stats['std']:.2f}",
            f"Median:          ${stats['median']:.2f}",
            f"Minimum:         ${stats['min']:.2f}",
            f"Maximum:         ${stats['max']:.2f}",
            f"25th Percentile: ${stats['percentile_25']:.2f}",
            f"75th Percentile: ${stats['percentile_75']:.2f}",
        ]

        self.stats_text.config(state="normal")
        self.stats_text.delete("1.0", tk.END)
        self.stats_text.insert("1.0", "\n".join(lines))
        self.stats_text.config(state="disabled")

        self.show_chart("category")

    def clear_chart(self):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        if self.current_figure is not None:
            plt.close(self.current_figure)
            self.current_figure = None
            self.current_canvas = None

    def show_chart(self, chart_type: str):
        self.clear_chart()

        fig, ax = plt.subplots(figsize=(7.5, 4.5))
        self.current_figure = fig

        if self.filtered_df.empty:
            ax.text(0.5, 0.5, "No data available for selected filters.", ha="center", va="center", fontsize=12)
            ax.set_axis_off()
        elif chart_type == "category":
            category_revenue = self.analyzer.get_category_revenue(self.filtered_df)
            ax.bar(category_revenue.index, category_revenue.values)
            ax.set_title("Revenue by Category")
            ax.set_xlabel("Category")
            ax.set_ylabel("Revenue ($)")
        elif chart_type == "daily_revenue":
            daily = self.analyzer.get_daily_trends(self.filtered_df)
            ax.plot(daily[COL_DATE], daily[COL_REVENUE], marker="o")
            ax.set_title("Daily Revenue Trend")
            ax.set_xlabel("Date")
            ax.set_ylabel("Revenue ($)")
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        elif chart_type == "daily_quantity":
            daily = self.analyzer.get_daily_trends(self.filtered_df)
            ax.plot(daily[COL_DATE], daily[COL_QUANTITY], marker="o")
            ax.set_title("Daily Quantity Trend")
            ax.set_xlabel("Date")
            ax.set_ylabel("Quantity Sold")
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        else:
            ax.text(0.5, 0.5, "Unknown chart type.", ha="center", va="center")
            ax.set_axis_off()

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)
        self.current_canvas = canvas


# =========================
# Demo / Startup
# =========================

def demo_products():
    print("Testing Product Classes...\n")

    latte = Beverage("Caramel Latte", 4.50, "Large", "Hot")
    croissant = Food("Butter Croissant", 3.25, is_vegetarian=True, prep_time=2)

    print(latte)
    print(croissant)

    try:
        Product("Invalid Product", "Test", -5.00)
    except InvalidPriceError as e:
        print(f"Caught expected error: {e}")

    print("\nProduct tests completed.\n")


def main():
    demo_products()

    root = tk.Tk()
    app = CoffeeShopGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()