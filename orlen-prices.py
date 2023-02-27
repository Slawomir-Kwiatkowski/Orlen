import calendar
import sys
import tkinter as tk
from datetime import date, datetime
from tkinter import ttk
from tkinter.font import nametofont

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from utils import fetch_data, json_to_df


class MainWindow(tk.Frame):
    bacground = "#EEEEEE"
    price_data = {}
    current_date = date.today()
    months = calendar.month_abbr
    products = {
        "Eurosuper95": 41,
        "SuperPlus98": 42,
        "Bio100": 47,
        "Arktyczny2": 44,
        "Ekodiesel": 43,
        "GrzewczyEkoterm": 46,
        "MiejskiSuper": 45,
    }

    def __init__(self, root):
        super().__init__(root)
        self.create_UI(root)

    def create_UI(self, root):
        if sys.platform.startswith("linux"):
            root.attributes("-zoomed", True)
        else:
            root.state("zoomed")
        root.title("Orlen wholesale prices")
        self.show_menu(root)
        self.show_product_combobox(root)
        self.show_year_combobox(root)
        self.show_radiobuttons(root)
        self.show_chart_button(root)
        self.show_msg_label(root)
        self.show_data_table(root)

    def show_menu(self, root):
        # Menu bar
        menu_bar = tk.Menu(root)
        root.config(menu=menu_bar)
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Exit", command=self._exit)
        menu_bar.add_cascade(label="File", menu=file_menu)

    @staticmethod
    def _exit():
        root.destroy()  # this is necessary on Windows
        root.quit()  # stops mainloop

    def show_product_combobox(self, root):
        self.product_sv = tk.StringVar(value="")
        product_cb = ttk.Combobox(root, textvariable=self.product_sv)
        product_cb["values"] = [x for x in self.products]
        product_cb.set("Product")
        product_cb.state = "readonly"
        product_cb.bind("<<ComboboxSelected>>", self.enable_show_chart_btn)
        product_cb.grid(row=0, column=0, padx=10, pady=10)

    def show_year_combobox(self, root):
        self.year_sv = tk.StringVar(value="")
        year_cb = ttk.Combobox(root, textvariable=self.year_sv)
        year_cb["values"] = [x for x in range(self.current_date.year, 2004 - 1, -1)]
        year_cb.set("Year")
        year_cb.state = "readonly"
        year_cb.bind("<<ComboboxSelected>>", self.enable_show_chart_btn)
        year_cb.grid(row=0, column=1, padx=10, pady=10)

    def show_radiobuttons(self, root):
        # Frame for Radiobuttons
        rb_frame = tk.Frame(root)
        rb_frame["borderwidth"] = 1
        rb_frame["relief"] = "groove"
        rb_frame.grid(row=0, column=2, sticky="w")
        # Radiobuttons
        self.radio_sv = tk.StringVar(value="All")
        for i, month in enumerate(self.months):
            if month == "":
                month_rb = tk.Radiobutton(
                    rb_frame, text="All", value="All", variable=self.radio_sv
                )
            else:
                month_rb = tk.Radiobutton(
                    rb_frame, text=month, value=month, variable=self.radio_sv
                )
            month_rb.grid(row=0, column=i)

    def show_chart_button(self, root):
        self.show_chart_btn = ttk.Button(
            root, text="Show Chart", command=self.show_chart_btn_clicked
        )
        self.show_chart_btn["state"] = "disabled"
        self.show_chart_btn.grid(row=0, column=3, padx=10, sticky="w")

    def show_data_table(self, root):
        # Show Data Frame
        data_frame = tk.Frame(root)
        data_frame["borderwidth"] = 1
        data_frame["relief"] = "groove"
        data_frame.grid(row=1, column=0, columnspan=2, sticky=tk.N)
        # Show Data Table
        nametofont("TkHeadingFont").configure(weight="bold")
        self.table = ttk.Treeview(data_frame, show="headings", height=25)
        scrollbar = ttk.Scrollbar(
            data_frame, orient="vertical", command=self.table.yview
        )
        scrollbar.grid(row=0, column=1, sticky=tk.NS)

        self.table.configure(yscrollcommand=scrollbar.set)

        self.table["columns"] = ("Date", "Price")
        self.table.column("Date", anchor=tk.CENTER)
        self.table.column("Price", anchor=tk.CENTER)

        self.table.heading("Date", text="Date", anchor=tk.CENTER)
        self.table.heading("Price", text="Price [PLN]", anchor=tk.CENTER)

        self.table.tag_configure("odd", background=self.bacground)
        self.table.configure

        self.table.grid(row=0, column=0)

    def show_msg_label(self, root):
        self.msg = tk.StringVar(value="OK")
        msg_label = tk.Label(root, relief="groove", anchor="w", textvariable=self.msg)
        msg_label.grid(row=3, column=0, columnspan=6, sticky="ews")
        root.grid_rowconfigure(3, weight=1)
        root.grid_columnconfigure(5, weight=1)

    def enable_show_chart_btn(self, sender):
        if (
            str(self.show_chart_btn["state"]) == "disabled"
            and self.product_sv.get() != "Product"
            and self.year_sv.get() != "Year"
        ):
            self.show_chart_btn["state"] = "!disabled"

    def show_chart_btn_clicked(self):
        self.msg.set("")
        product_id = self.products[self.product_sv.get()]
        if product_id in self.price_data:
            data = self.price_data[product_id]
        else:
            data = fetch_data(product_id, self.current_date)
            if data is not None:
                self.price_data[product_id] = data
            else:
                self.msg.set("Error fetching data")
                return
        product_df = json_to_df(data)
        year = self.year_sv.get()
        month = self.radio_sv.get()
        self.table.delete(*self.table.get_children())
        try:
            if month == "All":
                chart_df = product_df.loc[year]
            else:
                month_int = datetime.strptime(month, "%b").month
                chart_df = product_df.loc[f"{year}-{month_int}"]
        except:
            self.msg.set("No data for selected date")
            for widget in self.chart_canvas.winfo_children():
                widget.destroy()
        else:
            average_price = "%d" % chart_df["value"].mean().round()
            max_price = chart_df["value"].max()
            min_price = chart_df["value"].min()
            self.msg.set(
                f"Average price: {average_price}, Max price: {max_price}, Min price: {min_price}"
            )
            self._set_data_table(chart_df[::-1])
            self._show_chart(root, chart_df, year, month)

    def _set_data_table(self, df):
        for i, row in enumerate(df.iloc):
            date, value = row
            if i % 2:
                self.table.insert(
                    parent="", index=i, text="", values=(date.date(), value), tag="odd"
                )
            else:
                self.table.insert(
                    parent="", index=i, text="", values=(date.date(), value)
                )

    def _show_chart(self, root, df, year, month):
        # Show Chart Frame
        self.chart_canvas = tk.Frame(root)
        self.chart_canvas["borderwidth"] = 1
        self.chart_canvas.grid(row=1, column=2, columnspan=2)
        # Chart
        date = [str(x.date()) for x in df["effectiveDate"]]
        price = df["value"].tolist()
        fig, ax = plt.subplots()
        if month == "All":
            month = ""
        ax.set_title(
            f"Orlen wholesale prices \
                {self.product_sv.get()} [PLN/m3] - {month} {year}"
        )
        ax.set_xlabel("Date")
        ax.set_ylabel("Price [PLN]")
        fig.autofmt_xdate()
        ax.grid(True)
        ax.xaxis.set_major_locator(plt.MaxNLocator(12))
        ax.yaxis.set_major_locator(plt.MaxNLocator(12))
        textstr = "(c) S.Kwiatkowski"
        props = dict(boxstyle="round", alpha=0.5)
        ax.plot(date, price, c="#CA3F62")
        ax.text(
            0.8,
            0.95,
            textstr,
            transform=ax.transAxes,
            fontsize=8,
            verticalalignment="top",
            bbox=props,
        )
        canvas = FigureCanvasTkAgg(fig, master=self.chart_canvas)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=2, sticky="nswe")


if __name__ == "__main__":
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", MainWindow._exit)  # to proper closing window
    app = MainWindow(root)
    app.mainloop()
