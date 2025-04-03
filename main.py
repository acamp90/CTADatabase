#
# header comment! Overview, name, etc.
# Project Name: Project 1 - CTA Database App
# Author: Alberto Campuzano
# Last Modified : September 18, 2024
#
# 

import sqlite3
import matplotlib.pyplot as plt


##################################################################  
#
# print_stats
#
# Given a connection to the CTA database, executes various
# SQL queries to retrieve and output basic stats.
#
def print_stats(dbConn):
    dbCursor = dbConn.cursor()
    
    print("General Statistics:")
    
    dbCursor.execute("Select count(*) From Stations;")
    row = dbCursor.fetchone();
    print("  # of stations:", f"{row[0]:,}")
    
    dbCursor.execute("Select count(*) From Stops;")
    row = dbCursor.fetchone()
    print("  # of stops:", f"{row[0]:,}")

    dbCursor.execute("Select count(*) From Ridership;")
    row = dbCursor.fetchone()
    print("  # of ride entries:", f"{row[0]:,}")

    dbCursor.execute("Select min(date(Ride_Date)), max(date(Ride_Date)) From Ridership;")
    min_date, max_date = dbCursor.fetchone()
    print("  date range:", f"{min_date} - {max_date}")

    dbCursor.execute("Select sum(Num_Riders) From Ridership;")
    row = dbCursor.fetchone()
    print("  Total ridership:", f"{row[0]:,}")

    print("")

##################################################################  
#
# find_station_name
#
# Given a connection to the CTA database, execute a
# SQL querie to retrieve and output station names.
#
def find_station_name(dbConn):
    partial_name = input("Enter partial station name (wildcards _ and %): ")
    dbCursor = dbConn.cursor()

    sql = """
    SELECT Station_ID, Station_Name
    FROM Stations
    WHERE Station_Name LIKE ?
    ORDER BY Station_Name ASC;
    """

    # Using upper() for case-insensitive search
    dbCursor.execute(sql, [partial_name.upper()])

    result = dbCursor.fetchall()
    if result:
        for row in result:
            print(f"{row[0]} : {row[1]}")
            
    else:
        print("**No stations found...")

##################################################################  
#
# stat_ridership
#
# Given a connection to the CTA database, execute a
# SQL querie to retrieve and output station percentage of riders on type of day.
#
def stat_ridership(dbConn):
    station_name = input("Enter the name of the station you would like to analyze: ")
    dbCursor = dbConn.cursor()

    sql = """
    SELECT Type_of_Day, SUM(Num_Riders)
    FROM Ridership
    JOIN Stations ON Ridership.Station_ID = Stations.Station_ID
    WHERE Station_Name = ?
    GROUP BY Type_of_Day;
    """

    dbCursor.execute(sql, [station_name])
    results = dbCursor.fetchall()

    if results:
        # Initialize counts
        weekday_count, saturday_count, sunday_holiday_count = 0, 0, 0

        # Summarize counts for each day type
        for result in results:
            if result[0] == 'W':
                weekday_count = result[1]
            elif result[0] == 'A':
                saturday_count = result[1]
            elif result[0] == 'U':
                sunday_holiday_count = result[1]

        # Total ridership
        total_ridership = weekday_count + saturday_count + sunday_holiday_count

        # Displaying results
        print(f"Percentage of ridership for the {station_name} station:")
        if total_ridership > 0:
            print("  Weekday ridership:", f"{weekday_count:,}", f"({weekday_count / total_ridership * 100:.2f}%)")
            print("  Saturday ridership:", f"{saturday_count:,}", f"({saturday_count / total_ridership * 100:.2f}%)")
            print("  Sunday/holiday ridership:", f"{sunday_holiday_count:,}", f"({sunday_holiday_count / total_ridership * 100:.2f}%)")
            print(f"  Total ridership: {total_ridership:,}")
    else:
        print("**No data found...")

##################################################################  
#
# weekday_stats
#
# Given a connection to the CTA database, execute a
# SQL querie to retrieve and output station names with total ridership on weekdays.
#
def weekday_stats(dbConn):
    dbCursor = dbConn.cursor()

    # Retrieve total weekday ridership for each station
    sql = """
    SELECT Station_Name, SUM(Num_Riders) as Total_Ridership
    FROM Ridership
    JOIN Stations ON Ridership.Station_ID = Stations.Station_ID
    WHERE Type_of_Day = 'W'
    GROUP BY Station_Name
    ORDER BY Total_Ridership DESC;
    """

    dbCursor.execute(sql)
    results = dbCursor.fetchall()

    # Calculate total ridership for all stations
    total_weekday_ridership = sum(row[1] for row in results)

    # Displaying results
    print("Ridership on Weekdays for Each Station")
    for row in results:
        station_name, ridership = row
        percentage = (ridership / total_weekday_ridership) * 100
        print(f"{station_name} : {ridership:,} ({percentage:.2f}%)")

