import customtkinter as ctk
import sqlite3
import requests
from PIL import Image, ImageTk
from datetime import datetime,timedelta

def get_weather(api_key, city):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': api_key,
        'timesteps': "1h",
        'units': 'metric',
        'lang': 'ua',
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if response.status_code == 200:
            temperature_celsius = round(data['main']['temp'])
            weather_description = data['weather'][0]['description']
            timezone_offset = data['timezone']
            return temperature_celsius, weather_description,timezone_offset
        else:
            print(f"Не удалось получить данные. Код ошибки: {response.status_code}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

    return None, None, None

def get_forecast(api_key, city):
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        'q': city,
        'appid': api_key,
        'timesteps': "1h",
        'units': 'metric',
        'lang': 'ua',
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if response.status_code == 200:
            response = []
            i = 0
            class Forecast:
                date = datetime.now()
                temp = 0
                description = ""
                def __init__(self, date, temp, description):
                    self.date = date
                    self.temp = temp
                    self.description = description

            for forecast in data['list']:
                date_time = forecast['dt_txt']
                weather_description = forecast['weather'][0]['description']
                temperature = round(forecast['main']['temp'])
                response.append(Forecast(date_time,temperature,weather_description))

            return response
        else:
            print(f"Не удалось получить данные. Код ошибки: {response.status_code}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

    return None, None, None

api_key = "b88d649977a4a1d454b4118cac6e9037"

city = "Днепр"

weather_icons = {
    "хмарно": "./icon/sunny_2412798.png",
    "легкий дощ": "./icon/drizzle_2412695.png",
    "помірний дощ": "./icon/rainy_2412747.png",
    "рвані хмари": "./icon/sunny_2412794.png",
    "уривчасті хмари": "./icon/sunny_2412794.png",
    "кілька хмар": "./icon/sunny_2412794.png",
    "легкий сніг": "./icon/snowy_2412768.png",
    "чисте небо": "./icon/sun_2412787.png",
    "сніг": "./icon/snowy_2412766.png",
    "легка злива": "./icon/drizzle_2412695.png",
}

cities = [
    "Дніпро",
    "Київ",
    "Рим",
    "Лондон",
    "Варшава",
    "Прага"
]
forecast_idx = 0

def submit(entry_country, entry_city, entry_firstname, entry_lastname, registration_window):
    country = entry_country.get()
    city = entry_city.get()
    firstname = entry_firstname.get()
    lastname = entry_lastname.get()
    
    print(f"Country: {country}\nCity: {city}\nFirstname: {firstname}\nLastname: {lastname}")

    connection = sqlite3.connect("registration_data.db")
    cursor = connection.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS registration (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      country TEXT,
                      city TEXT,
                      firstname TEXT,
                      lastname TEXT)''')
    
    cursor.execute("SELECT * FROM registration WHERE country=? AND city=? AND firstname=? AND lastname=?", (country, city, firstname, lastname))
    existing_user = cursor.fetchone()

    if existing_user:
        print("User already exists!")
    else:

        cursor.execute("INSERT INTO registration (country, city, firstname, lastname) VALUES (?, ?, ?, ?)", (country, city, firstname, lastname))
        print("Registration successful!")

    connection.commit()
    connection.close()

    showuserinfo((1, country, city, firstname, lastname))

    registration_window.withdraw()

def detail_weather_window(city, cabinet_window, widget_window):
    widget_window.destroy()
    detail_weather_window = ctk.CTkToplevel()
    detail_weather_window.title("Detail weather")
    detail_weather_window.geometry("350x350")
    detail_weather_window.configure(fg_color="#56A7B0")
    detail_weather_window.overrideredirect(True)
    refresh_weather(city, detail_weather_window, cabinet_window)

def refresh_weather(city, detail_weather_window, cabinet_window):
    (temperature,weather_description,b)  = get_weather(api_key, city)
    canvas = ctk.CTkCanvas(detail_weather_window, width=350, height=350)
    canvas.pack()
    canvas.create_rectangle(0, 0, 350, 350, fill="#56A7B0", outline="#56A7B0")
    label_widget = ctk.CTkLabel(canvas, text=f"{temperature}°", font=("Inter", 80, "bold"),fg_color="#56A7B0", bg_color="#56A7B0", text_color= "white")
    canvas.create_window(200, 190, anchor="nw", window=label_widget)
    label_description = ctk.CTkLabel(canvas, text=f"{weather_description}", font=("Inter", 25, "bold"),fg_color="#56A7B0", bg_color="#56A7B0", text_color= "white")
    canvas.create_window(27, 180, anchor="nw", window=label_description)
    label_city = ctk.CTkLabel(canvas, text = f"{city}", font=("Inter", 48, "bold"),fg_color="#56A7B0", bg_color="#56A7B0", text_color= "white")
    canvas.create_window(160, 274, anchor="nw", window=label_city)
    canvas.bind("<Button-1>", lambda event: onDetailClick(event, detail_weather_window, cabinet_window))
    custom_image_path = weather_icons[weather_description]
    custom_image = Image.open(custom_image_path)
    resized_custom_image = custom_image.resize((180, 165))
    custom_photo = ImageTk.PhotoImage(resized_custom_image)
    label_custom_image = ctk.CTkLabel(detail_weather_window, text=" ", image=custom_photo)
    canvas.create_window(17,6, anchor="nw", window=label_custom_image)
    button_image = ctk.CTkButton(detail_weather_window,text="", image=ImageTk.PhotoImage(Image.open("icon/captcha_6741193.png").resize((25,25))),  bg_color="#56A7B0", fg_color="#56A7B0", width=25, height=25, command= lambda: refresh_weather(city, detail_weather_window, cabinet_window))
    canvas.create_window(300, 20, anchor="nw", window=button_image)
  

def onDetailClick(event, detail_weather_window, cabinet_window):
    on_open_widget(city, cabinet_window)
    detail_weather_window.destroy()
def open_cabinet(country, city, firstname, lastname):
    cabinet_window = ctk.CTkToplevel()
    cabinet_window.title("Особистий кабінет")
    cabinet_window.geometry("440x555")
    cabinet_window.configure(fg_color="#56A7B0")
    cabinet_window.overrideredirect(True)
    custom_image_path = "icon/left-arrow_10559390.png"
    custom_image = Image.open(custom_image_path)
    resized_custom_image = custom_image.resize((28, 29))
    custom_photo = ImageTk.PhotoImage(resized_custom_image)
    
    label_custom_image = ctk.CTkLabel(cabinet_window, text=" ", image=custom_photo)
    label_custom_image.pack(padx = (409, 0), pady = (20, 0), anchor="nw")
    close_button = ctk.CTkButton(cabinet_window, text="Вихід", command=close_window, font=("Courier New", 12), fg_color="#56A7B0", corner_radius=20, border_color="#56A7B0", border_width=3, height=12, width=12)
    close_button.place(x=370, y=22)
    label_widget_title = ctk.CTkLabel(cabinet_window, text="Особистий кабінет", text_color="#FFFFFF", font=("Courier New", 28, "bold"), fg_color="#56A7B0")
    label_widget_title.pack(anchor="center", padx=(30, 0), pady=(20, 0))
    show_user_info("Країна",country, cabinet_window)
    show_user_info("Місто",city, cabinet_window)
    show_user_info("Ім'я",firstname, cabinet_window)
    show_user_info("Прізвище",lastname, cabinet_window)
    button_open_new_window = ctk.CTkButton(cabinet_window, text="Перейти до додатку", command=lambda: on_open_widget(city, cabinet_window), fg_color="#096C82", corner_radius=20, border_color="#A8CCD3", border_width=3, height=36, width=150)
    button_open_new_window.pack(pady=10)

def showuserinfo(userInfo):
    root.withdraw()
    open_cabinet(userInfo[1], userInfo[2], userInfo[3], userInfo[4])

def open_widget(city, cabinet_window):
    widget_window = ctk.CTkToplevel()
    widget_window.title("Widget")
    widget_window.geometry("1200x800")
    widget_window.configure(fg_color="#56A7B0")
    widget_window.overrideredirect(True)

    canvas = ctk.CTkCanvas(widget_window, width=1200, height=800)
    canvas.pack()

    canvas.create_rectangle(0, 0, 275, 800, fill="#096C82", outline="#096C82")
    canvas.create_rectangle(275, 0, 1200, 800, fill="#56A7B0", outline="#56A7B0")
    entry_city_name = ctk.CTkEntry(canvas, fg_color="#096C82", placeholder_text="ПОШУК", placeholder_text_color="#56A7B0", bg_color="#56A7B0", corner_radius=20, border_color="#A8CCD3", border_width=3, height=46, width=218)
    canvas.create_window(918, 42, anchor="nw", window=entry_city_name)
    entry_city_name.bind('<KeyPress-Return>', lambda event: weather(canvas, widget_window,entry_city_name.get()))
    
    
    country, city, firstname, lastname = get_user_info()
    
    user_button = ctk.CTkButton(canvas, text=firstname + " " + lastname, bg_color="#56A7B0", fg_color="#56A7B0", font=("Courier New", 20, "bold"), command=lambda: (open_cabinet(country, city, firstname, lastname), widget_window.destroy()), width=282, height=40)
    canvas.create_window(282, 50, anchor="nw", window=user_button)

    mini_button = ctk.CTkButton(canvas, text="Mini", bg_color="#56A7B0", fg_color="#56A7B0", font=("Courier New", 20, "bold"), command=lambda: detail_weather_window(city, cabinet_window, widget_window), width=100, height=40)
    canvas.create_window(660, 50, anchor="nw", window=mini_button)
    frame = ctk.CTkFrame(widget_window, fg_color="#56A7B0", corner_radius= 20, border_color="white", border_width=5, height=240, width=818)
    canvas.create_window(332, 440, anchor="nw", window=frame)
    button_left = ctk.CTkButton(widget_window, text="<", bg_color="#56A7B0", width=47, height=50, fg_color="#56A7B0", text_color="#FFFFFF", font=("Courier New", 50, "bold"), command= lambda: left_arrow(canvas, widget_window))
    canvas.create_window(285, 532, anchor="nw", window=button_left)
    button_right = ctk.CTkButton(widget_window, text=">", bg_color="#56A7B0", width=47, height=50, fg_color="#56A7B0", text_color="#FFFFFF", font=("Courier New", 50, "bold"), command= lambda: right_arrow(canvas, widget_window))
    canvas.create_window(1150, 532, anchor="nw", window=button_right)

    button_image = ctk.CTkButton(widget_window,text="", image=ImageTk.PhotoImage(Image.open("icon/close_button.png").resize((48,50))),  bg_color="#56A7B0", fg_color="#56A7B0", width=48, height=50, command= close_window)
    canvas.create_window(1135, 5, anchor="nw", window=button_image)
    weather(canvas, widget_window, city)
    
    custom_image_path = "icon/user_9970571.png"
    custom_image = Image.open(custom_image_path)
    resized_custom_image = custom_image.resize((48, 50))
    custom_photo = ImageTk.PhotoImage(resized_custom_image)
    label_custom_image = ctk.CTkLabel(widget_window, text=" ", image=custom_photo)
    canvas.create_window(300, 43, anchor="nw", window=label_custom_image)
    weather(canvas, widget_window, city)
    
    for i in range(0,len(cities)):
        create_city_button(canvas,widget_window,i)

def create_city_button(canvas,widget_window,idx):
    (temperature, weather_description,timezoneoffset)  = get_weather(api_key, cities[idx])
    button = ctk.CTkButton(canvas, text="", bg_color="#096C82", font=("Courier New", 20, "bold"), command=lambda:  weather(canvas, widget_window, cities[idx]), fg_color="#096C82", corner_radius=20, border_color="#A8CCD3", border_width=2, height=101, width=236)
    canvas.create_window(19, idx*128+31, anchor="nw", window=button)
    label_city = ctk.CTkLabel(canvas, text=cities[idx],font=("Courier New", 20, "bold"), fg_color="#096C82", text_color="#FFFFFF")
    canvas.create_window(35, idx*128+43, anchor="nw", window=label_city)
    label_temp = ctk.CTkLabel(canvas, text=str(temperature)+"°",font=("Inter", 50, "bold"), fg_color="#096C82", text_color="#FFFFFF")
    canvas.create_window(250, idx*128+40, anchor="ne", window=label_temp)
    label_desc = ctk.CTkLabel(canvas, text=weather_description,font=("Courier New", 12, "bold"), bg_color="#096C82", fg_color="#096C82", text_color="#56A7B0")
    canvas.create_window(35, idx*128+100, anchor="nw", window=label_desc)
    timezone_offset = timedelta(hours=int(timezoneoffset)/3600)
    current_utc_time = datetime.utcnow()
    current_time_with_offset = current_utc_time + timezone_offset
    formatted_datetime = current_time_with_offset.strftime("%H:%M")
    label_time = ctk.CTkLabel(canvas, text=formatted_datetime,font=("Courier New", 12, "bold"), bg_color="#096C82", fg_color="#096C82", text_color="#FFFFFF")
    canvas.create_window(35, idx*128+65, anchor="nw", window=label_time)
def show_user_info(textLabel,textValue, cabinet_window):
    label_country_info = ctk.CTkLabel(cabinet_window, text=textLabel, fg_color="#56A7B0", text_color="#FFFFFF", font=("Courier New", 22, "bold"))
    label_country_info.pack(anchor="w", pady=(11, 0), padx=(46, 0))
    label_country_value = ctk.CTkLabel(cabinet_window, text=f"{textValue}", fg_color="#56A7B0", text_color="#FFFFFF", font=("Courier New", 28, "underline", "bold"))
    label_country_value.pack(anchor="w", pady=(0, 11), padx=(121, 0))
def left_arrow(canvas, widget_window):
    forecast = get_forecast(api_key, city)
    #if forecast_idx > len(forecast):
    global forecast_idx
    forecast_idx -= 1
    show_forecast(forecast,canvas, widget_window)
def right_arrow(canvas, widget_window):
    forecast = get_forecast(api_key, city)
    #if forecast_idx > 0:
    global forecast_idx
    forecast_idx += 1
    show_forecast(forecast,canvas, widget_window)
def weather(canvas, widget_window, city):
    temperature, weather_description,timezoneoffset  = get_weather(api_key, city)    
    label_widget = ctk.CTkLabel(
        canvas,
        text=f"Поточна позиція\n{city}\n{temperature}°\n{weather_description}",
        font=("Courier New", 28, "bold"),
        text_color="#FFFFFF",
        fg_color="#56A7B0"
    )
    canvas.create_window(576, 140, anchor="nw", window=label_widget) 
    timezone_offset = timedelta(hours=int(timezoneoffset)/3600)
    current_utc_time = datetime.utcnow()
    current_time_with_offset = current_utc_time + timezone_offset    
    formatted_datetime = current_time_with_offset.strftime("%A\n %d.%m.%Y\n %H:%M")  
    label_time = ctk.CTkLabel(canvas, text=formatted_datetime, font=("Courier New", 28, "bold"), text_color="#FFFFFF", fg_color="#56A7B0")
    canvas.create_window(936, 191, anchor="nw", window=label_time)
    custom_image_path = weather_icons[weather_description]
    custom_image = Image.open(custom_image_path)
    resized_custom_image = custom_image.resize((171, 159))
    custom_photo = ImageTk.PhotoImage(resized_custom_image)  
    label_custom_image = ctk.CTkLabel(widget_window, text=" ", image=custom_photo)
    canvas.create_window(360, 171, anchor="nw", window=label_custom_image)   
    show_forecast(get_forecast(api_key, city),canvas, widget_window)

def show_forecast(forecast,canvas, widget_window):
        # ищем индекс с которого будем выводить прогноз
        global forecast_idx
#        for fk in forecast:
#            formatted_datetime = datetime.strptime(fk.date,"%Y-%m-%d %H:%M:%S")
#            if formatted_datetime>=datetime.now():
#                break
#            forecast_idx+=1
#        if (forecast_idx+8)>len(forecast):
#            forecast_idx -= 8
        for i in range(0,8):
            show_one_forecast(i,forecast,canvas, forecast_idx, widget_window)

def show_one_forecast(i,forecast, canvas, idx, widget_window):
        x = i*97+370
        dt = datetime.strptime(forecast[idx+i].date ,'%Y-%m-%d %H:%M:%S').strftime('%H:%M')
        label = ctk.CTkLabel(widget_window, text= f"{dt}",fg_color="#56A7B0", bg_color="#56A7B0", font=("Courier New", 22, "bold"), text_color= "white")
        canvas.create_window(x, 484, anchor="nw", window=label)
        label2 = ctk.CTkLabel(widget_window, text= f"{forecast[idx+i].temp}°",fg_color="#56A7B0", bg_color="#56A7B0", font=("Courier New", 28, "bold"), text_color= "white")
        canvas.create_window(x, 614, anchor="nw", window=label2)

        custom_image_path = weather_icons[forecast[idx+i].description]
        custom_image = Image.open(custom_image_path)
        resized_custom_image = custom_image.resize((58, 60))
        custom_photo = ImageTk.PhotoImage(resized_custom_image)

        label_custom_image = ctk.CTkLabel(widget_window, text=" ", image=custom_photo)
        canvas.create_window(x, 534, anchor="nw", window=label_custom_image)





def on_open_widget(city, cabinet_window):
    cabinet_window.destroy()
    open_widget(city, cabinet_window)
    

def close_window():
    exit()


def create_user_info(text, registration_window):
    label = ctk.CTkLabel(registration_window, text="Країна:", fg_color="#56A7B0", text_color="#FFFFFF", font=("Courier New", 22, "bold"))
    label.pack(anchor="w", pady=(11, 0), padx=(46, 0))

    entry = ctk.CTkEntry(registration_window, fg_color="#096C82", corner_radius=20, border_color="#A8CCD3", border_width=3, height=36, width=175)
    entry.pack(anchor="w", pady=(0, 11), padx=(46, 0))
    return entry


def open_registration_window():
    root.withdraw()
    registration_window = ctk.CTkToplevel()
    registration_window.geometry("440x555")
    registration_window.configure(fg_color="#56A7B0")
    registration_window.overrideredirect(True)

    label_title = ctk.CTkLabel(registration_window, text="Реєстрація користувача", font=("Courier New", 28, "bold"), fg_color="#56A7B0", text_color="#FFFFFF")
    label_title.pack(anchor="w", padx=(38, 0), pady=(42, 0))

    #label_country = ctk.CTkLabel(registration_window, text="Країна:", fg_color="#56A7B0", text_color="#FFFFFF", font=("Courier New", 22, "bold"))
    #label_country.pack(anchor="w", pady=(11, 0), padx=(46, 0))

    #entry_country = ctk.CTkEntry(registration_window, fg_color="#096C82", corner_radius=20, border_color="#A8CCD3", border_width=3, height=36, width=175)
    #entry_country.pack(anchor="w", pady=(0, 11), padx=(46, 0))

    entry_country = create_user_info("Країна", registration_window)

    label_city = ctk.CTkLabel(registration_window, text="Місто:", fg_color="#56A7B0", text_color="#FFFFFF", font=("Courier New", 22, "bold"))
    label_city.pack(anchor="w", pady=(11, 0), padx=(46, 0))

    entry_city = ctk.CTkEntry(registration_window, fg_color="#096C82", corner_radius=20, border_color="#A8CCD3", border_width=3, height=36, width=175)
    entry_city.pack(anchor="w", pady=(0, 11), padx=(46, 0))

    label_firstname = ctk.CTkLabel(registration_window, text="Ім'я:", fg_color="#56A7B0", text_color="#FFFFFF", font=("Courier New", 22, "bold"))
    label_firstname.pack(anchor="w", pady=(11, 0), padx=(46, 0))

    entry_firstname = ctk.CTkEntry(registration_window, fg_color="#096C82", corner_radius=20, border_color="#A8CCD3", border_width=3, height=36, width=175)
    entry_firstname.pack(anchor="w", pady=(0, 11), padx=(46, 0))

    label_lastname = ctk.CTkLabel(registration_window, text="Прізвище:", fg_color="#56A7B0", text_color="#FFFFFF", font=("Courier New", 22, "bold"))
    label_lastname.pack(anchor="w", pady=(11, 0), padx=(46, 0))

    entry_lastname = ctk.CTkEntry(registration_window, fg_color="#096C82", corner_radius=20, border_color="#A8CCD3", border_width=3, height=36, width=175)
    entry_lastname.pack(anchor="w", pady=(0, 11), padx=(46, 0))

    button_submit = ctk.CTkButton(registration_window, text="Зберегти", command=lambda: submit(entry_country, entry_city, entry_firstname, entry_lastname, registration_window), fg_color="#096C82", corner_radius=20, border_color="#A8CCD3", border_width=3, height=36, width=150)
    button_submit.pack(pady=25)

def get_user_info():
    existing_user = check_registration()
    return existing_user[1], existing_user[2], existing_user[3], existing_user[4]    

def check_registration():
    connection = sqlite3.connect("registration_data.db")
    cursor = connection.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS registration (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      country TEXT,
                      city TEXT,
                      firstname TEXT,
                      lastname TEXT)''')

    cursor.execute("SELECT * FROM registration")
    existing_user = cursor.fetchone()

    connection.close()

    return existing_user

root = ctk.CTk()
existing_user = check_registration()

if existing_user:
    root.withdraw()
    showuserinfo(existing_user)
else:
    root.deiconify()    
    root.title("Головне вікно")
    root.geometry("200x200")
    root.configure(fg_color="#56A7B0", corner_radius=20)
    root.overrideredirect(True)

    label_title = ctk.CTkLabel(root, text="Головне вікно", text_color="#FFFFFF", font=("Courier New", 20, "bold"))
    label_title.pack(pady=5)

    button_register = ctk.CTkButton(root, text="Зареєструватися", command=lambda: open_registration_window(), fg_color="#096C82", corner_radius=20, border_color="#A8CCD3", border_width=3, height=36, width=150)
    button_register.pack(pady=40)
root.mainloop()