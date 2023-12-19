## ![bicicleta](https://github.com/tuskjant/bici_bcn_status/blob/main/images/bicicleta.png?raw=true)   Bici bcn Status

### About
Bici bcn status 
It's a simple gui app made in python with the aim of practicing code 
programming.
The app shows you a map and gives you instructions about how to get to 
bicing stations from the direction you give. You can look for empty slots, 
bikes or ebikes and it returns the nearest stations sorted by walking distance prioritizing 
those with more than 1 slot or bike.


This app uses two apis: 
+ **Citibikes API** for bike data collection. https://api.citybik.es/v2/
+ **Cartociudad API** for geocoding and routing https://www.cartociudad.es/web/portal/directorio-de-servicios/geoprocesamiento

It uses tkinter, customtkinter and tkintermapview for visualization.
### Demo


https://github.com/tuskjant/bici_bcn_status/assets/151870795/61597beb-cd87-41dd-aafa-1af967d3be35



### Usage
+ 1. Enter a direction *(street, number)* in Barcelona
+ 2. Select if you want to see empty slots, ebikes or bikes
+ 3. The map shows directions and instructions to get to nearest options

### Credits
+ Use of Cartociudad API for geocoding and routing https://www.cartociudad.es/web/portal/directorio-de-servicios/geoprocesamiento
+ Use of CityBikes API for bike data collection https://api.citybik.es/v2/\n\n"\
+ Icons from https://www.flaticon.es:
  +  Ciclismo iconos creados por Stockio
  +  Ciclismo iconos creados por Dragon Icons
  +  Marcador iconos creados por mavadee
### License
GNU Lesser General Public License v3.0