##################################################################  
#
# stops_line
#
# Given a connection to the CTA database,with input of color of line and direction executes various
# SQL queries to retrieve and output station with handicab accessible info and direction.
#
def stops_line(dbConn):
    line_color = input("Enter a line color (e.g. Red or Yellow): ").upper()
    dbCursor = dbConn.cursor()

    # Check if the line color exists
    sql_check_line = """
    SELECT COUNT(*)
    FROM Lines
    WHERE UPPER(Color) = ?;
    """

    dbCursor.execute(sql_check_line, [line_color])
    if dbCursor.fetchone()[0] == 0:
        print("**No such line...")
        return

    direction = input("Enter a direction (N/S/W/E): ").upper()

    sql_check_stops = """
    SELECT Stops.Stop_Name, Stops.Direction, Stops.ADA
    FROM Stops
    JOIN StopDetails ON Stops.Stop_ID = StopDetails.Stop_ID
    JOIN Lines ON StopDetails.Line_ID = Lines.Line_ID
    WHERE UPPER(Lines.Color) = ? AND UPPER(Stops.Direction) = ?
    ORDER BY Stops.Stop_Name ASC;
    """

    dbCursor.execute(sql_check_stops, [line_color, direction])
    results = dbCursor.fetchall()

    if not results:
        print("**That line does not run in the direction chosen...")
        return

    for row in results:
        ada = "handicap accessible" if row[2] == 1 else "not handicap accessible"
        print(f"{row[0]} : direction = {row[1]} ({ada})")

##################################################################  
#
# stops_color_direction
#
# Given a connection to the CTA database,with execute
# SQL querie to retrieve and output station with color line info, direction, and # of stops.
#
def stops_color_direction(dbConn):
    dbCursor = dbConn.cursor()

    # Retrieve counts of stops for each line color and direction
    sql = """
    SELECT Lines.Color, Stops.Direction, COUNT(*) as Stop_Count
    FROM Stops
    JOIN StopDetails ON Stops.Stop_ID = StopDetails.Stop_ID
    JOIN Lines ON StopDetails.Line_ID = Lines.Line_ID
    GROUP BY Lines.Color, Stops.Direction
    ORDER BY Lines.Color ASC, Stops.Direction ASC;
    """

    dbCursor.execute(sql)
    results = dbCursor.fetchall()

    # Calculate total number of distinct stops
    dbCursor.execute("SELECT COUNT(DISTINCT Stop_ID) FROM Stops;")
    total_stops = dbCursor.fetchone()[0]

    # Displaying results
    print("Number of Stops For Each Color By Direction")
    for row in results:
        color, direction, count = row
        percentage = (count / total_stops) * 100
        print(f"{color} going {direction} : {count} ({percentage:.2f}%)")

##################################################################  
#
# yearly_ridership_station
#
# Given a connection to the CTA database,with execute
# SQL querie to retrieve station name and output station ridership over the years.
#
def yearly_ridership_station(dbConn):
    station_name = input("Enter a station name (wildcards _ and %): ")
    dbCursor = dbConn.cursor()

    # Check for matching stations
    sql_check_station = """
    SELECT DISTINCT Station_Name
    FROM Stations
    WHERE Station_Name LIKE ?
    """

    dbCursor.execute(sql_check_station, [station_name])
    stations = dbCursor.fetchall()

    if len(stations) > 1:
        print("**Multiple stations found...")
        return
    elif len(stations) == 0:
        print("**No station found...")
        return

    # Retrieve total ridership by year for the station
    sql_ridership = """
    SELECT strftime('%Y', Ride_Date) AS Year, SUM(Num_Riders)
    FROM Ridership
    JOIN Stations ON Ridership.Station_ID = Stations.Station_ID
    WHERE Station_Name = ?
    GROUP BY Year
    ORDER BY Year;
    """
    dbCursor.execute(sql_ridership, [stations[0][0]])
    results = dbCursor.fetchall()

    print(f"Yearly Ridership at {stations[0][0]}")
    years = []
    riderships = []
    for year, ridership in results:
        print(f"{year} : {ridership:,}")
        years.append(year)
        riderships.append(ridership)

    # Plotting
    plot_response = input("\nPlot? (y/n) ")
    if plot_response.lower() == 'y':
        plt.figure(figsize=(10, 6))
        plt.plot(years, riderships, marker='o')
        plt.title(f"Yearly Ridership at {stations[0][0]}")
        plt.xlabel("Year")
        plt.ylabel("Ridership")
        plt.grid(True)
        plt.show(block =False)
        plt.pause(0.001)

