def getYearRangeInput():
    while True:
        try:
            startYear = int(input("Enter start year: ").strip())
            endYear = int(input("Enter end year: ").strip())

            if startYear > endYear:
                print("Start year cannot be greater than end year. Try again.")
                continue

            return startYear, endYear

        except ValueError:
            print("Invalid input. Please enter valid integers for years.")


def getFilterInputs():
    print("""
Select your choice:
1. Filter by Continent
2. Filter by Country
3. Filter by Specific Year
4. Filter by Year Range
5. Show all
6. Exit
""")
    
    choice = input("Enter your choice: ").strip()
    inputs = {"choice": choice}

    if choice == "1":
        # Filter by Continent
        continent = input("Enter Continent name: ").strip()
        inputs["continent"] = continent
        return inputs
    
    elif choice == "2":
        # Filter by Country
        country = input("Enter Country name: ").strip()
        inputs["country"] = country
        return inputs
    
    elif choice == "3":
        # Filter by Specific Year
        year = input("Enter the year: ").strip()
        inputs["year"] = year
        return inputs
    
    elif choice == "4":
        # Filter by Year Range
        startYear, endYear = getYearRangeInput()
        inputs["startYear"] = startYear
        inputs["endYear"] = endYear
        return inputs
    
    elif choice == "5":
        # Show all
        return {"choice": "5"}

    elif choice == "6":
        # Exit
        exit(0)

    else:
        print("Invalid choice. Please select 1-6.")
        return getFilterInputs()