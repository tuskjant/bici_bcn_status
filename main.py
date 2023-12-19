import tkinter
import customtkinter
from tkintermapview import TkinterMapView
from tkinter import messagebox
import bike_geo_functions

ATTRIBUTION = "Ciclismo iconos creados por Stockio - Flaticon"
ATTRIBUTION2 = "Ciclismo iconos creados por Dragon Icons - Flaticon"
ATTRIBUTION3 = "Marcador iconos creados por mavadee - Flaticon"

options = ["Empty slots", "Bikes", "E-bikes"]
dict_key = ["empty_slots", "normal_bikes", "ebikes"]

customtkinter.set_default_color_theme("dark-blue")
customtkinter.set_appearance_mode("Dark")


class App(customtkinter.CTk):
    APP_NAME = "Bici bcn status"
    WIDTH = 900
    HEIGHT = 600

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title(App.APP_NAME)
        self.geometry(str(App.WIDTH) + "x" + str(App.HEIGHT))
        self.minsize(App.WIDTH, App.HEIGHT)
        self.iconbitmap("images/bicicleta.ico")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.createcommand('tk::mac::Quit', self.on_closing)

        self.lat_long = ()
        self.bike_data = []
        self.path_colors = ["#7e57c2", "#66bb6a", "#f2ca4b"]
        self.marker_icons = []
        for image in ["bike_blue.png", "bike_green.png", "bike_yellow.png", "posicion.png"]:
            photo_img = tkinter.PhotoImage(file="images/" + image)
            self.marker_icons.append(photo_img)

        self.map_markers_to = None
        self.map_marker_from = None
        self.map_paths = None

        # ============ create two CTkFrames ============

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self, width=150, corner_radius=0)
        self.frame_left.grid(row=0, column=0, rowspan=1, pady=0, padx=0, sticky="nsew")

        self.frame_right = customtkinter.CTkFrame(master=self, corner_radius=0, fg_color=None)
        self.frame_right.grid(row=0, column=1, padx=0, pady=0, sticky="nsew")
        self.frame_right.grid_forget()


        # ============ frame_right ============

        self.frame_right.grid_rowconfigure(2, weight=1)

        self.label_1 = customtkinter.CTkLabel(master=self.frame_right, font=("Roboto", 15, "bold"), text="Stations")
        self.label_1.grid(pady=(10, 0), padx=(20, 20), row=0, column=0)

        self.frame_text = customtkinter.CTkFrame(master=self.frame_right)
        self.frame_text.grid(row=1, column=0, pady=(20, 5), padx=10)

        # Tab Station 1
        self.label_t1_name = customtkinter.CTkLabel(master=self.frame_text, text="", font=("Roboto", 13, "bold"))
        self.label_t1_name.pack(pady=(10, 0))

        self.text_route1 = customtkinter.CTkTextbox(master=self.frame_text, width=320, height=100)
        self.text_route1.configure(state="disabled")
        self.text_route1.pack(pady=(10, 0))

        # Tab Station 2
        self.label_t2_name = customtkinter.CTkLabel(master=self.frame_text, text="", font=("Roboto", 13, "bold"))
        self.label_t2_name.pack(pady=(10, 0))

        self.text_route2 = customtkinter.CTkTextbox(master=self.frame_text, width=320, height=100)
        self.text_route2.configure(state="disabled")
        self.text_route2.pack(pady=(10, 0))

        # Tab Station 3
        self.label_t3_name = customtkinter.CTkLabel(master=self.frame_text, text="", font=("Roboto", 13, "bold"))
        self.label_t3_name.pack(pady=(10, 0))

        self.text_route3 = customtkinter.CTkTextbox(master=self.frame_text, width=320, height=100)
        self.text_route3.configure(state="disabled")
        self.text_route3.pack(pady=(10, 0))

        # Clear button
        self.button_clear = customtkinter.CTkButton(master=self.frame_right,
                                                 text="Clear",
                                                 width=90,
                                                 command=self.restart)
        self.button_clear.grid(row=2, column=0, sticky="e", padx=10, pady=5)

        # ============ frame_left ============

        self.frame_left.grid_rowconfigure(1, weight=1)
        self.frame_left.grid_rowconfigure(0, weight=0)
        self.frame_left.grid_columnconfigure(0, weight=1)
        self.frame_left.grid_columnconfigure(1, weight=0)
        self.frame_left.grid_columnconfigure(2, weight=0)
        self.frame_left.grid_columnconfigure(3, weight=0)

        self.map_widget = TkinterMapView(self.frame_left, corner_radius=0, width=500)
        self.map_widget.grid(row=1, rowspan=1, column=0, columnspan=4, sticky="nswe", padx=(20, 10), pady=(0, 10))

        self.entry = customtkinter.CTkEntry(master=self.frame_left,
                                            placeholder_text="type address")
        self.entry.grid(row=0, column=0, sticky="we", padx=(12, 0), pady=12)
        self.entry.bind("<Return>", self.get_bike_data)

        self.button_es = customtkinter.CTkButton(master=self.frame_left,
                                                text=options[0],
                                                width=90,
                                                command=lambda: self.get_bike_data(1))
        self.button_es.grid(row=0, column=1, sticky="w", padx=(12, 0), pady=12)

        self.button_b = customtkinter.CTkButton(master=self.frame_left,
                                                text=options[1],
                                                width=90,
                                                command=lambda: self.get_bike_data(2))
        self.button_b.grid(row=0, column=2, sticky="w", padx=(12, 0), pady=12)

        self.button_eb = customtkinter.CTkButton(master=self.frame_left,
                                                text=options[2],
                                                width=90,
                                                command=lambda: self.get_bike_data(3))
        self.button_eb.grid(row=0, column=3, sticky="w", padx=(12, 5), pady=12)

        # Credits button
        self.credits = customtkinter.CTkButton(master=self.frame_left, text="Credits & About",
                                               fg_color="transparent", font=("Roboto", 11),
                                                command=self.credits)
        self.credits.grid(row=2, column=0, sticky="w", padx=(20, 0), pady=5)

        # Map selection button
        self.map_option_menu = customtkinter.CTkOptionMenu(self.frame_left, values=["OpenStreetMap", "Google normal",
                                                                                     "Google satellite"],
                                                           command=self.change_map)
        self.map_option_menu.grid(row=2, column=2, columnspan=2, padx=5, pady=5, sticky="e")

        # Set default values
        self.map_widget.set_address("Barcelona")
        self.map_option_menu.set("OpenStreetMap")



  # ----------------------------------------------- functions

    def get_bike_data(self, event=None):
        if len(self.entry.get()) < 5:
            messagebox.showinfo("Error", "You must enter a valid address.")
            return
        self.lat_long = bike_geo_functions.get_address_coordinates(self.entry.get() + ", Barcelona")
        if self.lat_long is False:
            messagebox.showinfo("Error", "You must enter a valid address.")
            return
        self.map_widget.set_position(self.lat_long[0], self.lat_long[1])
        self.map_widget.set_zoom(18)
        if event in [1, 2, 3]:
            self.query = options[event - 1]
            self.query_dict_key = dict_key[event - 1]
            self.bike_data = bike_geo_functions.get_stations_data(self.lat_long, event)
            self.show_data()


    def show_data(self):
        self.frame_right.grid(row=0, column=1, padx=0, pady=0, sticky="nsew")
        # Route 1
        if len(self.bike_data) == 0:
            title1 = "No stations found"
            self.label_t1_name.configure(text=title1)
        else:
            if len(self.bike_data) >0:
                title1 = f"{self.bike_data[0]['name']}\n" \
                        f"{self.query}: {self.bike_data[0][self.query_dict_key]}\n" \
                        f"Dist: {self.bike_data[0]['dist']}m Time: {self.bike_data[0]['time']}min"
                self.label_t1_name.configure(text=title1, text_color=self.path_colors[2])
                self.text_route1.configure(state="normal")
                text1 = "\n".join(self.bike_data[0]["description"])
                self.text_route1.delete('0.0', 'end')
                self.text_route1.insert('end', text1)

            # Route 2
            if len(self.bike_data) > 1:
                title2 = f"{self.bike_data[1]['name']}\n" \
                         f"{self.query}: {self.bike_data[1][self.query_dict_key]}\n" \
                         f"Dist: {self.bike_data[1]['dist']}m Time: {self.bike_data[1]['time']}min"
                self.label_t2_name.configure(text=title2, text_color=self.path_colors[1])
                self.text_route2.configure(state="normal")
                text2 = "\n".join(self.bike_data[1]["description"])
                self.text_route2.delete('0.0', 'end')
                self.text_route2.insert('end', text2)
            # Route 3
            if len(self.bike_data) > 2:
                title3 = f"{self.bike_data[2]['name']}\n" \
                         f"{self.query}: {self.bike_data[2][self.query_dict_key]}\n" \
                         f"Dist: {self.bike_data[2]['dist']}m Time: {self.bike_data[2]['time']}min"
                self.label_t3_name.configure(text=title3, text_color=self.path_colors[0])
                self.text_route3.configure(state="normal")
                text3 = "\n".join(self.bike_data[2]["description"])
                self.text_route3.delete('0.0', 'end')
                self.text_route3.insert('end', text3)

            # Show data in map
            self.clear_map()
            self.map_marker_from = self.map_widget.set_marker(self.bike_data[0]["geom"][0][0], self.bike_data[0]["geom"][0][1],
                                                              icon=self.marker_icons[3],
                                                              icon_anchor="s")
            self.map_markers_to = [None, None, None]
            self.map_paths = [None, None, None]
            for index, data in enumerate(reversed(self.bike_data[:3])):
                # Show path and markers
                self.map_markers_to[index] = self.map_widget.set_marker(data["geom"][-1][0], data["geom"][-1][1],
                                           icon=self.marker_icons[index],
                                           icon_anchor="center")
                self.map_paths[index] = self.map_widget.set_path(data["geom"], color=self.path_colors[index])
            bbox = bike_geo_functions.calculate_bounding_box(self.bike_data)
            self.map_widget.fit_bounding_box(bbox[0], bbox[1])

    def change_map(self, new_map: str):
        if new_map == "OpenStreetMap":
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif new_map == "Google normal":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga",
                                            max_zoom=22)
        elif new_map == "Google satellite":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga",
                                            max_zoom=22)

    def credits(self):
        message = f"This python code is made by Gemma Riu. \n\n" \
                  f"Use of Cartociudad API for geocoding and routing\n" \
                  f"Use of CityBikes API for bike data collection https://api.citybik.es/v2/\n\n"\
                  f"Icons from https://www.flaticon.es :\n•{ATTRIBUTION}\n•{ATTRIBUTION2}\n•{ATTRIBUTION3}"
        messagebox.showinfo(title="Credits & About", message=message, icon="info")

    def restart(self):
        self.frame_right.grid_forget()
        self.clear_map()
        self.map_widget.update_canvas_tile_images()
        self.entry.delete(0, 'end')

    def clear_map(self):
        if self.map_marker_from is not None:
            self.map_marker_from.delete()
        if self.map_markers_to is not None:
            for marker in self.map_markers_to:
                if marker is not None:
                    marker.delete()
        if self.map_paths is not None:
            for path in self.map_paths:
                if path is not None:
                    path.delete()




    def on_closing(self, event=0):
        self.destroy()

    def start(self):
        self.mainloop()


if __name__ == "__main__":
    app = App()
    app.start()
