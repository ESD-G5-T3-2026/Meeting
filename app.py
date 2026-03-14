
import os 
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from supabase import create_client

load_dotenv() 
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
port = os.environ.get("PORT")
supabase = create_client(url, key)

app = Flask(__name__)


@app.route('/health')
def check():
    return 'Server is working'

@app.route('/<club_id>', methods=['GET'])
def get_all_meetings_by_club(club_id):
    try:
        result = supabase.table("meetings").select("*").eq("club_id", club_id).execute()
        return jsonify({
            "status": "ok",
            "data": result.data
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500



@app.route('/<club_id>', methods=['POST'])
def post_meeting_to_club(club_id):
    data = request.get_json()
    meeting_dt = data.get("meeting_dt")
    if not meeting_dt or not club_id:
        return jsonify({
            "status": "error",
            "message": "meeting_dt and club_id are required"
        }), 400
    try:
        insert_data = {
            "timeful_link": data.get("timeful_link", ""),
            "zoom_link": data.get("zoom_link", ""),
            "club_id": club_id,
            "event_id": data.get("event_id", ""),
            "meeting_dt": meeting_dt,
            "personnel_list": data.get("personnel_list", {}),
            "status": "Planned"
            # created_at is defaulted by DB
        }
        result = supabase.table("meetings").insert(insert_data).execute()
        return jsonify({
            "status": "ok",
            "data": result.data
        }), 201
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/<club_id>/<meeting_id>', methods=['PUT'])
def update_meeting(club_id, meeting_id):
    data = request.get_json()
    try:
        update_data = {}
        allowed_fields = [
            "timeful_link", "zoom_link", "event_id", "meeting_dt", "personnel_list","status"
        ]
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        if not update_data:
            return jsonify({
                "status": "error",
                "message": "No valid fields to update"
            }), 400
        result = supabase.table("meetings")\
            .update(update_data)\
            .eq("id", meeting_id)\
            .eq("club_id", club_id)\
            .execute()
        return jsonify({
            "status": "ok",
            "data": result.data
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    
@app.route('/<club_id>/<meeting_id>', methods=['DELETE'])
def delete_meeting(club_id, meeting_id):
    try:
        result = supabase.table("meetings")\
            .delete()\
            .eq("id", meeting_id)\
            .eq("club_id", club_id)\
            .execute()
        if result.data:
            return jsonify({
                "status": "ok",
                "message": "Meeting deleted",
                "data": result.data
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Meeting not found"
            }), 404
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500 

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port)