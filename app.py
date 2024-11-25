from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Load the data
pincode_file = "Pincodes List.csv"
pricing_file = "Go Fast Logistics Commercial.xlsx"

pincode_data = pd.read_csv(pincode_file)
pricing_data = pd.read_excel(pricing_file, sheet_name=None)  # Load all sheets (Surface, Air, Premium)

# Logic for determining the zone based on the given pincode data
def determine_zone(origin_row, destination_row):
    origin_city = origin_row['City']
    origin_state = origin_row['State']
    destination_city = destination_row['City']
    destination_state = destination_row['State']
    origin_zone = origin_row['Zone']
    destination_zone = destination_row['Zone']
    
    # Zone A: Within City
    if origin_city == destination_city:
        return "Zone A"
    
    # Zone B: Within State
    elif origin_state == destination_state:
        return "Zone B"
    
    # Zone C: Regional (same zone in pincode list)
    elif origin_zone == destination_zone:
        return "Zone C"
    
    # Zone D: Metro to Metro
    elif (origin_city in ["Mumbai", "Delhi", "Bangalore", "Chennai"] and
          destination_city in ["Mumbai", "Delhi", "Bangalore", "Chennai"]):
        return "Zone D"
    
    # Zone F: Special States
    elif origin_state in ["Jammu & Kashmir", "Assam", "Meghalaya", "Manipur", "Nagaland", "Sikkim", 
                          "Mizoram", "Arunachal Pradesh", "Andaman & Nicobar"] or \
         destination_state in ["Jammu & Kashmir", "Assam", "Meghalaya", "Manipur", "Nagaland", "Sikkim", 
                               "Mizoram", "Arunachal Pradesh", "Andaman & Nicobar"]:
        return "Zone F"
    
    # Zone E: Rest of India
    else:
        return "Zone E"

# API endpoint for checking rates
@app.route('/check_rates', methods=['POST'])
def check_rates():
    data = request.get_json()
    
    # Validate input
    if not data or not all(k in data for k in ("origin_pincode", "destination_pincode", "service_type")):
        return jsonify({"error": "Invalid input. Required fields: origin_pincode, destination_pincode, service_type"}), 400
    
    origin_pincode = str(data['origin_pincode'])
    destination_pincode = str(data['destination_pincode'])
    service_type = data['service_type']
    
    # Validate service type
    if service_type not in pricing_data.keys():
        return jsonify({"error": "Invalid service type. Allowed values are: Surface, Air, Premium"}), 400

    # Find origin and destination rows
    origin_row = pincode_data[pincode_data['Pincode'] == int(origin_pincode)]
    destination_row = pincode_data[pincode_data['Pincode'] == int(destination_pincode)]
    
    if origin_row.empty or destination_row.empty:
        return jsonify({"error": "Invalid pincode(s). Pincode(s) not found in database."}), 400
    
    origin_row = origin_row.iloc[0]
    destination_row = destination_row.iloc[0]
    
    # Determine the zone
    zone = determine_zone(origin_row, destination_row)
    
    # Fetch rate from pricing data
    pricing_sheet = pricing_data[service_type]
    rate_row = pricing_sheet[pricing_sheet['Zone'] == zone]
    
    if rate_row.empty:
        return jsonify({"error": f"No rate found for Zone {zone} in service type {service_type}"}), 404
    
    rate = rate_row['Rate'].values[0]
    
    return jsonify({
        "origin_city": origin_row['City'],
        "destination_city": destination_row['City'],
        "zone": zone,
        "rate": rate
    })

# Entry point for running the app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Render sets the PORT variable
    app.run(host='0.0.0.0', port=port, debug=True)