##################################################################  
#
# monthly_ridership_station
#
# Given a connection to the CTA database,with execute
# SQL querie to retrieve station name and output station ridership by station.
#
def monthly_ridership_station(dbConn):
    print("")
    station_name = input("Enter a station name (wildcards _ and %): ")
    
    dbCursor = dbConn.cursor()

    # Check for matching stations
    sql_check_station = "SELECT DISTINCT Station_Name FROM Stations WHERE Station_Name LIKE ?"
    dbCursor.execute(sql_check_station, [station_name])
    stations = dbCursor.fetchall()

    if len(stations) > 1:
        print("**Multiple stations found...")
        return
    elif len(stations) == 0:
        print("**No station found...")
        return

    year = input("Enter a year: ")

    # Retrieve total ridership by month for the station and year
    sql_ridership = """
    SELECT strftime('%m/%Y', Ride_Date) AS Month, SUM(Num_Riders)
    FROM Ridership
    JOIN Stations ON Ridership.Station_ID = Stations.Station_ID
    WHERE Station_Name = ? AND strftime('%Y', Ride_Date) = ?
    GROUP BY Month
    ORDER BY Month;
    """
    dbCursor.execute(sql_ridership, [stations[0][0], year])
    results = dbCursor.fetchall()

    print(f"Monthly Ridership at {stations[0][0]} for {year}")
    months = []
    riderships = []
    for month, ridership in results:
        print(f"{month} : {ridership:,}")
        months.append(month)
        riderships.append(ridership)

    # Plotting
    plot_response = input("Plot? (y/n) ")
    if plot_response.lower() == 'y':
        plt.figure(figsize=(10, 6))
        plt.bar(months, riderships, color='blue')
        plt.title(f"Monthly Ridership at {stations[0][0]} for {year}")
        plt.xlabel("Month")
        plt.ylabel("Ridership")
        plt.xticks(rotation=45)
        plt.grid(True)
        #plt.show()
        plt.show(block =False)
        plt.pause(0.001)

##################################################################  
#
# compare_daily_ridership
#
# Given a connection to the CTA database,with execute
# SQL querie to retrieve year and stations and output station ridership between each.
#
def compare_daily_ridership(dbConn):
    year = input("Year to compare against? ")
    print("")
    station1 = input("Enter station 1 (wildcards _ and %): ")
    
    dbCursor = dbConn.cursor()

    # Function to get station data
    def get_station_data(station):
        sql_check_station = "SELECT DISTINCT Station_ID, Station_Name FROM Stations WHERE Station_Name LIKE ?"
        dbCursor.execute(sql_check_station, [station])
        stations = dbCursor.fetchall()
        if len(stations) > 1:
            print("**Multiple stations found...")
            return None
        elif len(stations) == 0:
            print("**No station found...")
            return None
        return stations[0]

    # Retrieve station data
    station1_data = get_station_data(station1)
    print("")

    if not station1_data:
        return
    station2 = input("Enter station 2 (wildcards _ and %): ")
    station2_data = get_station_data(station2)
    if not station2_data:
        return

    # Retrieve and display ridership data for both stations
    def display_ridership(station_id, station_name, station_label):
        sql_ridership = """
        SELECT strftime('%Y-%m-%d', Ride_Date), SUM(Num_Riders)
        FROM Ridership
        WHERE Station_ID = ? AND strftime('%Y', Ride_Date) = ?
        GROUP BY Ride_Date
        ORDER BY Ride_Date;
        """
        dbCursor.execute(sql_ridership, [station_id, year])
        results = dbCursor.fetchall()
        print(f"{station_label}: {station_id} {station_name}")
        for date, ridership in results[:5] + results[-5:]:
            print(f"{date} {ridership}")
        return [r[1] for r in results]

    ridership1 = display_ridership(*station1_data, "Station 1")
    ridership2 = display_ridership(*station2_data, "Station 2")

    # Plotting
    plot_response = input("\nPlot? (y/n) ")
    if plot_response.lower() == 'y' and ridership1 and ridership2:
        dates = [r[0] for r in dbCursor.execute(f"SELECT DISTINCT strftime('%Y-%m-%d', Ride_Date) FROM Ridership WHERE strftime('%Y', Ride_Date) = '{year}' ORDER BY Ride_Date;").fetchall()]
        plt.figure(figsize=(10, 6))
        plt.plot(dates, ridership1, label=f"{station1_data[1]}", marker='o')
        plt.plot(dates, ridership2, label=f"{station2_data[1]}", marker='o')
        plt.title(f"Daily Ridership Comparison for {year}")
        plt.xlabel("Date")
        plt.ylabel("Ridership")
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        ##plt.show()
        plt.show(block =False)
        ##plt.savefig('testfile.png')
        plt.pause(0.001)

