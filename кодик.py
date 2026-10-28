import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

CSV_URL = "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"
LOCAL_FILES = [
    Path("WA_Fn-UseC_-Telco-Customer-Churn.csv"),
    Path("Telco-Customer-Churn.csv"),
    Path("data") / "WA_Fn-UseC_-Telco-Customer-Churn.csv",
    Path("data") / "Telco-Customer-Churn.csv",
]

df = None

def load_data():
    global df
    try:
        df = pd.read_csv(CSV_URL)
        source = "Интернет"
    except Exception:
        for file in LOCAL_FILES:
            if file.exists():
                try:
                    df = pd.read_csv(file)
                    source = str(file)
                    break
                except Exception:
                    df = None
        if df is None:
            messagebox.showerror(
                "Ошибка загрузки",
                "Не удалось загрузить данные из интернета.\n"
                "Положи CSV-файл рядом с программой или в папку data."
            )
            return

    required = {
        "customerID", "tenure", "MonthlyCharges", "TotalCharges",
        "Churn", "PaymentMethod", "InternetService", "Contract"
    }
    missing = required - set(df.columns)
    if missing:
        messagebox.showerror("Неверный датасет", f"Не найдены столбцы: {', '.join(sorted(missing))}")
        df = None
        return

    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df["ChurnFlag"] = df["Churn"].map({"Yes": 1, "No": 0})
    status_var.set(f"Данные загружены: {len(df)} строк. Источник: {source}")
    update_summary()

def update_summary():
    if df is None:
        return
    total = len(df)
    churn = df["ChurnFlag"].mean() * 100
    missing = int(df["TotalCharges"].isna().sum())
    summary_text.set(
        f"Клиентов: {total}\n"
        f"Доля оттока: {churn:.1f}%\n"
        f"Пропусков в TotalCharges: {missing}"
    )

def show_plot(kind):
    if df is None:
        messagebox.showwarning("Нет данных", "Сначала нажми «Загрузить данные».")
        return

    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(9, 5))

    if kind == "payments":
        sns.countplot(data=df, y="PaymentMethod", hue="Churn",
                      hue_order=["No", "Yes"],
                      palette={"No": "#4C72B0", "Yes": "#C44E52"}, ax=ax)
        ax.set_title("Клиенты по способу оплаты и оттоку")
        ax.set_xlabel("Количество клиентов")
        ax.set_ylabel("Способ оплаты")

    elif kind == "monthly":
        sns.histplot(data=df, x="MonthlyCharges", hue="Churn", bins=30,
                     element="step", stat="density", common_norm=False,
                     palette={"No": "#4C72B0", "Yes": "#C44E52"}, ax=ax)
        ax.set_title("Месячные платежи в зависимости от оттока")
        ax.set_xlabel("Месячный платёж, $")
        ax.set_ylabel("Плотность")

    elif kind == "tenure":
        stats = df.groupby("tenure", as_index=False).agg(
            clients=("customerID", "count"),
            churn_rate=("ChurnFlag", "mean")
        )
        stats["churn_rate"] *= 100
        ax.plot(stats["tenure"], stats["churn_rate"], color="#C44E52")
        ax.set_title("Доля оттока по сроку обслуживания")
        ax.set_xlabel("Срок обслуживания, месяцев")
        ax.set_ylabel("Доля оттока, %")

    elif kind == "contract":
        sns.boxplot(data=df, x="Contract", y="MonthlyCharges", hue="Churn",
                    hue_order=["No", "Yes"],
                    palette={"No": "#4C72B0", "Yes": "#C44E52"}, ax=ax)
        ax.set_title("Месячный платёж по типу договора и оттоку")
        ax.set_xlabel("Тип договора")
        ax.set_ylabel("Месячный платёж, $")

    fig.tight_layout()
    plt.show()

def close_app():
    plt.close("all")
    root.destroy()

root = tk.Tk()
root.title("Лабораторная работа № 4 — анализ оттока клиентов")
root.geometry("620x440")
root.minsize(560, 400)

main = ttk.Frame(root, padding=18)
main.pack(fill="both", expand=True)

ttk.Label(main, text="Анализ оттока клиентов телеком-компании",
          font=("Segoe UI", 15, "bold")).pack(anchor="w", pady=(0, 8))
ttk.Label(main, text="Загрузи датасет, затем выбери график для просмотра.",
          font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 14))

ttk.Button(main, text="Загрузить данные", command=load_data).pack(anchor="w")

status_var = tk.StringVar(value="Данные ещё не загружены.")
ttk.Label(main, textvariable=status_var, wraplength=570).pack(anchor="w", pady=(10, 8))

summary_text = tk.StringVar(value="Сводка появится после загрузки данных.")
ttk.Label(main, textvariable=summary_text, justify="left",
          font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 14))

ttk.Label(main, text="Графики:", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))

buttons = ttk.Frame(main)
buttons.pack(fill="x")
ttk.Button(buttons, text="Способ оплаты", command=lambda: show_plot("payments")).grid(row=0, column=0, padx=(0, 8), pady=4, sticky="ew")
ttk.Button(buttons, text="Месячные платежи", command=lambda: show_plot("monthly")).grid(row=0, column=1, padx=(0, 8), pady=4, sticky="ew")
ttk.Button(buttons, text="Срок обслуживания", command=lambda: show_plot("tenure")).grid(row=1, column=0, padx=(0, 8), pady=4, sticky="ew")
ttk.Button(buttons, text="Тип договора", command=lambda: show_plot("contract")).grid(row=1, column=1, padx=(0, 8), pady=4, sticky="ew")
buttons.columnconfigure(0, weight=1)
buttons.columnconfigure(1, weight=1)

ttk.Label(main, text="Для работы нужны pandas, matplotlib и seaborn. Tkinter обычно входит в Python.",
          foreground="#555555", wraplength=570).pack(anchor="w", pady=(16, 0))

root.protocol("WM_DELETE_WINDOW", close_app)
root.mainloop()
