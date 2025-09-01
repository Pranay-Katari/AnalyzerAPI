from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud import firestore
import company_sentiment
from apscheduler.schedulers.background import BackgroundScheduler
import json
import datetime
import os

app = Flask(__name__)
CORS(app)

db = firestore.Client()

CACHE_COLLECTION = "company_cache"
TRACKED_COLLECTION = "tracked_companies"


def refresh_company_data(company_name):
    try:
        result = company_sentiment.company_data(company_name)
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

        db.collection(CACHE_COLLECTION).document(company_name).set({
            "data": json.dumps(result),
            "expires_at": expires_at
        })
        print(f"✅ Cache refreshed for {company_name}")
    except Exception as e:
        print(f"⚠️ Failed to refresh {company_name}: {e}")


def refresh_all_companies():
    docs = db.collection(TRACKED_COLLECTION).stream()
    companies = [doc.id for doc in docs]
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

        db.collection(TRACKED_COLLECTION).document(company_name).set({"active": True})

        doc = db.collection(CACHE_COLLECTION).document(company_name).get()
        if doc.exists:
            cache_entry = doc.to_dict()
            expires_at = cache_entry.get("expires_at")

            if expires_at and expires_at > datetime.datetime.utcnow():
                return jsonify({"success": True, "data": json.loads(cache_entry["data"])})

        result = company_sentiment.company_data(company_name)
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

        db.collection(CACHE_COLLECTION).document(company_name).set({
            "data": json.dumps(result),
            "expires_at": expires_at
        })

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

        db.collection(CACHE_COLLECTION).document(company_name).delete()
        db.collection(TRACKED_COLLECTION).document(company_name).delete()

        return jsonify({"success": True, "message": f"Cache cleared for {company_name}"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/tracked-companies", methods=["GET"])
def list_tracked_companies():
    docs = db.collection(TRACKED_COLLECTION).stream()
    companies = [doc.id for doc in docs]
    return jsonify({"tracked_companies": companies})



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)