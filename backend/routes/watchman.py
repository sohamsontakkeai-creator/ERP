"""
Watchman Routes Module
API endpoints for watchman operations (gate security)
"""
from flask import Blueprint, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename
from services.watchman_service import WatchmanService
from services.guest_list_service import GuestListService

watchman_bp = Blueprint('watchman', __name__)


@watchman_bp.route('/watchman/pending-pickups', methods=['GET'])
def get_pending_pickups():
    """Get all pending customer pickups waiting for verification"""
    try:
        pickups = WatchmanService.get_pending_pickups()
        return jsonify(pickups), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@watchman_bp.route('/watchman/gate-passes', methods=['GET'])
def get_all_gate_passes():
    """Get all gate passes (completed and pending)"""
    try:
        passes = WatchmanService.get_all_gate_passes()
        return jsonify(passes), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@watchman_bp.route('/watchman/verify/<int:gate_pass_id>', methods=['POST'])
def verify_customer_pickup(gate_pass_id):
    """Verify customer identity and complete pickup or send in.

    Accepts JSON body or multipart/form-data with optional images:
      - sendInPhoto -> file when action == 'send_in'
      - afterLoadingPhoto -> file when action == 'release' (after loading)
    """
    try:
        # Support both JSON and multipart
        if request.content_type and request.content_type.startswith('multipart/form-data'):
            data = request.form.to_dict() or {}
        else:
            data = request.get_json() or {}

        action = data.get('action', 'release')

        # Handle file uploads
        upload_folder = os.path.join(os.getcwd(), 'backend', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)

        saved_files = {}

        # 🆕 Helper: build public URL for uploaded files
        def build_public_url(filename):
            from flask import url_for
            return url_for('uploaded_file', filename=filename, _external=True)

        # send in photo
        if 'sendInPhoto' in request.files:
            f = request.files['sendInPhoto']
            if f and f.filename:
                filename = secure_filename(f.filename)
                filepath = os.path.join(upload_folder, filename)
                f.save(filepath)
                saved_files['send_in_photo'] = filepath
                saved_files['send_in_photo_url'] = build_public_url(filename)  # 🆕 add public URL

        # after loading photo
        if 'afterLoadingPhoto' in request.files:
            f = request.files['afterLoadingPhoto']
            if f and f.filename:
                filename = secure_filename(f.filename)
                filepath = os.path.join(upload_folder, filename)
                f.save(filepath)
                saved_files['after_loading_photo'] = filepath
                saved_files['after_loading_photo_url'] = build_public_url(filename)  # 🆕 add public URL

        # Merge files info into data passed to service
        data.update(saved_files)

        # Pass full data to your WatchmanService
        result = WatchmanService.verify_customer_identity(gate_pass_id, data, action)

        # 🆕 Optional: also return public URLs in the response for frontend convenience
        if 'send_in_photo_url' in saved_files:
            result['send_in_photo_url'] = saved_files['send_in_photo_url']
        if 'after_loading_photo_url' in saved_files:
            result['after_loading_photo_url'] = saved_files['after_loading_photo_url']

        # Handle identity mismatch case
        if result.get('status') == 'identity_mismatch':
            return jsonify(result), 409

        return jsonify(result), 200

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@watchman_bp.route('/watchman/reject/<int:gate_pass_id>', methods=['POST'])
def reject_customer_pickup(gate_pass_id):
    """Reject customer pickup for security reasons"""
    try:
        data = request.get_json() or {}
        rejection_reason = data.get('rejectionReason', 'No reason provided')
        
        result = WatchmanService.reject_pickup(gate_pass_id, rejection_reason)
        return jsonify(result), 200
        
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@watchman_bp.route('/watchman/summary', methods=['GET'])
def get_daily_summary():
    """Get daily summary of watchman activities"""
    try:
        summary = WatchmanService.get_daily_summary()
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@watchman_bp.route('/watchman/search', methods=['GET'])
def search_gate_passes():
    """Search gate passes by customer name, order number, or vehicle number"""
    try:
        search_term = request.args.get('q', '').strip()
        if not search_term:
            return jsonify({'error': 'Search term is required'}), 400
        
        results = WatchmanService.search_gate_pass(search_term)
        return jsonify({
            'searchTerm': search_term,
            'results': results,
            'count': len(results)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Guest List Routes
@watchman_bp.route('/watchman/guests', methods=['GET'])
def get_all_guests():
    """Get all guest entries with optional filters"""
    try:
        filters = {
            'status': request.args.get('status'),
            'startDate': request.args.get('startDate'),
            'endDate': request.args.get('endDate'),
            'search': request.args.get('search')
        }
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        guests = GuestListService.get_all_guests(filters if filters else None)
        return jsonify(guests), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@watchman_bp.route('/watchman/guests/today', methods=['GET'])
def get_todays_guests():
    """Get all guests scheduled for today"""
    try:
        guests = GuestListService.get_todays_guests()
        return jsonify(guests), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@watchman_bp.route('/watchman/guests/summary', methods=['GET'])
def get_guest_summary():
    """Get summary statistics for guest visits"""
    try:
        summary = GuestListService.get_guest_summary()
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@watchman_bp.route('/watchman/guests/<int:guest_id>', methods=['GET'])
def get_guest_by_id(guest_id):
    """Get a specific guest entry by ID"""
    try:
        guest = GuestListService.get_guest_by_id(guest_id)
        return jsonify(guest), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@watchman_bp.route('/watchman/guests', methods=['POST'])
def create_guest():
    """Create a new guest entry"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['guestName', 'meetingPerson', 'visitDate', 'purpose']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        created_by = request.headers.get('X-User-Email', 'security')
        guest = GuestListService.create_guest_entry(data, created_by)
        return jsonify(guest), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@watchman_bp.route('/watchman/guests/<int:guest_id>', methods=['PUT'])
def update_guest(guest_id):
    """Update guest entry details"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        guest = GuestListService.update_guest(guest_id, data)
        return jsonify(guest), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@watchman_bp.route('/watchman/guests/<int:guest_id>/check-in', methods=['POST'])
def check_in_guest(guest_id):
    """Check in a guest (mark arrival)"""
    try:
        data = request.get_json() or {}
        guest = GuestListService.check_in_guest(guest_id, data)
        return jsonify(guest), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@watchman_bp.route('/watchman/guests/<int:guest_id>/check-out', methods=['POST'])
def check_out_guest(guest_id):
    """Check out a guest (mark departure)"""
    try:
        data = request.get_json() or {}
        notes = data.get('notes')
        guest = GuestListService.check_out_guest(guest_id, notes)
        return jsonify(guest), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@watchman_bp.route('/watchman/guests/<int:guest_id>/cancel', methods=['POST'])
def cancel_guest(guest_id):
    """Cancel a guest visit"""
    try:
        data = request.get_json() or {}
        reason = data.get('reason')
        guest = GuestListService.cancel_guest(guest_id, reason)
        return jsonify(guest), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@watchman_bp.route('/watchman/guests/<int:guest_id>', methods=['DELETE'])
def delete_guest(guest_id):
    """Delete a guest entry"""
    try:
        result = GuestListService.delete_guest(guest_id)
        return jsonify(result), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500



# New endpoints: company vehicle returns listing and check-in
@watchman_bp.route('/watchman/company-vehicle-returns', methods=['GET'])
def get_company_vehicle_returns():
    """Return list of company vehicle return notifications for watchman"""
    try:
        # We reuse NotificationService in services.notification_service
        from services.notification_service import NotificationService
        notifs = NotificationService.get_notifications(department='watchman', unread_only=True, limit=50)
        # Filter only company vehicle return type
        returns = [n for n in notifs if n.get('type') == 'company_vehicle_return']
        return jsonify(returns), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@watchman_bp.route('/watchman/company-vehicle-returns/<int:vehicle_id>/check-in', methods=['POST'])
def checkin_company_vehicle(vehicle_id):
    """Watchman checks in the returning company vehicle, set vehicle available."""
    try:
        from services.transport_service import TransportService
        # Mark driver reached which will set vehicle available
        result = TransportService.mark_driver_reached(vehicle_id)

        # Also mark related notifications as read (best-effort)
        from services.notification_service import NotificationService
        # mark any matching notification read
        for n in NotificationService._notifications:
            data = n.get('data') or {}
            if n.get('type') == 'company_vehicle_return' and int(data.get('vehicleId') or 0) == int(vehicle_id):
                n['read'] = True

        return jsonify(result), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
