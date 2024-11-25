from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Load the data
pincode_data = pd.read_csv('Pincodes List.csv')  # Ensure this file exists in your project folder
rates_data = pd.read_excel('Go Fast Logistics Commercial.xlsx')  # Ensure this file exists in your project folder

@app.route('/')
def home():
    return "GoFastLogistics API is working!"

@app.route('/check_rates', methods=['POST'])
def check_rates():
    try:
        data = request.json
        origin_pincode = data.get('origin_pincode')
        destination_pincode = data.get('destination_pincode')
        service_type = data.get('service_type')

        # Validate inputs
        if not origin_pincode or not destination_pincode or not service_type:
            return jsonify({"error": "Invalid input, all fields are required"}), 400

        # Find origin and destination details
        origin = pincode_data[pincode_data['Pincode'] == int(origin_pincode)]
        destination = pincode_data[pincode_data['Pincode'] == int(destination_pincode)]

        if origin.empty or destination.empty:
            return jsonify({"error": "No service available for the entered pincodes"}), 404

        # Extract relevant details from the DataFrame rows
        origin_city = origin.iloc[0]['City']
        destination_city = destination.iloc[0]['City']
        origin_state = origin.iloc[0]['State']
        destination_state = destination.iloc[0]['State']
        origin_zone = origin.iloc[0]['Zone']
        destination_zone = destination.iloc[0]['Zone']

        # Determine the Zone
        if origin_city == destination_city:
            zone = "Zone A"
        elif origin_state == destination_state:
            zone = "Zone B"
        elif origin_zone == destination_zone:
            zone = "Zone C"
        elif origin_city in ['Delhi', 'Mumbai', 'Bangalore', 'Chennai'] and destination_city in ['Delhi', 'Mumbai', 'Bangalore', 'Chennai']:
            zone = "Zone D"
        elif origin_state in ['Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Sikkim', 'Arunachal Pradesh', 'Assam', 'Jammu and Kashmir', 'Andaman and Nicobar'] or \
                destination_state in ['Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Sikkim', 'Arunachal Pradesh', 'Assam', 'Jammu and Kashmir', 'Andaman and Nicobar']:
            zone = "Zone F"
        else:
            zone = "Zone E"

        # Get the rate from rates_data
        rate_row = rates_data[(rates_data['Zone'] == zone) & (rates_data['Service'] == service_type)]
        if rate_row.empty:
            return jsonify({"error": f"No rates available for Zone {zone} and service type {service_type}"}), 404

        rate = rate_row.iloc[0]['Rate']

        # Return the response
        return jsonify({
            "origin_city": origin_city,
            "destination_city": destination_city,
            "zone": zone,
            "rate": rate
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Render sets the PORT variable
    app.run(host='0.0.0.0', port=port, debug=True)
