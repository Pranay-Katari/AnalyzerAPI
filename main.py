from flask import Flask, request, jsonify
from flask_cors import CORS
import company_sentiment
import asyncio


app = Flask(__name__)
CORS(app)

@app.route("/company-data", methods = ["POST"])
def company_data_api():
    try:
        data = request.json
        company_name = data.get("company_name")
        if not company_name:
            return jsonify({"success": False, "error": "Missing company_name"}), 400
        result = asyncio.run(company_sentiment.company_data(company_name))
        return jsonify({"success":True, "data":result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