##################################################################  
#
# find_stations_within_radius
#
# Given a connection to the CTA database,with execute
# SQL querie to retrieve lat and long and create square of area and return station name and coordinates.
#
def find_stations_within_radius(dbConn):
    latitude_input = input("Enter a latitude: ")
    # Convert to float
    latitude = float(latitude_input)
    # Check bounds for latitude 
    if not (40 <= latitude <= 43):
        print("**Latitude entered is out of bounds...")
        return
    longitude_input = input("Enter a longitude: ")
    longitude = float(longitude_input)
    if not (-88 <= longitude <= -87):
        print("**Longitude entered is out of bounds...")
        return
    
    # Calculate the boundaries for a one mile radius
    lat_mile = 1 / 69  # approximately 69 miles per degree of latitude
    long_mile = 1 / 51  # 51 miles per degree of longitude at Chicago's latitude
    lat_min = round(latitude - lat_mile, 3)
    lat_max = round(latitude + lat_mile, 3)
    long_min = round(longitude - long_mile, 3)
    long_max = round(longitude + long_mile, 3)

    # SQL query to find stations within the specified boundaries
    sql = """
    SELECT DISTINCT Stations.Station_Name, Stops.Latitude , Stops.Longitude 
    FROM Stops
    JOIN Stations ON Stops.Station_ID = Stations.Station_ID
    WHERE Stops.Latitude BETWEEN ? AND ? AND Stops.Longitude BETWEEN ? AND ?
    ORDER BY Stations.Station_Name ASC
    """
    dbCursor = dbConn.cursor()
    dbCursor.execute(sql, (lat_min, lat_max, long_min, long_max))
    stations = dbCursor.fetchall()

    if not stations:
        print("**No stations found...")
        return
    print("")
    # Display the list of found stations
    print("List of Stations Within a Mile")
    for station in stations:
        print(f"{station[0]} : ({station[1]}, {station[2]})")
    print("")
    # Optional plotting
    plot_response = input("Plot? (y/n) ")
    if plot_response.lower() == 'y':
        x = [station[2] for station in stations]
        y = [station[1] for station in stations]

        image = plt.imread("chicago.png")
        xydims = [-87.9277, -87.5569, 41.7012, 42.0868] # area covered by
        ##the map:
        plt.imshow(image, extent=xydims)
        plt.title("Stations Near You")

        plt.plot(x, y, 'bo')
        #
        # annotate each (x, y) coordinate with its station name:
        #
        for station in stations:
            plt.annotate(station[0], (station[2], station[1])) 
        plt.xlim([-87.9277, -87.5569])
        plt.ylim([41.7012, 42.0868])
        ##plt.show() 
        plt.savefig('testfile.png') 

#
# main
#
print('** Welcome to CTA L analysis app **')
print()

dbConn = sqlite3.connect('CTA2_L_daily_ridership.db')

print_stats(dbConn)

while True:
        command = input("Please enter a command (1-9, x to exit): ")

        if command == 'x':
            print("")
            break
        elif command == '1':
            print("")
            find_station_name(dbConn)
            print("")
        elif command == '2':
            print("")
            stat_ridership(dbConn)
            print("")
        elif command == '3':
            
            weekday_stats(dbConn)
            print("")
        elif command == '4':
            print("")
            stops_line(dbConn)
            print("")
        elif command == '5':
            
            stops_color_direction(dbConn)
            print("")
        elif command == '6':
            print("")
            yearly_ridership_station(dbConn)
            print("")
        elif command == '7':
            
            monthly_ridership_station(dbConn)
            print("")
        elif command == '8':
            print("")
            compare_daily_ridership(dbConn)
            print("")
        elif command == '9':
            print("")
            find_stations_within_radius(dbConn)
            print("")
        else:
            print("**Error, unknown command, try again...\n")


#
# done
#
