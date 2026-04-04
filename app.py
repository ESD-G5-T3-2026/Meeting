
import os 
from flasgger import Swagger
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from supabase import create_client

load_dotenv() 
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
port = os.environ.get("PORT")
supabase = create_client(url, key)

app = Flask(__name__)
swagger = Swagger(app)


@app.route('/health')
def check():
    """
    Health Check
    ---
    responses:
      200:
        description: Server is working
        schema:
          type: string
    """
    return 'Server is working'


@app.route('/meetings/pending', methods=['GET'])
def get_all_pending_meetings():
    """
    personnel_list and timeful_link for meetings with status Pending (any club)
    ---
    responses:
      200:
        description: One object per pending meeting with personnel_list and timeful_link only
        schema:
          type: object
          properties:
            status:
              type: string
            data:
              type: array
              items:
                type: object
                properties:
                  personnel_list:
                    type: object
                  timeful_link:
                    type: string
      500:
        description: Internal server error
    """
    try:
        result = (
            supabase.table("meetings")
            .select("personnel_list,timeful_link")
            .eq("status", "Pending")
            .execute()
        )
        return jsonify({"status": "ok", "data": result.data or []}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/<club_id>', methods=['GET'])
def get_all_meetings_by_club(club_id):
    """
    Get all meetings for a club
    ---
    parameters:
      - name: club_id
        in: path
        type: integer
        required: true
        description: ID of the club
      - name: status
        in: query
        type: string
        required: false
        description: Filter by meeting status (e.g. Pending)
    responses:
      200:
        description: Returns a list of meetings for the club
        schema:
          type: object
          properties:
            status:
              type: string
            data:
              type: array
              items:
                type: object
      500:
        description: Internal server error
    """
    try:
        q = supabase.table("meetings").select("*").eq("club_id", club_id)
        status_filter = request.args.get("status")
        if status_filter is not None and status_filter != "":
            q = q.eq("status", status_filter)
        result = q.execute()
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
    """
    Create a meeting for a club
    ---
    parameters:
      - name: club_id
        in: path
        type: integer
        required: true
        description: ID of the club
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            meeting_dt:
              type: string
              description: Meeting date/time (optional)
            timeful_link:
              type: string
            zoom_link:
              type: string
            event_id:
              type: integer
            personnel_list:
              type: object
            status:
              type: string
              description: Stored on the row; defaults to Planned if omitted
    responses:
      201:
        description: Meeting created successfully
        schema:
          type: object
          properties:
            status:
              type: string
            data:
              type: object
      500:
        description: Internal server error
    """
    data = request.get_json() or {}
    try:
        insert_data = {
            "timeful_link": data.get("timeful_link", ""),
            "zoom_link": data.get("zoom_link", ""),
            "club_id": club_id,
            "event_id": data.get("event_id", None),
            "meeting_dt": data.get("meeting_dt"),
            "personnel_list": data.get("personnel_list", {}),
            "status": data.get("status", "Planned"),
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
    """
    Update a meeting
    ---
    parameters:
      - name: club_id
        in: path
        type: integer
        required: true
        description: ID of the club
      - name: meeting_id
        in: path
        type: integer
        required: true
        description: ID of the meeting
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            timeful_link:
              type: string
            zoom_link:
              type: string
            event_id:
              type: integer
            meeting_dt:
              type: string
            personnel_list:
              type: object
            status:
              type: string
    responses:
      200:
        description: Meeting updated successfully
        schema:
          type: object
          properties:
            status:
              type: string
            data:
              type: object
      400:
        description: No valid fields to update
      500:
        description: Internal server error
    """
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
    """
    Delete a meeting
    ---
    parameters:
      - name: club_id
        in: path
        type: integer
        required: true
        description: ID of the club
      - name: meeting_id
        in: path
        type: integer
        required: true
        description: ID of the meeting
    responses:
      200:
        description: Meeting deleted successfully
        schema:
          type: object
          properties:
            status:
              type: string
            message:
              type: string
            data:
              type: object
      404:
        description: Meeting not found
      500:
        description: Internal server error
    """
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