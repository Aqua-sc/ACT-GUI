def format_carbon(grams: float) -> str:   
        if grams < 1000:
            return f"{grams:.2f} g CO2"
        else:
            return f"{(grams/1000):.2f} kg CO2"