from flask import Flask, request, jsonify
from flask_cors import CORS
import company_sentiment
import redis
import json
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
CORS(app)

r = redis.Redis(host="redis", port=6379, decode_responses=True)

COMPANY_SET_KEY = "tracked_companies"


def refresh_company_data(company_name):
    try:
        result = company_sentiment.company_data(company_name)
        r.setex(company_name, 3600, json.dumps(result))  # TTL = 1 hr
        print(f"✅ Cache refreshed for {company_name}")
    except Exception as e:
        print(f"⚠️ Failed to refresh {company_name}: {e}")


def refresh_all_companies():
    companies = r.smembers(COMPANY_SET_KEY)
    print(f"Refreshing {len(companies)} companies...")
    for company in companies:
        refresh_company_data(company)


scheduler = BackgroundScheduler()
scheduler.add_job(refresh_all_companies, "interval", minutes=30)
scheduler.start()


@app.route("/company-data", methods=["POST"])
def company_data_api():
    try:
        data = request.json
        company_name = data.get("company_name")

        if not company_name:
            return jsonify({"success": False, "error": "Missing company_name"}), 400

        r.sadd(COMPANY_SET_KEY, company_name)
        cached = r.get(company_name)
        if cached:
            return jsonify({"success": True, "data": json.loads(cached)})

        result = company_sentiment.company_data(company_name)
        r.setex(company_name, 3600, json.dumps(result))
        return jsonify({"success": True, "data": result})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/clear-cache", methods=["POST"])
def clear_cache():
    try:
        data = request.json
        company_name = data.get("company_name")

        if not company_name:
            return jsonify({"success": False, "error": "Missing company_name"}), 400

        # Remove cache + tracking
        deleted = r.delete(company_name)
        r.srem(COMPANY_SET_KEY, company_name)

        if deleted:
            return jsonify({"success": True, "message": f"Cache cleared for {company_name}"})
        else:
            return jsonify({"success": False, "message": f"No cache found for {company_name}"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/tracked-companies", methods=["GET"])
def list_tracked_companies():
    companies = list(r.smembers(COMPANY_SET_KEY))
    return jsonify({"tracked_companies": companies})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
